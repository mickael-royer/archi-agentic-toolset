"""Timeline service for architecture score history and trend analysis."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class TrendDirection(StrEnum):
    """Trend direction classification."""

    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    STABLE = "STABLE"


class HealthStatus(StrEnum):
    """Overall health status of architecture."""

    IMPROVING = "IMPROVING"
    DECLINING = "DECLINING"
    STABLE = "STABLE"


@dataclass
class TimelinePoint:
    """A single point in the timeline."""

    position: int
    sha: str
    date: datetime
    author: str
    message: str | None
    composite_score: float
    dimensions: dict[str, float]
    element_count: int
    relationship_count: int
    score_delta: float | None = None
    is_significant: bool = False
    delta_threshold: float = 10.0


@dataclass
class TrendLine:
    """Calculated trend for a scoring dimension."""

    dimension: str
    direction: TrendDirection
    slope: float
    confidence: float


@dataclass
class ScoreDelta:
    """Significant score change between commits."""

    magnitude: float
    direction: str
    commit: str
    affected_dimensions: list[str]


@dataclass
class Timeline:
    """Complete timeline data."""

    repository_url: str
    commits: list[TimelinePoint]
    trends: list[TrendLine]
    significant_changes: list[ScoreDelta]
    pagination: dict[str, Any]
    gaps: list[str] = field(default_factory=list)


@dataclass
class CommitDiff:
    """Element and relationship changes between commits."""

    from_sha: str
    to_sha: str
    elements_added: list[dict[str, Any]] = field(default_factory=list)
    elements_removed: list[dict[str, Any]] = field(default_factory=list)
    elements_modified: list[dict[str, Any]] = field(default_factory=list)
    relationships_added: list[dict[str, Any]] = field(default_factory=list)
    relationships_removed: list[dict[str, Any]] = field(default_factory=list)
    relationships_modified: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ScoreImpact:
    """Explanation of how changes affected scores."""

    dimension: str
    change: float
    explanation: str


class TimelineService:
    """Service for generating timeline and analyzing trends."""

    DEFAULT_DELTA_THRESHOLD = 10.0
    DEFAULT_SLOPE_THRESHOLD = 0.1

    def __init__(self, delta_threshold: float = DEFAULT_DELTA_THRESHOLD) -> None:
        """Initialize timeline service."""
        self.delta_threshold = delta_threshold

    def calculate_score_delta(
        self,
        current_score: float,
        previous_score: float | None,
    ) -> tuple[float | None, bool]:
        """Calculate score delta and determine if significant."""
        if previous_score is None:
            return None, False
        delta = current_score - previous_score
        is_significant = abs(delta) >= self.delta_threshold
        return delta, is_significant

    def get_timeline(
        self,
        repository_url: str,
        scored_commits: list[dict[str, Any]],
        limit: int = 30,
        offset: int = 0,
    ) -> Timeline:
        """Generate timeline from scored commits."""
        from datetime import datetime, timezone

        def to_aware(dt):
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt

        def get_sort_key(c):
            d = c.get("commit_date")
            if isinstance(d, datetime):
                return to_aware(d)
            if isinstance(d, str):
                try:
                    return datetime.fromisoformat(d.replace("Z", "+00:00"))
                except Exception:
                    return datetime.min.replace(tzinfo=timezone.utc)
            return datetime.min.replace(tzinfo=timezone.utc)

        logger.info(f"Generating timeline for {repository_url}: {len(scored_commits)} commits")

        valid_commits = [c for c in scored_commits if c.get("composite_score") is not None]
        sorted_commits = sorted(valid_commits, key=get_sort_key)

        timeline_points: list[TimelinePoint] = []
        previous_score: float | None = None
        gaps: list[str] = []

        for i, commit in enumerate(sorted_commits):
            composite = commit.get("composite_score")
            if composite is None:
                continue
            delta, is_significant = self.calculate_score_delta(composite, previous_score)

            point = TimelinePoint(
                position=i,
                sha=commit["commit_sha"],
                date=commit["commit_date"],
                author=commit.get("author", "unknown"),
                message=commit.get("message"),
                composite_score=composite,
                dimensions=commit.get("dimensions", {}),
                element_count=commit.get("element_count", 0),
                relationship_count=commit.get("relationship_count", 0),
                score_delta=delta,
                is_significant=is_significant,
                delta_threshold=self.delta_threshold,
            )
            timeline_points.append(point)
            previous_score = composite

        paginated = timeline_points[offset : offset + limit]
        significant = [
            ScoreDelta(
                magnitude=abs(p.score_delta or 0),
                direction="improvement" if (p.score_delta or 0) > 0 else "degradation",
                commit=p.sha,
                affected_dimensions=[],
            )
            for p in paginated
            if p.is_significant and p.score_delta is not None
        ]

        return Timeline(
            repository_url=repository_url,
            commits=paginated,
            trends=[],
            significant_changes=significant,
            pagination={
                "total": len(timeline_points),
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < len(timeline_points),
            },
            gaps=gaps,
        )

    def calculate_trends(
        self,
        timeline_points: list[TimelinePoint],
    ) -> list[TrendLine]:
        """Calculate trend direction for each dimension using linear regression."""
        if len(timeline_points) < 2:
            return []

        dimensions = ["coupling", "modularity", "cohesion", "extensibility", "maintainability"]
        trends: list[TrendLine] = []

        valid_points = [p for p in timeline_points if p.dimensions]

        for dimension in dimensions:
            scores = [p.dimensions.get(dimension) for p in valid_points]
            scores = [s for s in scores if s is not None]
            if not scores:
                continue
            slope, confidence = self._linear_regression(range(len(scores)), scores)
            direction = self._classify_trend(slope)
            trends.append(
                TrendLine(
                    dimension=dimension,
                    direction=direction,
                    slope=slope,
                    confidence=confidence,
                )
            )

        return trends

    def _linear_regression(
        self,
        x: range,
        y: list[float],
    ) -> tuple[float, float]:
        """Calculate linear regression slope and R² confidence."""
        n = len(y)
        if n < 2:
            return 0.0, 0.0

        x_vals = list(x)
        x_mean = sum(x_vals) / n
        y_mean = sum(y) / n

        numerator = sum((x_vals[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0, 0.0

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        ss_res = sum((y[i] - (slope * x_vals[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        return slope, max(0.0, r_squared)

    def _classify_trend(self, slope: float) -> TrendDirection:
        """Classify trend direction based on slope."""
        if abs(slope) < self.DEFAULT_SLOPE_THRESHOLD:
            return TrendDirection.STABLE
        return TrendDirection.INCREASING if slope > 0 else TrendDirection.DECREASING


class CommitComparator:
    """Service for comparing two commits."""

    def compare(
        self,
        from_commit: dict[str, Any],
        to_commit: dict[str, Any],
    ) -> tuple[CommitDiff, list[ScoreImpact]]:
        """Compare two commits and return diff with scoring impact."""
        from_elements = {e["id"]: e for e in from_commit.get("elements", [])}
        to_elements = {e["id"]: e for e in to_commit.get("elements", [])}

        from_rels = {
            f"{r['source_id']}->{r['target_id']}": r for r in from_commit.get("relationships", [])
        }
        to_rels = {
            f"{r['source_id']}->{r['target_id']}": r for r in to_commit.get("relationships", [])
        }

        diff = CommitDiff(
            from_sha=from_commit["commit_sha"],
            to_sha=to_commit["commit_sha"],
            elements_added=[
                e for id_ in to_elements if id_ not in from_elements for e in [to_elements[id_]]
            ],
            elements_removed=[
                e for id_ in from_elements if id_ not in to_elements for e in [from_elements[id_]]
            ],
            relationships_added=[
                r for key in to_rels if key not in from_rels for r in [to_rels[key]]
            ],
            relationships_removed=[
                r for key in from_rels if key not in to_rels for r in [from_rels[key]]
            ],
        )

        impacts = self._calculate_impacts(from_commit, to_commit, diff)

        return diff, impacts

    def _calculate_impacts(
        self,
        from_commit: dict[str, Any],
        to_commit: dict[str, Any],
        diff: CommitDiff,
    ) -> list[ScoreImpact]:
        """Calculate how changes affected scoring dimensions."""
        impacts: list[ScoreImpact] = []

        from_dims = from_commit.get("dimensions", {})
        to_dims = to_commit.get("dimensions", {})

        for dimension in ["coupling", "modularity", "cohesion"]:
            from_val = from_dims.get(dimension, 0)
            to_val = to_dims.get(dimension, 0)
            change = to_val - from_val

            if abs(change) > 0.5:
                rel_count = len(diff.relationships_added)
                explanation = f"{dimension.capitalize()} changed by {change:.1f} points"
                if dimension == "coupling" and rel_count > 0:
                    explanation += f" due to {rel_count} new dependencies"
                impacts.append(
                    ScoreImpact(
                        dimension=dimension,
                        change=change,
                        explanation=explanation,
                    )
                )

        return impacts
