# Quickstart: LLM Dashboard Recommendations

Generate AI-powered recommendations based on architecture score trends.

## Prerequisites

- Python 3.12+
- Neo4j database with scored commit history
- Google Gemini API key (set `GEMINI_API_KEY` environment variable)

## Installation

```bash
uv add google-genai cachetools
```

## Usage

### CLI

```bash
# Generate dashboard with recommendations
uv run archi-c4-score dashboard \
  --repository-url https://github.com/owner/repo \
  --include-recommendations

# Output includes:
# - Recommendations section with priority-ordered suggestions
# - LLM availability status
```

### API

```bash
# Get dashboard with recommendations
curl "http://localhost:8000/api/v1/dashboard?repository_url=https://github.com/owner/repo"
```

Response:
```json
{
  "generated_at": "2026-04-16T10:00:00Z",
  "repository": {
    "url": "https://github.com/owner/repo",
    "name": "repo"
  },
  "recommendations": {
    "recommendations": [
      {
        "id": "REC-001",
        "priority": "HIGH",
        "dimension": "Coupling",
        "description": "Reduce cyclic dependencies between containers...",
        "impact": "High - addresses root cause of declining modularity",
        "trend_refs": ["abc123", "def456"]
      }
    ],
    "llm_available": true,
    "generated_at": "2026-04-16T10:00:00Z"
  }
}
```

### Python Library

```python
from archi_c4_score.llm_service import GeminiClient, TrendContext

# Build trend context
context = TrendContext(
    repository_url="https://github.com/owner/repo",
    repository_name="repo",
    date_range={"start": "2026-04-01", "end": "2026-04-16"},
    dimensions=[
        {
            "dimension": "coupling",
            "direction": "DECREASING",
            "slope": -0.5,
            "confidence": 0.85,
            "current_value": 45.0,
            "start_value": 60.0
        }
    ],
    significant_changes=[]
)

# Generate recommendations
client = GeminiClient()
recommendations = client.generate_recommendations(context)

print(f"Generated {len(recommendations.recommendations)} recommendations")
print(f"LLM available: {recommendations.llm_available}")
```

## Hugo Export

Recommendations are automatically included in Hugo export:

```python
from archi_c4_score.hugo_export import DashboardGenerator

generator = DashboardGenerator()
data = generator.generate(
    repository_url="https://github.com/owner/repo",
    commits=[...],
    trends=[...],
    health_status="DECLINING",
    significant_changes=[...],
    recommendations=recommendations  # NEW
)
```

Output at `output/data/timeline.json`:
```json
{
  "recommendations": {
    "llm_available": true,
    "generated_at": "2026-04-16T10:00:00Z",
    "items": [...]
  }
}
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `GEMINI_API_KEY` | required | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Model to use |
| `LLM_CACHE_TTL` | `3600` | Cache TTL in seconds |

## Fallback Behavior

When LLM is unavailable, recommendations return with `llm_available: false`:

```json
{
  "recommendations": {
    "recommendations": [],
    "llm_available": false,
    "generated_at": "2026-04-16T10:00:00Z",
    "error_message": "Rate limit exceeded"
  }
}
```

Dashboard generation continues normally without recommendations.

## Error Handling

| Error | Behavior |
|-------|----------|
| Invalid API key | Log error, return empty recommendations |
| Rate limited | Retry with exponential backoff (max 3 attempts) |
| Server error | Retry with backoff (max 3 attempts) |
| Timeout | Return empty recommendations after 5 seconds |
