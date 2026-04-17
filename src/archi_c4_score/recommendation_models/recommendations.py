"""Pydantic models for LLM recommendation system."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Priority levels for recommendations."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TrendDirection(str, Enum):
    """Trend direction for scoring dimensions."""

    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    STABLE = "STABLE"


class ChangeDirection(str, Enum):
    """Direction of significant change."""

    IMPROVING = "IMPROVING"
    DEGRADING = "DEGRADING"


class DimensionName(str, Enum):
    """Architecture scoring dimension names."""

    COUPLING = "coupling"
    MODULARITY = "modularity"
    COHESION = "cohesion"
    EXTENSIBILITY = "extensibility"
    MAINTAINABILITY = "maintainability"
    COMPOSITE = "composite"


class DateRange(BaseModel):
    """Start and end dates for analysis period."""

    start: datetime = Field(..., description="Start of analysis period")
    end: datetime = Field(..., description="End of analysis period")


class TrendDimension(BaseModel):
    """Trend data for a single scoring dimension."""

    dimension: DimensionName | str = Field(
        ...,
        description="Dimension name (coupling, modularity, cohesion, extensibility, maintainability)",
    )
    direction: TrendDirection = Field(..., description="Overall trend direction")
    slope: float = Field(..., description="Rate of change per commit")
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        ..., description="Confidence score (0.0-1.0)"
    )
    current_value: float | None = Field(None, description="Current score value")
    start_value: float | None = Field(None, description="Score at start of period")
    affected_commits: list[str] = Field(
        default_factory=list, description="Commit SHAs that contributed to trend"
    )


class SignificantChange(BaseModel):
    """A commit with significant score change."""

    commit_sha: str = Field(..., pattern=r"^[a-f0-9]{7,40}$", description="Git commit SHA")
    date: datetime = Field(..., description="Commit date")
    magnitude: float = Field(..., description="Absolute score change")
    direction: ChangeDirection = Field(..., description="Whether score improved or degraded")
    affected_dimensions: list[str] = Field(..., description="Dimensions affected by this change")


class Recommendation(BaseModel):
    """An AI-generated suggestion based on trend analysis."""

    id: str = Field(..., pattern=r"^REC-\d{3}$", description="Unique identifier (e.g., REC-001)")
    priority: Priority = Field(..., description="Priority level for the recommendation")
    dimension: DimensionName | str | None = Field(
        None, description="Which scoring dimension this addresses"
    )
    description: str = Field(..., description="The recommendation text in markdown format")
    impact: str = Field(..., description="Expected impact description (qualitative)")
    trend_refs: list[str] = Field(
        default_factory=list,
        description="References to specific trends or commits that prompted this",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "REC-001",
                "priority": "HIGH",
                "dimension": "coupling",
                "description": "Reduce cyclic dependencies between containers",
                "impact": "High - addresses root cause of declining modularity",
                "trend_refs": ["abc1234", "def5678"],
            }
        }
    }


class RecommendationSet(BaseModel):
    """A collection of recommendations with priority ordering."""

    recommendations: Annotated[
        list[Recommendation],
        Field(max_length=5, description="Ordered list of recommendations (max 5)"),
    ] = Field(default_factory=list)
    llm_available: bool = Field(..., description="Whether the LLM service was successfully called")
    generated_at: datetime = Field(..., description="Timestamp when recommendations were generated")
    model_used: str | None = Field(None, description="Gemini model used for generation")
    error_message: str | None = Field(None, description="Error message if LLM was unavailable")

    model_config = {
        "json_schema_extra": {
            "example": {
                "recommendations": [
                    {
                        "id": "REC-001",
                        "priority": "HIGH",
                        "dimension": "coupling",
                        "description": "Reduce cyclic dependencies",
                        "impact": "High impact",
                        "trend_refs": [],
                    }
                ],
                "llm_available": True,
                "generated_at": "2026-04-16T10:00:00Z",
                "model_used": "gemini-2.0-flash",
            }
        }
    }


class TrendContext(BaseModel):
    """The trend data provided to the LLM for generating recommendations."""

    repository_url: str = Field(..., description="URL of the repository")
    repository_name: str = Field(..., description="Name of the repository")
    date_range: DateRange = Field(..., description="Start and end dates of analysis period")
    dimensions: Annotated[
        list[TrendDimension], Field(min_length=1, description="Trend data per scoring dimension")
    ] = Field(...)
    significant_changes: list[SignificantChange] = Field(
        default_factory=list,
        description="Commits with significant score changes",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "repository_url": "https://github.com/owner/repo",
                "repository_name": "repo",
                "date_range": {
                    "start": "2026-04-01T00:00:00Z",
                    "end": "2026-04-16T00:00:00Z",
                },
                "dimensions": [
                    {
                        "dimension": "coupling",
                        "direction": "DECREASING",
                        "slope": -0.5,
                        "confidence": 0.85,
                        "current_value": 45.0,
                        "start_value": 60.0,
                    }
                ],
                "significant_changes": [],
            }
        }
    }
