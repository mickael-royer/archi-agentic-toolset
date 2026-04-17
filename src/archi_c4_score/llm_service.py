"""LLM recommendation service using Google Gemini API."""

import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import Any

from cachetools import TTLCache

from archi_c4_score.recommendation_models.recommendations import (
    Priority,
    Recommendation,
    RecommendationSet,
    TrendContext,
)

logger = logging.getLogger(__name__)

GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
DEFAULT_MODEL = "gemini-2.5-flash"
MAX_RECOMMENDATIONS = 5
CACHE_SIZE = 100
CACHE_TTL_SECONDS = int(os.environ.get("LLM_CACHE_TTL", "3600"))


class GeminiClient:
    """Client for generating architecture recommendations using Google Gemini API."""

    SYSTEM_PROMPT = """You are an expert software architect analyzing architecture score trends.

Your task is to generate actionable recommendations based on the provided trend data.

## Scoring Dimensions
- coupling: Measures dependencies between components (lower is better)
- modularity: Measures separation of concerns (higher is better)
- cohesion: Measures how related elements are within components (higher is better)
- extensibility: Measures ease of adding new features (higher is better)
- maintainability: Measures ease of maintenance (higher is better)

## Trend Directions
- INCREASING: Score is improving (good for most dimensions, but coupling should decrease)
- DECREASING: Score is declining (bad for most dimensions, but may be good for coupling)
- STABLE: Score is not changing significantly

## Instructions
1. Generate up to 5 specific, actionable recommendations
2. Each recommendation MUST include:
   - priority: HIGH/MEDIUM/LOW based on severity
   - dimension: Which scoring dimension this addresses
   - description: Specific action to take (markdown format)
   - impact: Expected improvement description
   - trend_refs: References to commits causing the issue
3. Order recommendations by priority (HIGH first)
4. For improving trends, acknowledge positive progress and suggest maintaining good practices
5. For declining trends, provide specific remediation steps

Return recommendations that are practical and tied to the observed trends."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = DEFAULT_MODEL,
    ) -> None:
        """Initialize Gemini client.

        Args:
            api_key: Google Gemini API key. If not provided, reads from GEMINI_API_KEY env.
            model_name: Gemini model to use. Defaults to gemini-2.0-flash.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.environ.get(GEMINI_API_KEY_ENV)
        if not self.api_key:
            raise ValueError(f"{GEMINI_API_KEY_ENV} environment variable is required")

        self.model_name = model_name
        self._cache: TTLCache[str, RecommendationSet] = TTLCache(
            maxsize=CACHE_SIZE, ttl=CACHE_TTL_SECONDS
        )

        self._client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Gemini API client."""
        try:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
            logger.info(f"Initialized Gemini client with model: {self.model_name}")
        except ImportError:
            logger.warning("google-genai package not installed")
            self._client = None

    def _generate_cache_key(self, context: TrendContext) -> str:
        """Generate cache key from trend context.

        Args:
            context: The trend context to generate key for.

        Returns:
            A hash-based cache key.
        """
        date_range_str = (
            f"{context.date_range.start.isoformat()}-{context.date_range.end.isoformat()}"
        )
        key_data = f"{context.repository_url}:{date_range_str}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

    def _build_user_prompt(self, context: TrendContext) -> str:
        """Build the user prompt with trend context.

        Args:
            context: The trend context with all dimension and change data.

        Returns:
            Formatted user prompt string.
        """
        dims_text = []
        for dim in context.dimensions:
            coupling_note = (
                " (decreasing is good)"
                if dim.dimension.value == "coupling"
                else " (increasing is good)"
            )
            dim_text = f"- {dim.dimension.value}: {dim.direction.value}{coupling_note} (slope: {dim.slope:.2f}, confidence: {dim.confidence:.0%})"
            if dim.affected_commits:
                dim_text += f", affected commits: {', '.join(dim.affected_commits)}"
            dims_text.append(dim_text)

        changes_text = ""
        if context.significant_changes:
            changes_lines = []
            for change in context.significant_changes:
                changes_lines.append(
                    f"- {change.commit_sha[:7]} ({change.date.strftime('%Y-%m-%d')}): "
                    f"{change.direction.value} by {change.magnitude:.1f} points, "
                    f"affecting: {', '.join(change.affected_dimensions)}"
                )
            changes_text = "\n\n## Significant Changes\n" + "\n".join(changes_lines)

        return f"""## Repository
{context.repository_name} ({context.repository_url})

