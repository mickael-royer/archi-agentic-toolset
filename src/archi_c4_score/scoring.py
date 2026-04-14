"""Architecture scoring engine for C4 models."""


class InstabilityCalculator:
    """Calculate instability index for a component."""

    def calculate(self, ce: int, ca: int) -> float:
        """Calculate instability: I = Ce / (Ca + Ce).

        Args:
            ce: Efferent coupling (outgoing dependencies)
            ca: Afferent coupling (incoming dependencies)
        """
        total = ce + ca
        if total == 0:
            return 0.0
        return ce / total


class ScoringEngine:
    """Calculate architecture scores for C4 models."""

    DEFAULT_WEIGHT = 1.0
    CYCLE_PENALTY_FACTOR = 0.1

    def score_dimension(self, value: float, max_value: float = 100.0) -> float:
        """Score a dimension as percentage (0-100)."""
        if max_value <= 0:
            return 0.0
        return min(100.0, max(0.0, (value / max_value) * 100))

    def apply_weight(self, score: float, weight: float) -> float:
        """Apply weight to a score."""
        return score * weight

    def aggregate_scores(self, scores: list[float]) -> float:
        """Aggregate multiple scores into an average."""
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    def detect_cycle(self, edges: list[tuple[str, str]]) -> bool:
        """Detect if graph has cycles using DFS.

        Args:
            edges: List of (source, target) tuples
        """
        graph: dict[str, list[str]] = {}
        for source, target in edges:
            graph.setdefault(source, []).append(target)

        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def apply_cycle_penalty(self, base_score: float, cycle_count: int = 1) -> float:
        """Apply complexity penalty for cycles."""
        penalty = cycle_count * self.CYCLE_PENALTY_FACTOR
        return max(0.0, base_score * (1 - penalty))


class RecommendationGenerator:
    """Generate actionable improvement recommendations."""

    def generate(self, instability: float) -> list:
        """Generate recommendations based on metrics.

        Args:
            instability: Component instability index (0-1)
        """
        from dataclasses import dataclass

        @dataclass
        class Recommendation:
            id: str
            priority: str
            dimension: str
            target_node_id: str
            description: str
            rationale: str

        recs = []
        if instability > 0.8:
            recs.append(
                Recommendation(
                    id="REC-001",
                    priority="HIGH",
                    dimension="Coupling",
                    target_node_id="current",
                    description="Reduce efferent dependencies",
                    rationale=f"Instability of {instability:.2f} is very high",
                )
            )
        elif instability > 0.5:
            recs.append(
                Recommendation(
                    id="REC-002",
                    priority="MEDIUM",
                    dimension="Coupling",
                    target_node_id="current",
                    description="Monitor dependency growth",
                    rationale=f"Instability of {instability:.2f} is moderate",
                )
            )
        return recs
