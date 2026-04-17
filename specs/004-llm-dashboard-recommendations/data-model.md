# Data Model: LLM Dashboard Recommendations

## Entities

### Recommendation

An AI-generated suggestion based on trend analysis.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | Unique identifier (e.g., "REC-001") |
| `priority` | `Literal["HIGH", "MEDIUM", "LOW"]` | Yes | Priority level for the recommendation |
| `dimension` | `str` | No | Which scoring dimension this addresses (coupling, modularity, etc.) |
| `description` | `str` | Yes | The recommendation text in markdown format |
| `impact` | `str` | Yes | Expected impact description (qualitative) |
| `trend_refs` | `list[str]` | No | References to specific trends or commits that prompted this |

### TrendContext

The trend data provided to the LLM for generating recommendations.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repository_url` | `str` | Yes | URL of the repository |
| `repository_name` | `str` | Yes | Name of the repository |
| `date_range` | `DateRange` | Yes | Start and end dates of analysis period |
| `dimensions` | `list[TrendDimension]` | Yes | Trend data per scoring dimension |
| `significant_changes` | `list[SignificantChange]` | No | Commits with significant score changes |

### TrendDimension

Trend data for a single scoring dimension.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dimension` | `str` | Yes | Dimension name (coupling, modularity, cohesion, extensibility, maintainability) |
| `direction` | `Literal["INCREASING", "DECREASING", "STABLE"]` | Yes | Overall trend direction |
| `slope` | `float` | Yes | Rate of change per commit |
| `confidence` | `float` | Yes | Confidence score (0.0-1.0) |
| `current_value` | `float` | No | Current score value |
| `start_value` | `float` | No | Score at start of period |
| `affected_commits` | `list[str]` | No | Commit SHAs that contributed to trend |

### SignificantChange

A commit with significant score change.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `commit_sha` | `str` | Yes | Git commit SHA |
| `date` | `datetime` | Yes | Commit date |
| `magnitude` | `float` | Yes | Absolute score change |
| `direction` | `Literal["IMPROVING", "DEGRADING"]` | Yes | Whether score improved or degraded |
| `affected_dimensions` | `list[str]` | Yes | Dimensions affected by this change |

### RecommendationSet

A collection of recommendations with metadata.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `recommendations` | `list[Recommendation]` | Yes | Ordered list of recommendations |
| `llm_available` | `bool` | Yes | Whether LLM was successfully called |
| `generated_at` | `datetime` | Yes | Timestamp of generation |
| `model_used` | `str` | No | Gemini model used for generation |
| `error_message` | `str` | No | Error message if LLM unavailable |

### DateRange

Start and end dates for analysis.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start` | `datetime` | Yes | Start of analysis period |
| `end` | `datetime` | Yes | End of analysis period |

## Validation Rules

1. **RecommendationSet** MUST contain at most 5 recommendations (FR-001: token management)
2. **RecommendationSet** MUST be ordered by priority (HIGH → MEDIUM → LOW)
3. **TrendContext** MUST include at least one dimension
4. **Priority** values MUST be one of: HIGH, MEDIUM, LOW
5. **Direction** values MUST be one of: INCREASING, DECREASING, STABLE

## State Transitions

```
TrendContext (from Neo4j + TimelineService)
         │
         ▼
  GeminiClient.generate_recommendations()
         │
    ┌────┴────┐
    │         │
 Success    Failure
    │         │
    ▼         ▼
RecommendationSet    RecommendationSet
(llm_available=True) (llm_available=False)
    │
    ▼
DashboardResponse + Hugo Export
```

## API Models

### DashboardResponse (extended)

```python
class DashboardResponse(BaseModel):
    generated_at: str
    repository: dict
    summary: dict
    commits: list[dict]
    trends: list[dict]
    concerns: list[dict]
    recommendations: RecommendationSet  # NEW FIELD
```

### RecommendationSet (API)

```python
class RecommendationSetResponse(BaseModel):
    recommendations: list[RecommendationResponse]
    llm_available: bool
    generated_at: str
    error_message: str | None = None

class RecommendationResponse(BaseModel):
    id: str
    priority: str
    dimension: str | None = None
    description: str
    impact: str
    trend_refs: list[str] = []
```

## Hugo Export Format

```json
{
  "recommendations": {
    "llm_available": true,
    "generated_at": "2026-04-16T10:00:00Z",
    "items": [
      {
        "id": "REC-001",
        "priority": "HIGH",
        "dimension": "Coupling",
        "description": "Reduce cyclic dependencies between containers",
        "impact": "High - addresses root cause of declining modularity",
        "trend_refs": ["abc123", "def456"]
      }
    ]
  }
}
```
