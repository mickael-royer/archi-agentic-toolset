"""Unit tests for coArchi2 parser."""

import pytest
import json
from archi_c4_score.parser import CoArchi2Parser, ParserError


SAMPLE_COARCHI2_JSON = {
    "version": "3.2",
    "elements": [
        {
            "id": "elem-1",
            "name": "User Service",
            "element_type": "ApplicationComponent",
            "stereotype": "<<Container>>",
            "properties": {},
        },
        {
            "id": "elem-2",
            "name": "Database",
            "element_type": "ApplicationComponent",
            "stereotype": "<<Component>>",
            "properties": {"technology": "PostgreSQL"},
        },
        {
            "id": "elem-3",
            "name": "Legacy Module",
            "element_type": "ApplicationComponent",
            "properties": {},
        },
    ],
    "relationships": [
        {
            "id": "rel-1",
            "relationship_type": "flow-to",
            "source": "elem-1",
            "target": "elem-2",
            "properties": {},
        },
        {
            "id": "rel-2",
            "relationship_type": "trigger",
            "source": "elem-2",
            "target": "elem-3",
            "properties": {},
        },
    ],
    "metadata": {
        "name": "Test Architecture",
        "exported": "2024-01-15T10:00:00Z",
    },
}


class TestCoArchi2Parser:
    """Tests for coArchi2 JSON parser."""

    def test_parse_valid_json(self):
        """Parser correctly parses valid coArchi2 JSON."""
        parser = CoArchi2Parser()
        model = parser.parse(SAMPLE_COARCHI2_JSON)
        assert model.version == "3.2"
        assert len(model.elements) == 3
        assert len(model.relationships) == 2

    def test_extract_elements(self):
        """Parser extracts all elements."""
        parser = CoArchi2Parser()
        elements = parser.extract_elements(SAMPLE_COARCHI2_JSON)
        assert len(elements) == 3
        assert elements[0].id == "elem-1"
        assert elements[0].name == "User Service"
        assert elements[0].element_type == "ApplicationComponent"

    def test_extract_relationships(self):
        """Parser extracts all relationships."""
        parser = CoArchi2Parser()
        rels = parser.extract_relationships(SAMPLE_COARCHI2_JSON)
        assert len(rels) == 2
        assert rels[0].relationship_type == "flow-to"
        assert rels[0].source_id == "elem-1"

    def test_parse_file(self, tmp_path):
        """Parser reads from file path."""
        json_file = tmp_path / "model.json"
        json_file.write_text(json.dumps(SAMPLE_COARCHI2_JSON))
        parser = CoArchi2Parser()
        model = parser.parse_file(str(json_file))
        assert model.version == "3.2"
        assert len(model.elements) == 3

    def test_filter_application_components(self):
        """Parser filters only ApplicationComponent elements."""
        parser = CoArchi2Parser()
        elements = parser.extract_elements(SAMPLE_COARCHI2_JSON)
        app_components = parser.filter_application_components(elements)
        assert len(app_components) == 3
        assert all(e.element_type == "ApplicationComponent" for e in app_components)


class TestParserError:
    """Tests for parser error handling."""

    def test_invalid_json_error(self):
        """Parser raises error for invalid JSON."""
        parser = CoArchi2Parser()
        with pytest.raises(ParserError) as exc_info:
            parser.parse({"invalid": "json"})
        assert "Missing required field" in str(exc_info.value)

    def test_missing_elements_error(self):
        """Parser raises error for missing elements."""
        parser = CoArchi2Parser()
        with pytest.raises(ParserError) as exc_info:
            parser.parse({"version": "3.2", "relationships": []})
        assert "Missing required field" in str(exc_info.value)

    def test_error_message(self):
        """Error has descriptive message."""
        error = ParserError("Test error", field="version")
        assert "Test error" in str(error)
        assert "version" in str(error)
