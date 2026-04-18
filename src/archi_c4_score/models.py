"""Data models for C4 Architecture Scoring."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class C4Level(StrEnum):
    """C4 model level enumeration."""

    SYSTEM = "System"
    CONTAINER = "Container"
    COMPONENT = "Component"


@dataclass
class ArchimateElement:
    """An element from the ArchiMate model."""

    id: str
    name: str
    element_type: str
    stereotype: str | None = None
    properties: dict[str, str] | None = None
    layer: str | None = None


@dataclass
class ArchimateModel:
    """Root model representing a coArchi2 export."""

    version: str
    elements: list[ArchimateElement]
    relationships: list["Relationship"]
    metadata: "ModelMetadata | None" = None


@dataclass
class Relationship:
    """A relationship in the ArchiMate model."""

    id: str
    relationship_type: str
    source_id: str
    target_id: str
    properties: dict[str, str] | None = None


@dataclass
class ModelMetadata:
    """Metadata for an ArchiMate model."""

    name: str
    exported: datetime | None = None
    author: str | None = None


@dataclass
class C4Node:
    """A C4 model node."""

    id: str
    name: str
    c4_level: C4Level
    parent_id: str | None = None
    git_commit: str | None = None
    imported_at: datetime | None = None
    properties: dict[str, str] | None = None


@dataclass
class C4Relationship:
    """A weighted relationship in the C4 model."""

    source_id: str
    target_id: str
    relationship_type: str
    weight: float = 1.0
    is_circular: bool = False


@dataclass
class Recommendation:
    """An actionable improvement recommendation."""

    id: str
    priority: str
    dimension: str
    target_node_id: str
    description: str
    rationale: str


@dataclass
class ContainerScore:
    """Score for a container."""

    node_id: str
    node_name: str
    composite: float
    coupling: float
    component_count: int
    stereotype: str = ""


@dataclass
class ComponentScore:
    """Score for a component."""

    node_id: str
    node_name: str
    composite: float
    coupling: float
    instability_index: float
    efferent_coupling: int
    afferent_coupling: int


@dataclass
class ScoringReport:
    """Comprehensive architecture score report."""

    report_id: str
    timestamp: datetime
    git_commit: str
    composite_score: float
    system_score: float
    container_scores: list[ContainerScore]
    component_scores: list[ComponentScore]
    recommendations: list[Recommendation]


@dataclass
class ScoredCommit:
    """A commit with its architecture score data."""

    id: str
    commit_sha: str
    repository_url: str
    commit_date: datetime
    author: str
    message: str | None
    composite_score: float
    coupling_score: float
    modularity_score: float
    cohesion_score: float
    extensibility_score: float
    maintainability_score: float
    element_count: int
    relationship_count: int
    scored_at: datetime


@dataclass
class TimelineReport:
    """Timeline data with trends and analysis."""

    repository_url: str
    commits: list[ScoredCommit]
    health_status: str
    trends: list["TrendAnalysis"]
    significant_changes: list["SignificantChange"]


@dataclass
class TrendAnalysis:
    """Trend direction for a scoring dimension."""

    dimension: str
    direction: str
    slope: float
    confidence: float


@dataclass
class SignificantChange:
    """Significant score change between commits."""

    magnitude: float
    direction: str
    commit_sha: str
    affected_dimensions: list[str]


@dataclass
class TreemapCell:
    """Cell data for treemap visualization."""

    id: str
    name: str
    level: str
    score: float
    size: int
    parent_id: str | None = None
    stereotype: str = ""


@dataclass
class ScoreSnapshot:
    """Point-in-time score record linked to a commit."""

    id: str
    commit_sha: str
    repository_url: str
    commit_date: datetime
    system_score: float
    container_scores_json: str
    scored_at: datetime
