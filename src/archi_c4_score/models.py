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
