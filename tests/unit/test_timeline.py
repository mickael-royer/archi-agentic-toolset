"""Unit tests for timeline service."""

import pytest
from datetime import datetime, timedelta
from archi_c4_score.timeline import (
    TimelineService,
    CommitComparator,
    TimelinePoint,
    TrendDirection,
)


class TestTimelineService:
    """Tests for TimelineService."""

    def test_calculate_score_delta_with_previous(self):
        """Score delta calculated correctly."""
        service = TimelineService()
        delta, is_significant = service.calculate_score_delta(80.0, 70.0)
        assert delta == 10.0
        assert is_significant is True

    def test_calculate_score_delta_first_commit(self):
        """First commit has no delta."""
        service = TimelineService()
        delta, is_significant = service.calculate_score_delta(80.0, None)
        assert delta is None
        assert is_significant is False

    def test_calculate_score_delta_insignificant_change(self):
        """Small changes are not significant."""
        service = TimelineService(delta_threshold=10.0)
        delta, is_significant = service.calculate_score_delta(75.0, 73.0)
        assert delta == 2.0
        assert is_significant is False

    def test_get_timeline_empty(self):
        """Empty commits returns empty timeline."""
        service = TimelineService()
        timeline = service.get_timeline("https://github.com/test/repo", [])
        assert len(timeline.commits) == 0
        assert timeline.repository_url == "https://github.com/test/repo"

    def test_get_timeline_with_commits(self):
        """Timeline generated from scored commits."""
        service = TimelineService()
        commits = [
            {
                "commit_sha": "abc123",
                "commit_date": "2024-01-01T00:00:00",
                "author": "Test Author",
                "message": "First commit",
                "composite_score": 70.0,
                "dimensions": {"coupling": 80.0},
                "element_count": 10,
                "relationship_count": 15,
            },
            {
                "commit_sha": "def456",
                "commit_date": "2024-01-02T00:00:00",
                "author": "Test Author",
                "message": "Second commit",
                "composite_score": 80.0,
                "dimensions": {"coupling": 75.0},
                "element_count": 12,
                "relationship_count": 18,
            },
        ]
        timeline = service.get_timeline("https://github.com/test/repo", commits)

        assert len(timeline.commits) == 2
        assert timeline.commits[0].sha == "abc123"
        assert timeline.commits[1].sha == "def456"
        assert timeline.commits[1].score_delta == 10.0
        assert timeline.commits[1].is_significant is True

    def test_get_timeline_pagination(self):
        """Pagination works correctly."""
        service = TimelineService()
        commits = [
            {
                "commit_sha": f"sha{i:03d}",
                "commit_date": f"2024-01-{i + 1:02d}T00:00:00",
                "author": "Test",
                "message": f"Commit {i}",
                "composite_score": 70.0 + i,
                "dimensions": {},
                "element_count": 10,
                "relationship_count": 15,
            }
            for i in range(50)
        ]
        timeline = service.get_timeline(
            "https://github.com/test/repo", commits, limit=10, offset=20
        )

        assert len(timeline.commits) == 10
        assert timeline.pagination["total"] == 50
        assert timeline.pagination["offset"] == 20
        assert timeline.pagination["has_more"] is True

    def test_get_timeline_significant_change_detection(self):
        """Significant changes are flagged."""
        service = TimelineService(delta_threshold=10.0)
        commits = [
            {
                "commit_sha": "abc123",
                "commit_date": "2024-01-01T00:00:00",
                "author": "Test",
                "message": "First",
                "composite_score": 70.0,
                "dimensions": {},
                "element_count": 10,
                "relationship_count": 15,
            },
            {
                "commit_sha": "def456",
                "commit_date": "2024-01-02T00:00:00",
                "author": "Test",
                "message": "Big change",
                "composite_score": 90.0,
                "dimensions": {},
                "element_count": 20,
                "relationship_count": 30,
            },
        ]
        timeline = service.get_timeline("https://github.com/test/repo", commits)

        assert timeline.commits[1].is_significant is True
        assert len(timeline.significant_changes) == 1
        assert timeline.significant_changes[0].direction == "improvement"


