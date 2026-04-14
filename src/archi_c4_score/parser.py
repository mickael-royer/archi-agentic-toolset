"""coArchi2 JSON parser for ArchiMate models."""

import json
import logging
from pathlib import Path

from archi_c4_score.models import (
    ArchimateElement,
    ArchimateModel,
    ModelMetadata,
    Relationship,
)

logger = logging.getLogger(__name__)


class ParserError(Exception):
    """Parser error with field context."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        detail = f" (field: {field})" if field else ""
        super().__init__(f"{message}{detail}")


class CoArchi2Parser:
    """Parser for coArchi2 export format."""

    REQUIRED_FIELDS = ["version", "elements", "relationships"]

    def parse(self, data: dict) -> ArchimateModel:
        """Parse coArchi2 JSON data into ArchimateModel."""
        self._validate_required_fields(data)

        elements = self.extract_elements(data)
        relationships = self.extract_relationships(data)
        metadata = self._extract_metadata(data)

        logger.info(
            f"Parsed model with {len(elements)} elements, {len(relationships)} relationships"
        )

        return ArchimateModel(
            version=data["version"],
            elements=elements,
            relationships=relationships,
            metadata=metadata,
        )

    def parse_file(self, file_path: str | Path) -> ArchimateModel:
        """Parse coArchi2 JSON from file."""
        path = Path(file_path)
        logger.info(f"Parsing file: {path}")

        if not path.exists():
            raise ParserError(f"File not found: {path}", field="file_path")

        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ParserError(f"Invalid JSON: {e.msg} at line {e.lineno}", field="json")

        return self.parse(data)

    def extract_elements(self, data: dict) -> list[ArchimateElement]:
        """Extract and parse elements from data."""
        elements = []
        for elem_data in data.get("elements", []):
            element_type = (
                elem_data.get("element_type")
                or elem_data.get("type")
                or elem_data.get("$type", "Unknown")
            )
            elements.append(
                ArchimateElement(
                    id=elem_data.get("id", ""),
                    name=elem_data.get("name", ""),
                    element_type=element_type,
                    stereotype=elem_data.get("stereotype"),
                    properties=elem_data.get("properties"),
                    layer=elem_data.get("layer"),
                )
            )
        logger.debug(f"Extracted {len(elements)} elements")
        return elements

    def extract_relationships(self, data: dict) -> list[Relationship]:
        """Extract and parse relationships from data."""
        rels = []
        for rel_data in data.get("relationships", []):
            rel_type = (
                rel_data.get("relationship_type")
                or rel_data.get("type")
                or rel_data.get("$type", "Unknown")
            )
            rels.append(
                Relationship(
                    id=rel_data.get("id", ""),
                    relationship_type=rel_type,
                    source_id=rel_data.get("source_id") or rel_data.get("source", ""),
                    target_id=rel_data.get("target_id") or rel_data.get("target", ""),
                    properties=rel_data.get("properties"),
                )
            )
        logger.debug(f"Extracted {len(rels)} relationships")
        return rels

    def filter_application_components(
        self, elements: list[ArchimateElement]
    ) -> list[ArchimateElement]:
        """Filter only ApplicationComponent elements."""
        app_components = [e for e in elements if e.element_type == "ApplicationComponent"]
        logger.debug(f"Filtered {len(app_components)} ApplicationComponent elements")
        return app_components

    def _validate_required_fields(self, data: dict) -> None:
        """Validate required fields are present."""
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                raise ParserError(
                    f"Missing required field: {field}",
                    field=field,
                )

    def _extract_metadata(self, data: dict) -> ModelMetadata | None:
        """Extract metadata if present."""
        metadata = data.get("metadata")
        if not metadata:
            return None
        return ModelMetadata(
            name=metadata.get("name", "Unknown"),
            exported=metadata.get("exported"),
            author=metadata.get("author"),
        )
