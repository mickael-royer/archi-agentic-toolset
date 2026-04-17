# Research: LLM Dashboard Recommendations

## Decision: Google Gemini 2.0 API for Recommendations

### Rationale

- User requirement specified Google Gemini 2.0 API
- Supports function calling for structured JSON output (reliable parsing)
- High token limits (1M input, 64K output) suitable for trend context
- Cost-effective for recommendation generation use case

### Alternatives Considered

- **Azure OpenAI GPT-4o**: More mature but user explicitly selected Gemini
- **Anthropic Claude**: Strong reasoning but not selected
- **Local models**: Too resource-intensive for container deployment

## Gemini API Integration Patterns

### Function Calling (Tools)

Gemini 2.0 uses a tool-based approach for structured output:

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

recommendation_tool = {
    "name": "generate_recommendations",
    "description": "Generate architecture improvement recommendations based on trends",
    "parameters": {
        "type": "object",
        "properties": {
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                        "dimension": {"type": "string"},
                        "description": {"type": "string"},
                        "impact": {"type": "string"},
                        "trend_refs": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["priority", "description", "impact"]
                }
            }
        }
    }
}

config = types.GenerateContentConfig(
    tools=[recommendation_tool],
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(mode="ANY")
    )
)
```

### Error Handling

- Rate limit (429): Exponential backoff with jitter
- Invalid request (400): Fail fast, log error
- Server error (500): Retry with backoff
- Timeout: Return empty recommendations with `llm_available: false`

### Caching Strategy

- Use in-memory LRU cache with TTL
- Cache key: `hash(repository_url + date_range + trend_summary)`
- TTL: 1 hour (configurable)
- Fallback: Return empty if cache unavailable

### Token Management

- Gemini 2.0 Flash: 1M input / 8K output
- Gemini 2.0 Pro: 1M input / 64K output
- Strategy: Use Flash for cost efficiency, limit to top 5 recommendations

## Project Structure

### Source Layout

```
src/archi_c4_score/
├── llm_service.py          # NEW: Gemini API client + recommendation generation
├── models/
│   └── recommendations.py  # NEW: Pydantic models for recommendations
├── api.py                  # MODIFIED: Add recommendations to DashboardResponse
├── hugo_export.py          # MODIFIED: Add recommendations to Hugo export
└── cli.py                  # MODIFIED: Add --recommendations flag

tests/
├── unit/
│   └── test_llm_service.py # NEW: Unit tests for LLM service
└── contract/
    └── test_api.py         # MODIFIED: Add recommendation contract tests
```

## Key Findings

1. **Gemini SDK**: Use `google-genai` package (not `google-generativeai`)
2. **Structured Output**: Use function calling with `mode="ANY"` for reliable JSON
3. **Error Handling**: Implement retry with exponential backoff for 429s
4. **Caching**: Simple in-memory cache with repository+date range key
5. **Fallback**: Always return valid response, mark `llm_available: false` when unavailable
