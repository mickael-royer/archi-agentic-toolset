"""Integration tests for full pipeline."""

from archi_c4_score.mapper import C4Mapper
from archi_c4_score.parser import CoArchi2Parser


class TestPipelineIntegration:
    """Integration tests for the full import pipeline."""

    def test_parse_to_map_to_score_pipeline(self):
        """Test complete pipeline from JSON to scored model."""
        data = {
            "version": "1.0",
            "elements": [
                {
                    "id": "sys-1",
                    "name": "System A",
                    "element_type": "application",
                    "stereotype": "<<Software System>>",
                    "properties": {"description": "Main system"},
                },
                {
                    "id": "con-1",
                    "name": "Container B",
                    "element_type": "application",
                    "stereotype": "<<Container>>",
                    "properties": {},
                },
            ],
            "relationships": [
                {
                    "id": "rel-1",
                    "relationship_type": "flow-to",
                    "source_id": "con-1",
                    "target_id": "sys-1",
                }
            ],
        }

        parser = CoArchi2Parser()
        model = parser.parse(data)

        assert len(model.elements) == 2
        assert len(model.relationships) == 1

        mapper = C4Mapper()
        nodes, rels = mapper.map_model(model.elements, model.relationships)

        assert len(nodes) == 2
        assert len(rels) == 1
        assert rels[0].weight == 3.0

    def test_c4_levels_mapping(self):
        """Test correct C4 level assignment."""
        data = {
            "version": "1.0",
            "elements": [
                {
                    "id": "s1",
                    "name": "System",
                    "element_type": "app",
                    "stereotype": "<<Software System>>",
                },
                {
                    "id": "c1",
                    "name": "Container",
                    "element_type": "app",
                    "stereotype": "<<Container>>",
                },
                {
                    "id": "m1",
                    "name": "Component",
                    "element_type": "app",
                    "stereotype": "<<Component>>",
                },
            ],
            "relationships": [],
        }

        parser = CoArchi2Parser()
        model = parser.parse(data)
        mapper = C4Mapper()
        nodes, _ = mapper.map_model(model.elements, model.relationships)

        from archi_c4_score.models import C4Level

        levels = {n.id: n.c4_level for n in nodes}
        assert levels["s1"] == C4Level.SYSTEM
        assert levels["c1"] == C4Level.CONTAINER
        assert levels["m1"] == C4Level.COMPONENT

    def test_dependency_weights(self):
        """Test correct dependency weight assignment."""
        data = {
            "version": "1.0",
            "elements": [
                {"id": "a", "name": "A", "element_type": "app", "stereotype": "<<Component>>"},
                {"id": "b", "name": "B", "element_type": "app", "stereotype": "<<Component>>"},
            ],
            "relationships": [
                {"id": "r1", "relationship_type": "flow-to", "source_id": "a", "target_id": "b"},
                {"id": "r2", "relationship_type": "trigger", "source_id": "b", "target_id": "a"},
            ],
        }

        parser = CoArchi2Parser()
        model = parser.parse(data)
        mapper = C4Mapper()
        _, rels = mapper.map_model(model.elements, model.relationships)

        weights = {(r.source_id, r.target_id): r.weight for r in rels}
        assert weights[("a", "b")] == 3.0
        assert weights[("b", "a")] == 1.0


class TestTimelinePerformance:
    """Performance tests for timeline generation (SC-001)."""

    def test_timeline_100_commits_under_30_seconds(self):
        """SC-001: Timeline for 100 commits must complete in under 30 seconds."""
        import time
        from datetime import datetime, timedelta
        from archi_c4_score.timeline import TimelineService

        service = TimelineService()
        base_date = datetime.now() - timedelta(days=100)

        commits = [
            {
                "commit_sha": f"abc{i:03d}",
                "repository_url": "https://github.com/example/repo",
                "commit_date": (base_date + timedelta(days=i)).isoformat(),
                "author": "Test Author",
                "message": f"Commit {i}",
                "composite_score": 70.0 + (i * 0.15),
                "coupling_score": 80.0 - (i * 0.1),
                "modularity_score": 70.0 + (i * 0.05),
                "cohesion_score": 75.0,
                "extensibility_score": 65.0 + (i * 0.05),
                "maintainability_score": 72.0,
                "element_count": 10 + i,
                "relationship_count": 15 + (i * 2),
            }
            for i in range(100)
        ]

        start = time.perf_counter()
        timeline = service.get_timeline("https://github.com/example/repo", commits, limit=100)
        elapsed = time.perf_counter() - start

        assert elapsed < 30.0, f"Timeline generation took {elapsed:.2f}s, expected < 30s"
        assert len(timeline.commits) == 100
        assert timeline.pagination["total"] == 100

    def test_trends_calculation_performance(self):
        """Trend calculation for 100 commits completes quickly."""
        import time
        from datetime import datetime, timedelta
        from archi_c4_score.timeline import TimelineService, TimelinePoint

        service = TimelineService()
        base_date = datetime.now()

        points = [
            TimelinePoint(
                position=i,
                sha=f"abc{i:03d}",
                date=base_date + timedelta(days=i),
                author="Test",
                message=f"Commit {i}",
                composite_score=70.0 + (i * 0.15),
                dimensions={
                    "coupling": 80.0 - (i * 0.1),
                    "modularity": 70.0 + (i * 0.05),
                    "cohesion": 75.0,
                    "extensibility": 65.0 + (i * 0.05),
                    "maintainability": 72.0,
                },
                element_count=10 + i,
                relationship_count=15 + (i * 2),
            )
            for i in range(100)
        ]

        start = time.perf_counter()
        trends = service.calculate_trends(points)
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"Trend calculation took {elapsed:.2f}s, expected < 1s"
        assert len(trends) == 5  # 5 dimensions
