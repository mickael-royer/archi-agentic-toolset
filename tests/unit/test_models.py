"""Unit tests for data models."""

from archi_c4_score.models import (
    ArchimateElement,
    C4Level,
    C4Node,
    C4Relationship,
)


class TestArchimateElement:
    """Tests for ArchimateElement dataclass."""

    def test_create_element(self):
        """Element creation with required fields."""
        element = ArchimateElement(
            id="elem-1",
            name="User Service",
            element_type="ApplicationComponent",
        )
        assert element.id == "elem-1"
        assert element.name == "User Service"
        assert element.element_type == "ApplicationComponent"

    def test_element_with_stereotype(self):
        """Element with optional stereotype."""
        element = ArchimateElement(
            id="elem-1",
            name="API Gateway",
            element_type="ApplicationComponent",
            stereotype="<<Container>>",
        )
        assert element.stereotype == "<<Container>>"

    def test_element_with_properties(self):
        """Element with additional properties."""
        element = ArchimateElement(
            id="elem-1",
            name="Auth Service",
            element_type="ApplicationComponent",
            properties={"technology": "Python", "framework": "FastAPI"},
        )
        assert element.properties == {"technology": "Python", "framework": "FastAPI"}


class TestC4Node:
    """Tests for C4Node dataclass."""

    def test_create_node(self):
        """Node creation with required fields."""
        node = C4Node(
            id="node-1",
            name="User Service",
            c4_level=C4Level.CONTAINER,
        )
        assert node.id == "node-1"
        assert node.name == "User Service"
        assert node.c4_level == C4Level.CONTAINER

    def test_node_with_parent(self):
        """Node with parent reference."""
        node = C4Node(
            id="node-1",
            name="Auth Module",
            c4_level=C4Level.COMPONENT,
            parent_id="parent-1",
        )
        assert node.parent_id == "parent-1"

    def test_node_c4_levels(self):
        """Verify all C4 levels are available."""
        assert C4Level.SYSTEM == "System"
        assert C4Level.CONTAINER == "Container"
        assert C4Level.COMPONENT == "Component"


class TestC4Relationship:
    """Tests for C4Relationship dataclass."""

    def test_create_relationship(self):
        """Relationship creation."""
        rel = C4Relationship(
            source_id="node-1",
            target_id="node-2",
            relationship_type="flow-to",
            weight=3.0,
        )
        assert rel.source_id == "node-1"
        assert rel.target_id == "node-2"
        assert rel.weight == 3.0
        assert rel.is_circular is False

    def test_relationship_circular_flag(self):
        """Relationship with circular dependency flag."""
        rel = C4Relationship(
            source_id="node-1",
            target_id="node-2",
            relationship_type="trigger",
            weight=1.0,
            is_circular=True,
        )
        assert rel.is_circular is True
