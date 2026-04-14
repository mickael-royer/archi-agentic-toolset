"""Unit tests for C4 mapper."""

from archi_c4_score.mapper import C4Mapper
from archi_c4_score.models import (
    ArchimateElement,
    C4Level,
    Relationship,
)


class TestC4Mapper:
    """Tests for C4 level mapping."""

    def test_map_system_stereotype(self):
        """<<Software System>> maps to System level."""
        element = ArchimateElement(
            id="elem-1",
            name="E-Commerce Platform",
            element_type="ApplicationComponent",
            stereotype="<<Software System>>",
        )
        mapper = C4Mapper()
        node = mapper.map_element(element)
        assert node.c4_level == C4Level.SYSTEM
        assert node.name == "E-Commerce Platform"

    def test_map_container_stereotype(self):
        """<<Container>> maps to Container level."""
        element = ArchimateElement(
            id="elem-1",
            name="API Gateway",
            element_type="ApplicationComponent",
            stereotype="<<Container>>",
        )
        mapper = C4Mapper()
        node = mapper.map_element(element)
        assert node.c4_level == C4Level.CONTAINER
        assert node.name == "API Gateway"

    def test_map_component_stereotype(self):
        """<<Component>> maps to Component level."""
        element = ArchimateElement(
            id="elem-1",
            name="Auth Module",
            element_type="ApplicationComponent",
            stereotype="<<Component>>",
        )
        mapper = C4Mapper()
        node = mapper.map_element(element)
        assert node.c4_level == C4Level.COMPONENT
        assert node.name == "Auth Module"

    def test_default_to_component(self):
        """No stereotype defaults to Component level."""
        element = ArchimateElement(
            id="elem-1",
            name="Unknown Module",
            element_type="ApplicationComponent",
        )
        mapper = C4Mapper()
        node = mapper.map_element(element)
        assert node.c4_level == C4Level.COMPONENT

    def test_map_model(self):
        """Map full model to C4 nodes."""
        elements = [
            ArchimateElement(
                id="sys-1",
                name="System",
                element_type="ApplicationComponent",
                stereotype="<<Software System>>",
            ),
            ArchimateElement(
                id="cont-1",
                name="Container",
                element_type="ApplicationComponent",
                stereotype="<<Container>>",
            ),
        ]
        relationships = [
            Relationship(
                id="rel-1",
                relationship_type="flow-to",
                source_id="cont-1",
                target_id="cont-1",
            ),
        ]
        mapper = C4Mapper()
        nodes, rels = mapper.map_model(elements, relationships)
        assert len(nodes) == 2
        assert len(rels) == 1


class TestMapperWarnings:
    """Tests for mapper warning handling."""

    def test_skip_unknown_stereotype(self):
        """Unknown stereotypes are skipped with warning."""
        element = ArchimateElement(
            id="elem-1",
            name="Unknown",
            element_type="ApplicationComponent",
            stereotype="<<Unknown>>",
        )
        mapper = C4Mapper()
        node = mapper.map_element(element)
        assert node is None
        assert len(mapper.warnings) == 1
        assert "Unknown" in str(mapper.warnings[0])


class TestDependencyWeights:
    """Tests for relationship weight assignment."""

    def test_flow_to_weight(self):
        """flow-to gets weight 3 (synchronous)."""
        mapper = C4Mapper()
        weight = mapper.DEPENDENCY_WEIGHTS.get("flow-to", mapper.DEFAULT_WEIGHT)
        assert weight == 3.0

    def test_trigger_weight(self):
        """trigger gets weight 1 (asynchronous)."""
        mapper = C4Mapper()
        weight = mapper.DEPENDENCY_WEIGHTS.get("trigger", mapper.DEFAULT_WEIGHT)
        assert weight == 1.0

    def test_other_weight(self):
        """Other relationship types get default weight."""
        mapper = C4Mapper()
        weight = mapper.DEPENDENCY_WEIGHTS.get("serving", mapper.DEFAULT_WEIGHT)
        assert weight == 1.5
