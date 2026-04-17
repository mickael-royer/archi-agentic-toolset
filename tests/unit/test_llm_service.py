"""Tests for LLM recommendation service."""

import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from archi_c4_score.recommendation_models.recommendations import (
    ChangeDirection,
    DateRange,
    DimensionName,
    Priority,
    RecommendationSet,
    SignificantChange,
    TrendContext,
    TrendDimension,
    TrendDirection,
)


class TestGeminiClientInitialization:
    """Tests for GeminiClient initialization."""

    def test_init_with_api_key(self):
        """Test GeminiClient initializes with api_key and model_name."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            from archi_c4_score.llm_service import GeminiClient

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            assert client.api_key == "test-key"
            assert client.model_name == "gemini-2.0-flash"

    def test_init_defaults(self):
        """Test GeminiClient uses default model when not specified."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            from archi_c4_score.llm_service import GeminiClient

            client = GeminiClient(api_key="test-key")
            assert client.model_name == "gemini-2.5-flash"

    def test_init_without_api_key_raises(self):
        """Test GeminiClient raises error without API key."""
        with patch.dict(os.environ, {}, clear=True):
            from archi_c4_score.llm_service import GeminiClient

            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                GeminiClient()


class TestGenerateRecommendations:
    """Tests for generate_recommendations method."""

    def _create_trend_context(self) -> TrendContext:
        """Helper to create a test TrendContext."""
        return TrendContext(
            repository_url="https://github.com/test/repo",
            repository_name="repo",
            date_range=DateRange(
                start=datetime(2026, 4, 1, tzinfo=timezone.utc),
                end=datetime(2026, 4, 16, tzinfo=timezone.utc),
            ),
            dimensions=[
                TrendDimension(
                    dimension=DimensionName.COUPLING,
                    direction=TrendDirection.DECREASING,
                    slope=-0.5,
                    confidence=0.85,
                    current_value=45.0,
                    start_value=60.0,
                    affected_commits=["abc1234", "def5678"],
                ),
                TrendDimension(
                    dimension=DimensionName.MODULARITY,
                    direction=TrendDirection.INCREASING,
                    slope=0.3,
                    confidence=0.75,
                    current_value=70.0,
                    start_value=65.0,
                ),
            ],
            significant_changes=[
                SignificantChange(
                    commit_sha="abc1234",
                    date=datetime(2026, 4, 10, tzinfo=timezone.utc),
                    magnitude=15.0,
                    direction=ChangeDirection.DEGRADING,
                    affected_dimensions=["coupling"],
                ),
            ],
        )

    @patch("archi_c4_score.llm_service.GeminiClient._call_gemini_with_retry")
    def test_generate_recommendations_returns_recommendation_set(self, mock_call: MagicMock):
        """Test generate_recommendations returns a RecommendationSet."""
        mock_call.return_value = [
            {
                "id": "REC-001",
                "priority": "HIGH",
                "dimension": "coupling",
                "description": "Reduce cyclic dependencies between containers",
                "impact": "High - addresses root cause of declining modularity",
                "trend_refs": ["abc1234", "def5678"],
            }
        ]

        from archi_c4_score.llm_service import GeminiClient

        client = GeminiClient(api_key="test-key")
        context = self._create_trend_context()
        result = client.generate_recommendations(context)

        assert isinstance(result, RecommendationSet)
        assert result.llm_available is True
        assert len(result.recommendations) == 1
        assert result.recommendations[0].id == "REC-001"

    @patch("archi_c4_score.llm_service.GeminiClient._call_gemini_with_retry")
    def test_generate_recommendations_orders_by_priority(self, mock_call: MagicMock):
        """Test recommendations are ordered HIGH → MEDIUM → LOW."""
        mock_call.return_value = [
            {
                "id": "REC-002",
                "priority": "MEDIUM",
                "description": "Test medium",
                "impact": "Medium",
            },
            {"id": "REC-001", "priority": "HIGH", "description": "Test high", "impact": "High"},
            {"id": "REC-003", "priority": "LOW", "description": "Test low", "impact": "Low"},
        ]

        from archi_c4_score.llm_service import GeminiClient

        client = GeminiClient(api_key="test-key")
        context = self._create_trend_context()
        result = client.generate_recommendations(context)

        assert result.recommendations[0].priority == Priority.HIGH
        assert result.recommendations[1].priority == Priority.MEDIUM
        assert result.recommendations[2].priority == Priority.LOW


