"""XML parser for ArchiMate model files."""

import logging
from pathlib import Path
from xml.etree import ElementTree as ET

from archi_c4_score.models import ArchimateModel, ArchimateElement, Relationship

logger = logging.getLogger(__name__)


class ArchimateXMLElement:
    """An element parsed from XML."""

    def __init__(
        self,
        elem_id: str,
        name: str,
        element_type: str,
        stereotype: str | None = None,
        properties: dict[str, str] | None = None,
        layer: str | None = None,
    ):
        self.id = elem_id
        self.name = name
        self.element_type = element_type
        self.stereotype = stereotype
        self.properties = properties
        self.layer = layer


class ArchimateXMLRelationship:
    """A relationship parsed from XML."""

    def __init__(
        self,
        rel_id: str,
        relationship_type: str,
        source_id: str,
        target_id: str,
        properties: dict[str, str] | None = None,
    ):
        self.id = rel_id
        self.relationship_type = relationship_type
        self.source_id = source_id
        self.target_id = target_id
        self.properties = properties


class ArchimateXMLParser:
    """Parser for ArchiMate XML format (.archimate files)."""

    ELEMENT_TYPES = {
        "archimate:ApplicationComponent",
        "ApplicationComponent",
        "archimate:Container",
        "Container",
        "archimate:Component",
        "Component",
        "archimate:ApplicationFunction",
        "ApplicationFunction",
        "archimate:ApplicationInterface",
        "ApplicationInterface",
        "archimate:BusinessActor",
        "BusinessActor",
        "archimate:BusinessProcess",
        "BusinessProcess",
        "archimate:BusinessRole",
        "BusinessRole",
        "archimate:Node",
        "Node",
        "archimate:SystemSoftware",
        "SystemSoftware",
        "archimate:TechnologyInterface",
        "TechnologyInterface",
    }

    RELATIONSHIP_TYPES = {
        "archimate:CompositionRelationship",
        "CompositionRelationship",
        "archimate:AggregationRelationship",
        "AggregationRelationship",
        "archimate:AssignmentRelationship",
        "AssignmentRelationship",
        "archimate:RealizationRelationship",
        "RealizationRelationship",
        "archimate:ServingRelationship",
        "ServingRelationship",
        "archimate:DependencyRelationship",
        "DependencyRelationship",
        "archimate:FlowRelationship",
        "FlowRelationship",
        "archimate:TriggeringRelationship",
        "TriggeringRelationship",
        "archimate:AccessRelationship",
        "AccessRelationship",
        "Composition",
        "Aggregation",
        "Assignment",
        "Realization",
        "Serving",
        "Dependency",
        "Flow",
        "Triggering",
        "Access",
    }

    def parse_file(
        self, file_path: str | Path
    ) -> tuple[list[ArchimateXMLElement], list[ArchimateXMLRelationship]]:
        """Parse an ArchiMate XML file.

        Returns:
            Tuple of (elements, relationships)
        """
        path = Path(file_path)
        logger.info(f"Parsing XML file: {path}")

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        tree = ET.parse(path)
        root = tree.getroot()

        elements = self._parse_elements(root)
        relationships = self._parse_relationships(root)

        logger.info(f"Parsed {len(elements)} elements, {len(relationships)} relationships")

        return elements, relationships

    def _parse_elements(self, root: ET.Element) -> list[ArchimateXMLElement]:
        """Parse all elements from the XML root."""
        elements = []

        for elem in root.iter():
            xsi_type = elem.get("{http://www.w3.org/2001/XMLSchema-instance}type")

            if xsi_type and xsi_type in self.ELEMENT_TYPES:
                elem_id = elem.get("id", "")
                name = elem.get("name", "")

                stereotype = self._get_property(elem, "Stereotype")
                layer = self._get_layer(elem)

                normalized_type = self._normalize_type(xsi_type)

                elements.append(
                    ArchimateXMLElement(
                        elem_id=elem_id,
                        name=name,
                        element_type=normalized_type,
                        stereotype=stereotype,
                        layer=layer,
                    )
                )

        return elements

    def _parse_relationships(self, root: ET.Element) -> list[ArchimateXMLRelationship]:
        """Parse all relationships from the XML root."""
        relationships = []

        for elem in root.iter():
            xsi_type = elem.get("{http://www.w3.org/2001/XMLSchema-instance}type")

            if xsi_type and xsi_type in self.RELATIONSHIP_TYPES:
                rel_id = elem.get("id", "")
                source = elem.get("source")
                target = elem.get("target")

                if source and target:
                    normalized_type = self._normalize_type(xsi_type)
                    relationships.append(
                        ArchimateXMLRelationship(
                            rel_id=rel_id,
                            relationship_type=normalized_type,
                            source_id=source,
                            target_id=target,
                        )
                    )

        return relationships

    def _normalize_type(self, xsi_type: str) -> str:
        """Normalize element/relationship type names."""
        type_map = {
            "archimate:ApplicationComponent": "ApplicationComponent",
            "archimate:Container": "Container",
            "archimate:Component": "Component",
            "archimate:ApplicationFunction": "ApplicationFunction",
            "archimate:ApplicationInterface": "ApplicationInterface",
            "archimate:BusinessActor": "BusinessActor",
            "archimate:BusinessProcess": "BusinessProcess",
            "archimate:BusinessRole": "BusinessRole",
            "archimate:Node": "Node",
            "archimate:SystemSoftware": "SystemSoftware",
            "archimate:TechnologyInterface": "TechnologyInterface",
            "archimate:CompositionRelationship": "Composition",
            "archimate:AggregationRelationship": "Aggregation",
            "archimate:AssignmentRelationship": "Assignment",
            "archimate:RealizationRelationship": "Realization",
            "archimate:ServingRelationship": "Serving",
            "archimate:DependencyRelationship": "Dependency",
            "archimate:FlowRelationship": "Flow",
            "archimate:TriggeringRelationship": "Triggering",
            "archimate:AccessRelationship": "Access",
        }

        return type_map.get(xsi_type, xsi_type.split(":")[-1])

    def _get_property(self, elem: ET.Element, key: str) -> str | None:
        """Get a property value by key."""
        for prop in elem.findall("property"):
            if prop.get("key") == key:
                return prop.get("value")
        return None

    def _get_layer(self, elem: ET.Element) -> str | None:
        """Get the layer from parent folder."""
        parent = elem.find("..")
        if parent is not None:
            parent_type = parent.get("type")
            if parent_type:
                return parent_type.capitalize()
        return None

    def to_model(
        self,
        elements: list[ArchimateXMLElement],
        relationships: list[ArchimateXMLRelationship],
    ) -> ArchimateModel:
        """Convert parsed XML to standard ArchimateModel.

        Args:
            elements: Parsed XML elements
            relationships: Parsed XML relationships

        Returns:
            Standard ArchimateModel for use with scoring
        """
        model_elements = [
            ArchimateElement(
                id=e.id,
                name=e.name,
                element_type=e.element_type,
                stereotype=e.stereotype,
                properties=e.properties,
                layer=e.layer,
            )
            for e in elements
        ]

        model_relationships = [
            Relationship(
                id=r.id,
                relationship_type=r.relationship_type,
                source_id=r.source_id,
                target_id=r.target_id,
                properties=r.properties,
            )
            for r in relationships
        ]

        return ArchimateModel(
            version="1.0",
            elements=model_elements,
            relationships=model_relationships,
        )

    def parse_to_model(self, file_path: str | Path) -> ArchimateModel:
        """Parse an XML file and return a standard ArchimateModel.

        Args:
            file_path: Path to .archimate XML file

        Returns:
            Standard ArchimateModel ready for scoring
        """
        elements, relationships = self.parse_file(file_path)
        return self.to_model(elements, relationships)