class TestTrendCalculation:
    """Tests for trend calculation."""

    def test_calculate_trends_empty(self):
        """No trends with insufficient data."""
        service = TimelineService()
        trends = service.calculate_trends([])
        assert len(trends) == 0

    def test_calculate_trends_single_point(self):
        """No trends with single point."""
        service = TimelineService()
        points = [
            TimelinePoint(
                position=0,
                sha="abc123",
                date=datetime.now(),
                author="Test",
                message="Test",
                composite_score=80.0,
                dimensions={"coupling": 80.0},
                element_count=10,
                relationship_count=15,
            )
        ]
        trends = service.calculate_trends(points)
        assert len(trends) == 0

    def test_calculate_trends_increasing(self):
        """Increasing trend detected."""
        service = TimelineService()
        points = [
            TimelinePoint(
                position=i,
                sha=f"sha{i:03d}",
                date=datetime.now() + timedelta(days=i),
                author="Test",
                message=f"Commit {i}",
                composite_score=60.0 + i * 5,
                dimensions={
                    "coupling": 60.0 + i * 5,
                    "modularity": 70.0,
                    "cohesion": 75.0,
                    "extensibility": 65.0,
                    "maintainability": 72.0,
                },
                element_count=10,
                relationship_count=15,
            )
            for i in range(10)
        ]
        trends = service.calculate_trends(points)

        coupling_trend = next(t for t in trends if t.dimension == "coupling")
        assert coupling_trend.direction == TrendDirection.INCREASING
        assert coupling_trend.slope > 0

    def test_calculate_trends_decreasing(self):
        """Decreasing trend detected."""
        service = TimelineService()
        points = [
            TimelinePoint(
                position=i,
                sha=f"sha{i:03d}",
                date=datetime.now() + timedelta(days=i),
                author="Test",
                message=f"Commit {i}",
                composite_score=100.0 - i * 5,
                dimensions={
                    "coupling": 100.0 - i * 5,
                    "modularity": 70.0,
                    "cohesion": 75.0,
                    "extensibility": 65.0,
                    "maintainability": 72.0,
                },
                element_count=10,
                relationship_count=15,
            )
            for i in range(10)
        ]
        trends = service.calculate_trends(points)

        coupling_trend = next(t for t in trends if t.dimension == "coupling")
        assert coupling_trend.direction == TrendDirection.DECREASING
        assert coupling_trend.slope < 0

    def test_calculate_trends_stable(self):
        """Stable trend with little variance."""
        service = TimelineService()
        points = [
            TimelinePoint(
                position=i,
                sha=f"sha{i:03d}",
                date=datetime.now() + timedelta(days=i),
                author="Test",
                message=f"Commit {i}",
                composite_score=75.0,
                dimensions={
                    "coupling": 75.0,
                    "modularity": 75.0,
                    "cohesion": 75.0,
                    "extensibility": 75.0,
                    "maintainability": 75.0,
                },
                element_count=10,
                relationship_count=15,
            )
            for i in range(10)
        ]
        trends = service.calculate_trends(points)

        for trend in trends:
            assert trend.direction == TrendDirection.STABLE

    def test_linear_regression_confidence(self):
        """R² confidence calculated correctly."""
        service = TimelineService()
        slope, confidence = service._linear_regression(range(5), [10, 20, 30, 40, 50])
        assert slope > 0
        assert confidence > 0.9