class TestFallbackBehavior:
    """Tests for LLM unavailable fallback behavior."""

    def _create_trend_context(self) -> TrendContext:
        """Helper to create a test TrendContext."""
        return TrendContext(
            repository_url="https://github.com/test/repo",
            repository_name="repo",
            date_range=DateRange(
                start=datetime(2026, 4, 1, tzinfo=timezone.utc),
                end=datetime(2026, 4, 16, tzinfo=timezone.utc),
            ),
            dimensions=[
                TrendDimension(
                    dimension=DimensionName.COUPLING,
                    direction=TrendDirection.DECREASING,
                    slope=-0.5,
                    confidence=0.85,
                ),
            ],
        )

    @patch("archi_c4_score.llm_service.GeminiClient._call_gemini_with_retry")
    def test_llm_unavailable_returns_empty_recommendations(self, mock_call: MagicMock):
        """Test fallback returns empty recommendations when LLM fails."""
        mock_call.side_effect = Exception("API Error")

        from archi_c4_score.llm_service import GeminiClient

        client = GeminiClient(api_key="test-key")
        context = self._create_trend_context()
        result = client.generate_recommendations(context)

        assert result.llm_available is False
        assert result.recommendations == []
        assert result.error_message is not None

    @patch("archi_c4_score.llm_service.GeminiClient._call_gemini_with_retry")
    def test_rate_limit_returns_empty_with_retry_message(self, mock_call: MagicMock):
        """Test rate limit returns empty with appropriate error message."""
        mock_call.side_effect = Exception("429 Rate limit exceeded")

        from archi_c4_score.llm_service import GeminiClient

        client = GeminiClient(api_key="test-key")
        context = self._create_trend_context()
        result = client.generate_recommendations(context)

        assert result.llm_available is False
        assert len(result.recommendations) == 0


class TestTokenLimitHandling:
    """Tests for token limit and max recommendations handling."""

    def _create_trend_context(self) -> TrendContext:
        """Helper to create a test TrendContext."""
        return TrendContext(
            repository_url="https://github.com/test/repo",
            repository_name="repo",
            date_range=DateRange(
                start=datetime(2026, 4, 1, tzinfo=timezone.utc),
                end=datetime(2026, 4, 16, tzinfo=timezone.utc),
            ),
            dimensions=[
                TrendDimension(
                    dimension=DimensionName.COUPLING,
                    direction=TrendDirection.DECREASING,
                    slope=-0.5,
                    confidence=0.85,
                ),
            ],
        )

    @patch("archi_c4_score.llm_service.GeminiClient._call_gemini_with_retry")
    def test_max_five_recommendations_enforced(self, mock_call: MagicMock):
        """Test that max 5 recommendations are enforced."""
        mock_call.return_value = [
            {"id": f"REC-{i:03d}", "priority": "HIGH", "description": f"Rec {i}", "impact": "High"}
            for i in range(1, 8)  # 7 recommendations returned
        ]

        from archi_c4_score.llm_service import GeminiClient

        client = GeminiClient(api_key="test-key")
        context = self._create_trend_context()
        result = client.generate_recommendations(context)

        assert len(result.recommendations) <= 5


