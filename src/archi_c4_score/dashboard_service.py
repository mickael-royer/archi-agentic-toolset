"""Dashboard service for generating recommendations."""

import logging
from datetime import datetime, timezone
from typing import Any

from archi_c4_score.recommendation_models.recommendations import (
    DateRange,
    DimensionName,
    SignificantChange,
    TrendContext,
    TrendDimension,
    TrendDirection,
)

logger = logging.getLogger(__name__)


def build_trend_context(
    repository_url: str,
    repository_name: str,
    commits: list[Any],
    trends: list[Any],
    significant_changes: list[Any],
) -> TrendContext:
    """Build TrendContext from dashboard data.

    Args:
        repository_url: Repository URL
        repository_name: Repository name
        commits: Timeline commits
        trends: Calculated trends
        significant_changes: Significant score changes

    Returns:
        TrendContext for LLM recommendation generation
    """
    date_range = DateRange(
        start=commits[-1].date if commits else datetime.now(timezone.utc),
        end=commits[0].date if commits else datetime.now(timezone.utc),
    )

    dimensions = []
    for t in trends:
        dim_name = DimensionName.COMPOSITE
        for d in DimensionName:
            if t.dimension.lower() == d.value:
                dim_name = d
                break

        dimensions.append(
            TrendDimension(
                dimension=dim_name,
                direction=TrendDirection(t.direction.value),
                slope=t.slope,
                confidence=t.confidence,
            )
        )

    sig_changes = []
    for s in significant_changes:
        direction = (
            "IMPROVING" if s.direction.upper() in ["IMPROVING", "INCREASING"] else "DEGRADING"
        )
        sig_changes.append(
            SignificantChange(
                commit_sha=s.commit,
                date=datetime.now(timezone.utc),
                magnitude=s.magnitude,
                direction=direction,
                affected_dimensions=s.affected_dimensions,
            )
        )

    return TrendContext(
        repository_url=repository_url,
        repository_name=repository_name,
        date_range=date_range,
        dimensions=dimensions,
        significant_changes=sig_changes,
    )


def format_recommendations_response(rec_set: Any) -> dict[str, Any]:
    """Format RecommendationSet for API response.

    Args:
        rec_set: RecommendationSet from GeminiClient

    Returns:
        Dict suitable for API response
    """
    return {
        "recommendations": [
            {
                "id": r.id,
                "priority": r.priority.value,
                "dimension": r.dimension.value if r.dimension else None,
                "description": r.description,
                "impact": r.impact,
                "trend_refs": r.trend_refs,
            }
            for r in rec_set.recommendations
        ],
        "llm_available": rec_set.llm_available,
        "generated_at": rec_set.generated_at.isoformat(),
        "model_used": rec_set.model_used,
        "error_message": rec_set.error_message,
    }


def get_recommendations_for_dashboard(
    repository_url: str,
    repository_name: str,
    commits: list[Any],
    trends: list[Any],
    significant_changes: list[Any],
) -> dict[str, Any]:
    """Get recommendations for dashboard.

    Args:
        repository_url: Repository URL
        repository_name: Repository name
        commits: Timeline commits
        trends: Calculated trends
        significant_changes: Significant score changes

    Returns:
        Recommendations dict for dashboard response
    """
    if not commits:
        return {
            "recommendations": [],
            "llm_available": False,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "error_message": "No commits available",
        }

    try:
        from archi_c4_score.llm_service import GeminiClient

        trend_context = build_trend_context(
            repository_url=repository_url,
            repository_name=repository_name,
            commits=commits,
            trends=trends,
            significant_changes=significant_changes,
        )

        client = GeminiClient()
        rec_set = client.generate_recommendations(trend_context)

        return format_recommendations_response(rec_set)

    except ValueError as e:
        logger.warning(f"GEMINI_API_KEY not configured: {e}")
        return {
            "recommendations": [],
            "llm_available": False,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "error_message": "LLM not configured",
        }
    except Exception as e:
        logger.warning(f"Failed to generate recommendations: {e}")
        return {
            "recommendations": [],
            "llm_available": False,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "error_message": str(e),
        }
