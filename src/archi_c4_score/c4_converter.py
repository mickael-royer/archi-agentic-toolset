"""C4 Entity Converter - Convert Archimate elements to C4 entities."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from archi_c4_score.models import (
    C4Level,
    C4Node,
    C4Relationship,
    ArchimateElement,
    Relationship,
)

if TYPE_CHECKING:
    from archi_c4_score.models import ArchimateModel


C4_STEREOTYPE_MAP = {
    "SoftwareSystem": C4Level.SYSTEM,
    "Software System": C4Level.SYSTEM,
    "System": C4Level.SYSTEM,
    "Container": C4Level.CONTAINER,
    "ApplicationContainer": C4Level.CONTAINER,
    "Component": C4Level.COMPONENT,
    "ApplicationComponent": C4Level.COMPONENT,
}


def is_c4_component(element: "ArchimateElement") -> bool:
    """Check if element qualifies as C4 component."""
    if element.element_type == "ApplicationComponent":
        if element.stereotype in ("Software System", "SoftwareSystem", "Container"):
            return True
        return False
    if element.element_type == "ApplicationFunction":
        if element.stereotype == "Component":
            return True
        return False
    return False


RELATIONSHIP_WEIGHTS = {
    "Flow": 1.0,
    "flow": 1.0,
    "Serving": 1.0,
    "serving": 1.0,
    "Dependency": 1.0,
    "dependency": 1.0,
    "Trigger": 0.5,
    "trigger": 0.5,
    "AsyncTrigger": 0.5,
    "async": 0.5,
}


@dataclass
class C4ConversionResult:
    """Result of converting Archimate model to C4."""

    nodes: list[C4Node]
    relationships: list[C4Relationship]
    system_id: str | None = None


class C4Converter:
    """Convert Archimate elements to C4 model entities."""

    def convert_model(self, model: "ArchimateModel") -> C4ConversionResult:
        """Convert an Archimate model to C4 entities.

        Args:
            model: Parsed Archimate model

        Returns:
            C4ConversionResult with nodes and relationships
        """
        nodes: list[C4Node] = []
        relationships: list[C4Relationship] = []
        system_id: str | None = None

        element_map: dict[str, ArchimateElement] = {e.id: e for e in model.elements}

        for element in model.elements:
            c4_level = self._get_c4_level(element)
            if c4_level is None:
                continue

            node = C4Node(
                id=element.id,
                name=element.name,
                c4_level=c4_level,
                parent_id=None,
                properties=element.properties,
            )
            nodes.append(node)

            if c4_level == C4Level.SYSTEM:
                system_id = element.id

        for node in nodes:
            if node.c4_level == C4Level.COMPONENT:
                node.parent_id = self._find_container_parent(
                    node.id, model.relationships, element_map
                )

        for rel in model.relationships:
            if rel.source_id in element_map and rel.target_id in element_map:
                if not is_c4_component(element_map[rel.source_id]):
                    continue
                if not is_c4_component(element_map[rel.target_id]):
                    continue
                weight = RELATIONSHIP_WEIGHTS.get(rel.relationship_type, 1.0)
                c4_rel = C4Relationship(
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    relationship_type=rel.relationship_type,
                    weight=weight,
                )
                relationships.append(c4_rel)

        return C4ConversionResult(
            nodes=nodes,
            relationships=relationships,
            system_id=system_id,
        )

    def _get_c4_level(self, element: ArchimateElement) -> C4Level | None:
        """Get C4 level from Archimate element."""
        if element.stereotype:
            level = C4_STEREOTYPE_MAP.get(element.stereotype)
            if level:
                return level

        if element.element_type:
            level = C4_STEREOTYPE_MAP.get(element.element_type)
            if level:
                return level

        return None

    def _find_container_parent(
        self,
        component_id: str,
        relationships: list[Relationship],
        element_map: dict[str, ArchimateElement],
    ) -> str | None:
        """Find the parent container for a component."""
        composition_types = {"Composition", "composition", "Aggregation", "aggregation"}

        for rel in relationships:
            if rel.relationship_type not in composition_types:
                continue
            if rel.target_id == component_id and rel.source_id in element_map:
                source = element_map[rel.source_id]
                if self._get_c4_level(source) == C4Level.CONTAINER:
                    return rel.source_id

        return None