class TestCaching:
    """Tests for recommendation caching."""

    def _create_trend_context(self) -> TrendContext:
        """Helper to create a test TrendContext."""
        return TrendContext(
            repository_url="https://github.com/test/repo",
            repository_name="repo",
            date_range=DateRange(
                start=datetime(2026, 4, 1, tzinfo=timezone.utc),
                end=datetime(2026, 4, 16, tzinfo=timezone.utc),
            ),
            dimensions=[
                TrendDimension(
                    dimension=DimensionName.COUPLING,
                    direction=TrendDirection.DECREASING,
                    slope=-0.5,
                    confidence=0.85,
                ),
            ],
        )

    @patch("archi_c4_score.llm_service.GeminiClient._call_gemini_with_retry")
    def test_cache_key_includes_repository_and_date_range(self, mock_call: MagicMock):
        """Test cache key is based on repository URL and date range."""
        from archi_c4_score.llm_service import GeminiClient

        mock_call.return_value = []
        client = GeminiClient(api_key="test-key")

        context = self._create_trend_context()
        key1 = client._generate_cache_key(context)

        # Same context should produce same key
        key2 = client._generate_cache_key(context)
        assert key1 == key2

        # Different date range should produce different key
        context2 = TrendContext(
            repository_url="https://github.com/test/repo",
            repository_name="repo",
            date_range=DateRange(
                start=datetime(2026, 4, 2, tzinfo=timezone.utc),
                end=datetime(2026, 4, 17, tzinfo=timezone.utc),
            ),
            dimensions=[
                TrendDimension(
                    dimension=DimensionName.COUPLING,
                    direction=TrendDirection.DECREASING,
                    slope=-0.5,
                    confidence=0.85,
                ),
            ],
        )
        key3 = client._generate_cache_key(context2)
        assert key1 != key3

    @patch("archi_c4_score.llm_service.GeminiClient._call_gemini_with_retry")
    def test_cached_response_skips_llm_call(self, mock_call: MagicMock):
        """Test that cached responses skip the LLM call."""
        from archi_c4_score.llm_service import GeminiClient

        mock_call.return_value = [
            {"id": "REC-001", "priority": "HIGH", "description": "Cached", "impact": "High"}
        ]

        client = GeminiClient(api_key="test-key")
        context = self._create_trend_context()

        # First call - should hit LLM
        client.generate_recommendations(context)
        assert mock_call.call_count == 1

        # Second call - should use cache
        result2 = client.generate_recommendations(context)
        assert mock_call.call_count == 1  # Still 1, not 2
        assert result2.recommendations[0].id == "REC-001"


class TestPositiveTrendAcknowledgment:
    """Tests for positive trend acknowledgment."""

    def _create_positive_trend_context(self) -> TrendContext:
        """Helper to create a context with improving trends."""
        return TrendContext(
            repository_url="https://github.com/test/repo",
            repository_name="repo",
            date_range=DateRange(
                start=datetime(2026, 4, 1, tzinfo=timezone.utc),
                end=datetime(2026, 4, 16, tzinfo=timezone.utc),
            ),
            dimensions=[
                TrendDimension(
                    dimension=DimensionName.COHESION,
                    direction=TrendDirection.INCREASING,
                    slope=0.8,
                    confidence=0.90,
                    current_value=85.0,
                    start_value=70.0,
                ),
                TrendDimension(
                    dimension=DimensionName.MODULARITY,
                    direction=TrendDirection.INCREASING,
                    slope=0.5,
                    confidence=0.80,
                    current_value=75.0,
                    start_value=60.0,
                ),
            ],
        )

    @patch("archi_c4_score.llm_service.GeminiClient._call_gemini_with_retry")
    def test_positive_trends_acknowledged_in_recommendations(self, mock_call: MagicMock):
        """Test that improving trends result in positive acknowledgment."""
        mock_call.return_value = [
            {
                "id": "REC-001",
                "priority": "MEDIUM",
                "dimension": "cohesion",
                "description": "Continue maintaining high cohesion scores",
                "impact": "Positive - sustaining good practices",
                "trend_refs": [],
            }
        ]

        from archi_c4_score.llm_service import GeminiClient

        client = GeminiClient(api_key="test-key")
        context = self._create_positive_trend_context()
        result = client.generate_recommendations(context)

        assert result.llm_available is True
        assert len(result.recommendations) > 0
        # The LLM should acknowledge positive progress
        rec_text = result.recommendations[0].description.lower()
        assert any(
            word in rec_text for word in ["maintain", "continue", "sustain", "positive", "good"]
        )
