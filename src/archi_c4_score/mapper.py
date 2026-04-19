"""C4 model mapper for ArchiMate elements."""

import logging

from archi_c4_score.models import (
    ArchimateElement,
    C4Level,
    C4Node,
    C4Relationship,
    Relationship,
)

logger = logging.getLogger(__name__)


class MapperWarning(UserWarning):
    """Warning from C4 mapper."""

    pass


class C4Mapper:
    """Maps ArchiMate elements to C4 model."""

    STEREOTYPE_TO_LEVEL = {
        "<<Software System>>": C4Level.SYSTEM,
        "<<System>>": C4Level.SYSTEM,
        "<<Container>>": C4Level.CONTAINER,
        "<<Component>>": C4Level.COMPONENT,
        # Also support plain names (from Archi import)
        "Software System": C4Level.SYSTEM,
        "Container": C4Level.CONTAINER,
        "Component": C4Level.COMPONENT,
        "System Software": C4Level.SYSTEM,
    }

    DEPENDENCY_WEIGHTS = {
        "flow-to": 3.0,
        "trigger": 1.0,
    }
    DEFAULT_WEIGHT = 1.5

    def __init__(self) -> None:
        """Initialize C4 mapper."""
        self.warnings: list[UserWarning] = []

    def map_element(self, element: ArchimateElement) -> C4Node | None:
        """Map single ArchimateElement to C4Node."""
        stereotype = element.stereotype

        if not stereotype:
            logger.debug(f"Element {element.name} has no stereotype, defaulting to Component")
            c4_level = C4Level.COMPONENT
        elif stereotype in self.STEREOTYPE_TO_LEVEL:
            c4_level = self.STEREOTYPE_TO_LEVEL[stereotype]
        else:
            warning = MapperWarning(
                f"Unknown stereotype '{stereotype}' for element {element.name}, skipping"
            )
            self.warnings.append(warning)
            logger.warning(warning)
            return None

        return C4Node(
            id=element.id,
            name=element.name,
            c4_level=c4_level,
            properties=element.properties,
        )

    def map_model(
        self,
        elements: list[ArchimateElement],
        relationships: list[Relationship],
    ) -> tuple[list[C4Node], list[C4Relationship]]:
        """Map full ArchiMate model to C4 model."""
        logger.info(f"Mapping {len(elements)} elements to C4 model")

        element_map = {e.id: e for e in elements}
        c4_nodes: list[C4Node] = []
        c4_rels: list[C4Relationship] = []

        for element in elements:
            node = self.map_element(element)
            if node:
                c4_nodes.append(node)

        for rel in relationships:
            if rel.source_id not in element_map or rel.target_id not in element_map:
                continue

            weight = self.DEPENDENCY_WEIGHTS.get(rel.relationship_type, self.DEFAULT_WEIGHT)
            c4_rel = C4Relationship(
                source_id=rel.source_id,
                target_id=rel.target_id,
                relationship_type=rel.relationship_type,
                weight=weight,
            )
            c4_rels.append(c4_rel)

        logger.info(f"Mapped {len(c4_nodes)} C4 nodes, {len(c4_rels)} relationships")
        return c4_nodes, c4_rels

    def get_hierarchy(self, nodes: list[C4Node]) -> dict[C4Level, list[C4Node]]:
        """Group nodes by C4 level."""
        hierarchy: dict[C4Level, list[C4Node]] = {
            C4Level.SYSTEM: [],
            C4Level.CONTAINER: [],
            C4Level.COMPONENT: [],
        }
        for node in nodes:
            hierarchy[node.c4_level].append(node)
        return hierarchy
