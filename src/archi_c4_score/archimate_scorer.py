"""Architecture scoring for ArchiMate models."""

import logging
from collections import defaultdict
from dataclasses import dataclass

from archi_c4_score.models import (
    ArchimateElement,
    ArchimateModel,
    Relationship,
)

logger = logging.getLogger(__name__)


@dataclass
class ArchitectureMetrics:
    """Computed architecture metrics."""

    element_count: int
    relationship_count: int
    container_count: int
    component_count: int
    coupling: float
    modularity: float
    cohesion: float
    extensibility: float
    maintainability: float
    composite_score: float


class ArchimateScorer:
    """Calculate architecture scores from ArchiMate models."""

    CONTAINER_TYPES = {
        "Container",
        "application",
        "ApplicationContainer",
        "container",
    }
    COMPONENT_TYPES = {
        "Component",
        "applicationComponent",
        "ApplicationComponent",
        "component",
    }
    RELATIONSHIP_TYPES = {
        "Composition",
        "composition",
        "Aggregation",
        "aggregation",
        "Assignment",
        "assignment",
        "Realization",
        "realization",
        "Serving",
        "serving",
        "Dependency",
        "dependency",
    }

    def score_model(self, model: ArchimateModel) -> ArchitectureMetrics:
        """Calculate architecture metrics from a parsed model."""
        elements = model.elements
        relationships = model.relationships

        containers = self._filter_by_types(elements, self.CONTAINER_TYPES)
        components = self._filter_by_types(elements, self.COMPONENT_TYPES)

        coupling = self._calculate_coupling(relationships, containers, components)
        modularity = self._calculate_modularity(relationships, containers, components)
        cohesion = self._calculate_cohesion(relationships, components)
        extensibility = self._calculate_extensibility(relationships, elements)
        maintainability = self._calculate_maintainability(relationships, elements, components)

        composite = self._calculate_composite(
            coupling, modularity, cohesion, extensibility, maintainability
        )

        return ArchitectureMetrics(
            element_count=len(elements),
            relationship_count=len(relationships),
            container_count=len(containers),
            component_count=len(components),
            coupling=coupling,
            modularity=modularity,
            cohesion=cohesion,
            extensibility=extensibility,
            maintainability=maintainability,
            composite_score=composite,
        )

    def _filter_by_types(
        self, elements: list[ArchimateElement], types: set[str]
    ) -> list[ArchimateElement]:
        """Filter elements by type."""
        return [e for e in elements if e.element_type in types]

    def _calculate_coupling(
        self,
        relationships: list[Relationship],
        containers: list[ArchimateElement],
        components: list[ArchimateElement],
    ) -> float:
        """Calculate coupling score (0-100, higher is better).

        Coupling measures dependencies between containers/components.
        Only Flow (sync) and Triggering (async) relationships count.
        Flow = 1.5x weight, Triggering = 1.0x weight.
        """
        # Filter to only Flow and Triggering relationships
        relevant_rels = [
            r
            for r in relationships
            if getattr(r, "relationship_type", "") in ["Flow", "Triggering"]
            or getattr(r, "rel_type", "") in ["Flow", "Triggering"]
        ]

        if not relevant_rels:
            return 70.0  # No flow/triggering = default medium coupling

        all_nodes = {e.id for e in containers + components}
        if len(all_nodes) <= 1:
            return 70.0

        # Calculate weighted dependencies
        flow_count = sum(
            1
            for r in relevant_rels
            if getattr(r, "relationship_type", "") == "Flow" or getattr(r, "rel_type", "") == "Flow"
        )
        trigger_count = len(relevant_rels) - flow_count
        weighted_deps = (flow_count * 1.5) + (trigger_count * 1.0)

        # Map to 30-70 scale
        if weighted_deps <= 1:
            coupling = 30.0
        elif weighted_deps <= 3:
            coupling = 40.0
        elif weighted_deps <= 6:
            coupling = 50.0
        elif weighted_deps <= 10:
            coupling = 60.0
        else:
            coupling = 70.0

        return coupling

    def _calculate_modularity(
        self,
        relationships: list[Relationship],
        containers: list[ArchimateElement],
        components: list[ArchimateElement],
    ) -> float:
        """Calculate modularity score (0-100, higher is better).

        Modularity measures how well components are grouped into containers.
        """
        if not containers or not components:
            return 50.0

        container_ids = {c.id for c in containers}
        component_to_container = {}

        for rel in relationships:
            if rel.relationship_type in self.RELATIONSHIP_TYPES:
                if rel.source_id in container_ids:
                    component_to_container[rel.target_id] = rel.source_id
                elif rel.target_id in container_ids:
                    component_to_container[rel.source_id] = rel.target_id

        grouped = defaultdict(list)
        for comp_id, container_id in component_to_container.items():
            grouped[container_id].append(comp_id)

        if not grouped:
            return 50.0

        ideal_size = len(components) / len(containers) if containers else 1
        variance = sum(abs(len(comps) - ideal_size) for comps in grouped.values()) / len(containers)

        size_score = max(0, 100 - variance * 10)

        coverage = len(component_to_container) / len(components) * 100 if components else 0

        return size_score * 0.5 + coverage * 0.5

    def _calculate_cohesion(
        self, relationships: list[Relationship], components: list[ArchimateElement]
    ) -> float:
        """Calculate cohesion score (0-100, higher is better).

        Cohesion measures how related components within a container are.
        """
        if len(components) <= 1:
            return 100.0

        internal_rels = sum(
            1
            for rel in relationships
            if rel.source_id in {c.id for c in components}
            and rel.target_id in {c.id for c in components}
        )

        possible_rels = len(components) * (len(components) - 1) / 2
        density = internal_rels / possible_rels if possible_rels > 0 else 0

        return min(100.0, density * 100 + 20)

    def _calculate_extensibility(
        self,
        relationships: list[Relationship],
        elements: list[ArchimateElement],
    ) -> float:
        """Calculate extensibility score (0-100, higher is better).

        Extensibility measures how easy it is to add new components.
        Based on abstraction level and interface usage.
        """
        interfaces = sum(
            1 for e in elements if e.stereotype and "interface" in e.stereotype.lower()
        )
        abstractions = sum(
            1
            for e in elements
            if e.element_type
            and any(t in e.element_type.lower() for t in ["interface", "abstract", "trait"])
        )

        if not elements:
            return 50.0

        abstraction_ratio = (interfaces + abstractions) / len(elements)
        interface_score = min(100.0, abstraction_ratio * 500)

        return max(30.0, min(100.0, interface_score))

    def _calculate_maintainability(
        self,
        relationships: list[Relationship],
        elements: list[ArchimateElement],
        components: list[ArchimateElement],
    ) -> float:
        """Calculate maintainability score (0-100, higher is better).

        Based on complexity, component size, and dependency depth.
        """
        if not elements:
            return 0.0

        avg_components_per_container = (
            len(components) / len({r.source_id for r in relationships}) if components else 1
        )

        size_penalty = min(30, avg_components_per_container * 5)

        depth = self._calculate_dependency_depth(relationships, elements)
        depth_penalty = min(20, depth * 5)

        complexity_penalty = min(30, (len(relationships) / len(elements)) * 10)

        score = 100.0 - size_penalty - depth_penalty - complexity_penalty
        return max(0.0, min(100.0, score))

    def _calculate_composite(
        self,
        coupling: float,
        modularity: float,
        cohesion: float,
        extensibility: float,
        maintainability: float,
    ) -> float:
        """Calculate weighted composite score."""
        weights = {
            "coupling": 0.30,
            "modularity": 0.20,
            "cohesion": 0.15,
            "extensibility": 0.15,
            "maintainability": 0.20,
        }

        return (
            coupling * weights["coupling"]
            + modularity * weights["modularity"]
            + cohesion * weights["cohesion"]
            + extensibility * weights["extensibility"]
            + maintainability * weights["maintainability"]
        )

    def _build_dependency_graph(
        self, relationships: list[Relationship], node_ids: set[str]
    ) -> dict[str, set[str]]:
        """Build dependency graph from relationships."""
        deps: dict[str, set[str]] = defaultdict(set)

        for rel in relationships:
            if rel.relationship_type in ["Dependency", "dependency", "Serving", "serving"]:
                if rel.source_id in node_ids and rel.target_id in node_ids:
                    deps[rel.source_id].add(rel.target_id)

        return deps

    def _find_cycles(self, graph: dict[str, set[str]]) -> list[list[str]]:
        """Find cycles in dependency graph."""
        cycles = []
        visited: set[str] = set()
        stack: list[str] = []

        def dfs(node: str) -> bool:
            if node in stack:
                cycle_start = stack.index(node)
                cycles.append(stack[cycle_start:] + [node])
                return True

            if node in visited:
                return False

            visited.add(node)
            stack.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor in graph:
                    dfs(neighbor)

            stack.pop()
            return False

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def _calculate_dependency_depth(
        self, relationships: list[Relationship], elements: list[ArchimateElement]
    ) -> int:
        """Calculate maximum dependency depth."""
        deps = self._build_dependency_graph(relationships, {e.id for e in elements})

        if not deps:
            return 0

        def longest_path(node: str, visited: set[str]) -> int:
            if node in visited:
                return 0
            visited.add(node)

            max_child = 0
            for child in deps.get(node, set()):
                max_child = max(max_child, longest_path(child, visited.copy()))

            return 1 + max_child

        return max((longest_path(n, set()) for n in deps), default=0)
