# Feature Specification: LLM Dashboard Recommendations

**Feature Branch**: `004-llm-dashboard-recommendations`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: User description: "add a LLM generated recommendation to the dashboard based on architecture score trend"

## User Scenarios & Testing

### User Story 1 - View AI-Generated Recommendations (Priority: P1)

As an architect, I want to receive AI-generated recommendations based on my architecture score trends so that I can understand what actions to take to improve the architecture.

**Why this priority**: Without actionable recommendations, architects have data but no guidance on how to use it to improve the system.

**Independent Test**: Can be fully tested by requesting dashboard with recommendations and verifying recommendations are generated based on trend data.

**Acceptance Scenarios**:

1. **Given** a dashboard with existing trend data, **When** the user views recommendations, **Then** the system generates recommendations based on the identified trends.
2. **Given** a declining coupling trend, **When** recommendations are generated, **Then** the system suggests actions to reduce coupling.
3. **Given** a declining modularity trend, **When** recommendations are generated, **Then** the system suggests actions to improve modularity.
4. **Given** the recommendations, **When** displayed, **Then** each recommendation includes a priority level and expected impact.

---

### User Story 2 - Contextual Recommendations (Priority: P2)

As an architect, I want recommendations that are specific to the detected issues so that I can take targeted action.

**Why this priority**: Generic recommendations are less actionable than those directly tied to observed patterns.

**Independent Test**: Can be fully tested by providing known trend patterns and verifying recommendations address specific detected issues.

**Acceptance Scenarios**:

1. **Given** a trend showing increased complexity, **When** recommendations are generated, **Then** the recommendation references the specific commits or patterns that caused the change.
2. **Given** multiple concerning trends, **When** recommendations are generated, **Then** they are ordered by priority based on severity.
3. **Given** a positive trend (improving scores), **When** recommendations are generated, **Then** the system acknowledges positive progress and suggests maintaining good practices.

---

### User Story 3 - Integration with Dashboard (Priority: P3)

As an architect, I want recommendations embedded in my existing dashboard workflow so that I don't need to switch contexts.

**Why this priority**: Seamless integration increases adoption and usability of the recommendation feature.

**Independent Test**: Can be fully tested by accessing the existing dashboard endpoint and verifying recommendations appear in the response.

**Acceptance Scenarios**:

1. **Given** the existing dashboard API, **When** recommendations are requested, **Then** they are included in the response without changing existing fields.
2. **Given** the Hugo export, **When** recommendations are generated, **Then** they appear in the generated report.
3. **Given** the CLI dashboard command, **When** it is executed, **Then** recommendations are displayed in the output.

---

### Edge Cases

- What happens when trends are all stable (no significant changes)?
- How does the system handle missing or incomplete trend data?
- What occurs when the LLM service is unavailable?
- How are recommendations limited to prevent token overflow?

## Requirements

### Functional Requirements

- **FR-001**: System MUST generate recommendations based on trend analysis data (coupling, modularity, cohesion trends)
- **FR-002**: System MUST include priority level (HIGH/MEDIUM/LOW) for each recommendation
- **FR-003**: System MUST include expected impact description for each recommendation
- **FR-004**: System MUST reference specific trends or commits in recommendations when relevant
- **FR-005**: System MUST order recommendations by priority
- **FR-006**: System MUST include positive acknowledgment when trends are improving
- **FR-007**: System MUST fall back gracefully when LLM service is unavailable (return empty recommendations with warning)
- **FR-008**: System MUST integrate recommendations into existing dashboard endpoint response
- **FR-009**: System MUST generate Hugo-compatible recommendation section for export

### Key Entities

- **Recommendation**: An AI-generated suggestion based on trend analysis
- **TrendContext**: The trend data (dimension, direction, slope, affected commits) provided to the LLM
- **RecommendationSet**: A collection of recommendations with priority ordering

## Success Criteria

### Measurable Outcomes

- **SC-001**: Recommendations are generated for 100% of dashboard requests with trend data
- **SC-002**: Each recommendation includes priority level and expected impact
- **SC-003**: System responds within 5 seconds even when LLM call is included
- **SC-004**: Dashboard with recommendations is viewable via CLI, API, and Hugo export

## Assumptions

- LLM integration: Google Gemini 2.0 API via `google-generativeai` package
- Recommendation format: Markdown text with structured metadata
- Prompt engineering: System prompt includes trend context and scoring dimension definitions
- Token management: Recommendations limited to top 5 priority items
- Fallback: If LLM unavailable, return empty recommendations array with `llm_available: false`
- Response caching: LLM responses may be cached for identical trend configurations

## Implementation Checklist

### Development

- [ ] **New: LLM Service** (`src/archi_c4_score/llm_service.py`)
  - [ ] GeminiClient class for Google Gemini 2.0 API integration
  - [ ] `generate_recommendations(trend_context: TrendContext) -> RecommendationSet`
  - [ ] System prompt with trend context and dimension definitions
  - [ ] User prompt template with dynamic trend data injection
  - [ ] Use Gemini function calling for structured JSON output
  - [ ] Token limit handling (top 5 recommendations max)
  - [ ] Graceful fallback when LLM unavailable (return empty with `llm_available: false`)
  - [ ] Response caching using repository URL + date range as key

- [ ] **New: Data Models** (`src/archi_c4_score/llm_service.py` or `models/recommendations.py`)
  - [ ] `Recommendation` model (id, priority, impact, description, trend_refs)
  - [ ] `TrendContext` model (dimensions with direction/slope/commits)
  - [ ] `RecommendationSet` model (recommendations, llm_available, generated_at)

- [ ] **API Updates** (`src/archi_c4_score/api.py`)
  - [ ] Extend `/api/v1/dashboard` response with `recommendations` field
  - [ ] Add `recommendations` to response schema

- [ ] **Hugo Export Updates** (`src/archi_c4_score/hugo_export.py`)
  - [ ] Add recommendations section to `DashboardGenerator`
  - [ ] Generate recommendations data JSON for Hugo
  - [ ] Add Hugo shortcode for recommendations display

- [ ] **CLI Updates** (`src/archi_c4_score/cli.py`)
  - [ ] Add `--recommendations` flag to `dashboard` command
  - [ ] Display recommendations in CLI output

### Testing

- [ ] **Unit Tests** (`tests/unit/test_llm_service.py`)
  - [ ] Test recommendation generation with mock LLM
  - [ ] Test fallback when LLM unavailable
  - [ ] Test priority ordering
  - [ ] Test token limit handling
  - [ ] Test caching behavior

- [ ] **Integration Tests**
  - [ ] Test end-to-end with real LLM (if available)
  - [ ] Test recommendations appear in dashboard response

### Documentation

- [ ] Update quickstart with recommendation examples

## Clarifications

### Session 2026-04-16

- **LLM Model**: Google Gemini 2.0 API (not Azure OpenAI)
- **Structured Output**: Yes - use function calling/tools for reliable JSON parsing
- **Trend Context**: Include last 30 commits (matches existing backfill default)
- **Caching Key**: Repository URL + date range (stable key that invalidates on new commits)
- **API Location**: Add recommendations to `DashboardResponse` model
- **Expected Impact**: Qualitative (HIGH/MEDIUM/LOW) is sufficient
- **Fallback**: Continue generating dashboard if LLM unavailable, return empty recommendations with `llm_available: false`
