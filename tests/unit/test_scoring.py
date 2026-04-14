"""Unit tests for scoring engine."""

import pytest
from archi_c4_score.scoring import ScoringEngine, InstabilityCalculator


class TestInstabilityCalculator:
    """Tests for instability index calculation."""

    def test_instability_with_dependencies(self):
        """Instability = Ce / (Ca + Ce)."""
        calc = InstabilityCalculator()
        instability = calc.calculate(ce=3, ca=2)
        assert instability == pytest.approx(0.6)

    def test_instability_zero_dependencies(self):
        """No dependencies means instability = 0."""
        calc = InstabilityCalculator()
        instability = calc.calculate(ce=0, ca=5)
        assert instability == 0.0

    def test_instability_all_outgoing(self):
        """All outgoing = instability = 1."""
        calc = InstabilityCalculator()
        instability = calc.calculate(ce=5, ca=0)
        assert instability == 1.0

    def test_instability_no_coupling(self):
        """No coupling at all = 0."""
        calc = InstabilityCalculator()
        instability = calc.calculate(ce=0, ca=0)
        assert instability == 0.0


class TestScoringEngine:
    """Tests for the scoring engine."""

    def test_dimension_scoring(self):
        """Dimensions are scored 0-100."""
        engine = ScoringEngine()
        score = engine.score_dimension(value=75, max_value=100)
        assert 0 <= score <= 100

    def test_apply_weight(self):
        """Weights modify scores correctly."""
        engine = ScoringEngine()
        result = engine.apply_weight(score=50, weight=2.0)
        assert result == 100.0

    def test_aggregate_scores(self):
        """Scores aggregate correctly."""
        engine = ScoringEngine()
        scores = [80, 60, 100]
        avg = engine.aggregate_scores(scores)
        assert avg == pytest.approx(80.0)


class TestCircularDependencyPenalty:
    """Tests for cycle detection penalties."""

    def test_cycle_detection(self):
        """Cycles are detected correctly."""
        engine = ScoringEngine()
        edges = [
            ("A", "B"),
            ("B", "C"),
            ("C", "A"),
        ]
        has_cycle = engine.detect_cycle(edges)
        assert has_cycle is True

    def test_no_cycle(self):
        """Linear graph has no cycle."""
        engine = ScoringEngine()
        edges = [
            ("A", "B"),
            ("B", "C"),
            ("C", "D"),
        ]
        has_cycle = engine.detect_cycle(edges)
        assert has_cycle is False

    def test_penalty_application(self):
        """Cycles apply a complexity penalty."""
        engine = ScoringEngine()
        base_score = 100
        penalized = engine.apply_cycle_penalty(base_score, cycle_count=2)
        assert penalized < base_score


class TestRecommendations:
    """Tests for recommendation generation."""

    def test_recommendation_priorities(self):
        """Recommendations have priority levels."""
        from archi_c4_score.scoring import RecommendationGenerator

        gen = RecommendationGenerator()
        recs = gen.generate(instability=0.9)
        assert len(recs) > 0
        assert all(r.priority in ("HIGH", "MEDIUM", "LOW") for r in recs)

    def test_high_instability_warning(self):
        """High instability generates warning."""
        from archi_c4_score.scoring import RecommendationGenerator

        gen = RecommendationGenerator()
        recs = gen.generate(instability=0.9)
        high_priority = [r for r in recs if r.priority == "HIGH"]
        assert len(high_priority) > 0

    def test_recommendation_has_dimensions(self):
        """Recommendations include dimension info."""
        from archi_c4_score.scoring import RecommendationGenerator

        gen = RecommendationGenerator()
        recs = gen.generate(instability=0.9)
        assert all(r.dimension for r in recs)