class TestCommitComparator:
    """Tests for CommitComparator."""

    def test_compare_identical_commits(self):
        """Identical commits have no diff."""
        comparator = CommitComparator()
        commit = {
            "commit_sha": "abc123",
            "elements": [{"id": "e1", "name": "Element 1"}],
            "relationships": [{"source_id": "e1", "target_id": "e2"}],
            "dimensions": {"coupling": 80.0},
        }

        diff, impacts = comparator.compare(commit, commit)

        assert len(diff.elements_added) == 0
        assert len(diff.elements_removed) == 0
        assert len(diff.relationships_added) == 0
        assert len(diff.relationships_removed) == 0

    def test_compare_added_elements(self):
        """New elements detected."""
        comparator = CommitComparator()
        from_commit = {
            "commit_sha": "abc123",
            "elements": [{"id": "e1", "name": "Element 1"}],
            "relationships": [],
            "dimensions": {"coupling": 80.0},
        }
        to_commit = {
            "commit_sha": "def456",
            "elements": [
                {"id": "e1", "name": "Element 1"},
                {"id": "e2", "name": "Element 2"},
            ],
            "relationships": [],
            "dimensions": {"coupling": 75.0},
        }

        diff, impacts = comparator.compare(from_commit, to_commit)

        assert len(diff.elements_added) == 1
        assert diff.elements_added[0]["id"] == "e2"
        assert len(diff.elements_removed) == 0

    def test_compare_removed_elements(self):
        """Removed elements detected."""
        comparator = CommitComparator()
        from_commit = {
            "commit_sha": "abc123",
            "elements": [{"id": "e1", "name": "Element 1"}, {"id": "e2", "name": "Element 2"}],
            "relationships": [],
            "dimensions": {"coupling": 80.0},
        }
        to_commit = {
            "commit_sha": "def456",
            "elements": [{"id": "e1", "name": "Element 1"}],
            "relationships": [],
            "dimensions": {"coupling": 85.0},
        }

        diff, impacts = comparator.compare(from_commit, to_commit)

        assert len(diff.elements_removed) == 1
        assert diff.elements_removed[0]["id"] == "e2"
        assert len(diff.elements_added) == 0

    def test_compare_added_relationships(self):
        """New relationships detected."""
        comparator = CommitComparator()
        from_commit = {
            "commit_sha": "abc123",
            "elements": [{"id": "e1"}, {"id": "e2"}],
            "relationships": [],
            "dimensions": {"coupling": 70.0},
        }
        to_commit = {
            "commit_sha": "def456",
            "elements": [{"id": "e1"}, {"id": "e2"}],
            "relationships": [{"source_id": "e1", "target_id": "e2"}],
            "dimensions": {"coupling": 80.0},
        }

        diff, impacts = comparator.compare(from_commit, to_commit)

        assert len(diff.relationships_added) == 1
        assert diff.relationships_added[0]["source_id"] == "e1"

    def test_compare_score_impact(self):
        """Score impact calculated."""
        comparator = CommitComparator()
        from_commit = {
            "commit_sha": "abc123",
            "elements": [],
            "relationships": [],
            "dimensions": {"coupling": 70.0, "modularity": 75.0, "cohesion": 80.0},
        }
        to_commit = {
            "commit_sha": "def456",
            "elements": [],
            "relationships": [{"source_id": "e1", "target_id": "e2"}],
            "dimensions": {"coupling": 85.0, "modularity": 75.0, "cohesion": 80.0},
        }

        diff, impacts = comparator.compare(from_commit, to_commit)

        assert len(impacts) > 0
        coupling_impact = next((i for i in impacts if i.dimension == "coupling"), None)
        assert coupling_impact is not None
        assert coupling_impact.change == pytest.approx(15.0)


class TestHealthStatus:
    """Tests for health status in hugo_export."""

    def test_health_status_calculating(self):
        """Health status calculated correctly."""
        from archi_c4_score.hugo_export import DashboardGenerator

        generator = DashboardGenerator()

        trends = [{"direction": "INCREASING"}, {"direction": "DECREASING"}]
        assert generator.calculate_health_status(trends) == "STABLE"

        trends = [
            {"direction": "INCREASING"},
            {"direction": "INCREASING"},
            {"direction": "DECREASING"},
        ]
        assert generator.calculate_health_status(trends) == "IMPROVING"

        trends = [
            {"direction": "DECREASING"},
            {"direction": "DECREASING"},
            {"direction": "INCREASING"},
        ]
        assert generator.calculate_health_status(trends) == "DECLINING"

    def test_health_status_empty_trends(self):
        """Empty trends returns STABLE."""
        from archi_c4_score.hugo_export import DashboardGenerator

        generator = DashboardGenerator()
        assert generator.calculate_health_status([]) == "STABLE"