## Analysis Period
{context.date_range.start.strftime("%Y-%m-%d")} to {context.date_range.end.strftime("%Y-%m-%d")}

## Trend Analysis
{chr(10).join(dims_text)}{changes_text}

Generate recommendations to improve the architecture based on these trends."""

    def _call_gemini_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 3,
    ) -> list[dict[str, Any]]:
        """Call Gemini API with retry logic.

        Args:
            system_prompt: The system prompt.
            user_prompt: The user prompt with context.
            max_retries: Maximum retry attempts.

        Returns:
            List of recommendation dictionaries from Gemini.

        Raises:
            Exception: If all retries fail.
        """
        if not self._client:
            raise Exception("Gemini client not initialized")

        try:
            from google.genai import types

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                ),
            )

            return self._parse_response(response)

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise

    def _parse_response(self, response: Any) -> list[dict[str, Any]]:
        """Parse Gemini response into recommendations.

        Args:
            response: The raw Gemini response.

        Returns:
            List of recommendation dictionaries.
        """
        recommendations = []

        try:
            text = response.text
            if not text:
                return []

            import json

            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                data = json.loads(json_str)
                if "recommendations" in data:
                    recommendations = data["recommendations"]
                elif isinstance(data, list):
                    recommendations = data

        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse Gemini response: {e}")

        return recommendations[:MAX_RECOMMENDATIONS]

    def _format_recommendations(
        self,
        raw_recommendations: list[dict[str, Any]],
    ) -> list[Recommendation]:
        """Format raw recommendations into Recommendation models.

        Args:
            raw_recommendations: List of recommendation dicts from LLM.

        Returns:
            List of Recommendation models sorted by priority.
        """
        recommendations = []
        for i, raw in enumerate(raw_recommendations[:MAX_RECOMMENDATIONS]):
            try:
                rec = Recommendation(
                    id=raw.get("id", f"REC-{i + 1:03d}"),
                    priority=Priority(raw.get("priority", "MEDIUM")),
                    dimension=raw.get("dimension"),
                    description=raw.get("description", ""),
                    impact=raw.get("impact", ""),
                    trend_refs=raw.get("trend_refs", []),
                )
                recommendations.append(rec)
            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to format recommendation: {e}")

        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(recommendations, key=lambda r: priority_order.get(r.priority, 1))

    def generate_recommendations(
        self,
        context: TrendContext,
    ) -> RecommendationSet:
        """Generate recommendations based on trend context.

        Args:
            context: The trend context with dimension and change data.

        Returns:
            RecommendationSet with generated recommendations or empty on failure.
        """
        cache_key = self._generate_cache_key(context)
        cached = self._cache.get(cache_key)
        if cached:
            logger.info(f"Using cached recommendations for key: {cache_key}")
            return cached

        try:
            system_prompt = self.SYSTEM_PROMPT
            user_prompt = self._build_user_prompt(context)

            raw_recommendations = self._call_gemini_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            recommendations = self._format_recommendations(raw_recommendations)

            result = RecommendationSet(
                recommendations=recommendations,
                llm_available=True,
                generated_at=datetime.now(timezone.utc),
                model_used=self.model_name,
            )

            self._cache[cache_key] = result
            logger.info(f"Generated {len(recommendations)} recommendations")

            return result

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return RecommendationSet(
                recommendations=[],
                llm_available=False,
                generated_at=datetime.now(timezone.utc),
                error_message=str(e),
            )
