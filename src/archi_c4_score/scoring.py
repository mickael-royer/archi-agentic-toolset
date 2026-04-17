"""Architecture scoring engine for C4 models."""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from archi_c4_score.archimate_scorer import ArchimateScorer, ArchitectureMetrics
from archi_c4_score.archimate_xml_parser import ArchimateXMLParser
from archi_c4_score.parser import CoArchi2Parser

if TYPE_CHECKING:
    from archi_c4_score.repository import Repository

logger = logging.getLogger(__name__)


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


class BackfillOrchestrator:
    """Orchestrate scoring of historical commits."""

    def __init__(
        self,
        scoring_engine: ScoringEngine,
        repository: "Repository",
    ) -> None:
        """Initialize backfill orchestrator."""
        self.scoring_engine = scoring_engine
        self.repository = repository

    def backfill(
        self,
        repository_url: str,
        commit_count: int = 30,
    ) -> list[dict[str, Any]]:
        """Backfill scoring for historical commits.

        Returns list of scored commits.
        """
        logger.info(f"Starting backfill for {commit_count} commits from {repository_url}")

        scored_commits = []
        commits = self.repository.get_commit_history(limit=commit_count)

        for commit in commits:
            sha = commit["sha"]
            try:
                self.repository.checkout_commit(sha)
                score_data = self._score_current_state(repository_url, commit)
                scored_commits.append(score_data)
                logger.info(f"Scored commit {sha[:7]}: {score_data.get('composite_score', 0):.1f}")
            except Exception as e:
                logger.warning(f"Failed to score commit {sha[:7]}: {e}")
                continue

        logger.info(f"Backfill complete: {len(scored_commits)} commits scored")
        return scored_commits

    def _score_current_state(
        self,
        repository_url: str,
        commit_info: dict[str, str],
    ) -> dict[str, Any]:
        """Score the current repository state.

        Returns scored commit data ready for persistence.
        """
        model_files = self.repository.find_model_files(pattern="*.archimate")
        logger.info(
            f"Found {len(model_files)} model files at commit {commit_info.get('sha', '?')[:7]}"
        )

        if not model_files:
            return {
                "id": str(uuid4()),
                "commit_sha": commit_info["sha"],
                "repository_url": repository_url,
                "commit_date": commit_info["date"],
                "author": commit_info["author"],
                "message": commit_info["message"],
                "composite_score": 0.0,
                "coupling_score": 0.0,
                "modularity_score": 0.0,
                "cohesion_score": 0.0,
                "extensibility_score": 0.0,
                "maintainability_score": 0.0,
                "element_count": 0,
                "relationship_count": 0,
                "scored_at": datetime.utcnow().isoformat(),
            }

        scorer = ArchimateScorer()
        xml_parser = ArchimateXMLParser()
        json_parser = CoArchi2Parser()
        all_metrics = []

        for model_file in model_files:
            try:
                if model_file.suffix.lower() == ".archimate":
                    model = xml_parser.parse_to_model(model_file)
                else:
                    model = json_parser.parse_file(model_file)
                metrics = scorer.score_model(model)
                all_metrics.append(metrics)
                logger.info(
                    f"Scored {model_file.name}: composite={metrics.composite_score:.1f}, "
                    f"coupling={metrics.coupling:.1f}, modularity={metrics.modularity:.1f}"
                )
            except Exception as e:
                logger.warning(f"Failed to score {model_file}: {e}")
                continue

        if not all_metrics:
            return {
                "id": str(uuid4()),
                "commit_sha": commit_info["sha"],
                "repository_url": repository_url,
                "commit_date": commit_info["date"],
                "author": commit_info["author"],
                "message": commit_info["message"],
                "composite_score": 0.0,
                "coupling_score": 0.0,
                "modularity_score": 0.0,
                "cohesion_score": 0.0,
                "extensibility_score": 0.0,
                "maintainability_score": 0.0,
                "element_count": 0,
                "relationship_count": 0,
                "scored_at": datetime.utcnow().isoformat(),
            }

        avg_metrics = self._average_metrics(all_metrics)

        return {
            "id": str(uuid4()),
            "commit_sha": commit_info["sha"],
            "repository_url": repository_url,
            "commit_date": commit_info["date"],
            "author": commit_info["author"],
            "message": commit_info["message"],
            "composite_score": avg_metrics.composite_score,
            "coupling_score": avg_metrics.coupling,
            "modularity_score": avg_metrics.modularity,
            "cohesion_score": avg_metrics.cohesion,
            "extensibility_score": avg_metrics.extensibility,
            "maintainability_score": avg_metrics.maintainability,
            "element_count": avg_metrics.element_count,
            "relationship_count": avg_metrics.relationship_count,
            "scored_at": datetime.utcnow().isoformat(),
        }

    def _average_metrics(self, metrics_list: list) -> ArchitectureMetrics:
        """Average multiple architecture metrics."""
        count = len(metrics_list)
        return ArchitectureMetrics(
            element_count=sum(m.element_count for m in metrics_list) // count,
            relationship_count=sum(m.relationship_count for m in metrics_list) // count,
            container_count=sum(m.container_count for m in metrics_list) // count,
            component_count=sum(m.component_count for m in metrics_list) // count,
            coupling=sum(m.coupling for m in metrics_list) / count,
            modularity=sum(m.modularity for m in metrics_list) / count,
            cohesion=sum(m.cohesion for m in metrics_list) / count,
            extensibility=sum(m.extensibility for m in metrics_list) / count,
            maintainability=sum(m.maintainability for m in metrics_list) / count,
            composite_score=sum(m.composite_score for m in metrics_list) / count,
        )
