# Tasks: LLM Dashboard Recommendations

**Input**: Design documents from `/specs/004-llm-dashboard-recommendations/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included per Constitution Principle IX (Test-First)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency configuration

- [x] T001 Add `google-genai` and `cachetools` to project dependencies in pyproject.toml
- [x] T002 [P] Create `src/archi_c4_score/models/` directory if not exists
- [x] T003 [P] Create `tests/unit/` directory if not exists

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create `Recommendation` model in src/archi_c4_score/models/recommendations.py with fields: id, priority, dimension, description, impact, trend_refs
- [x] T005 [P] Create `TrendDimension` model in src/archi_c4_score/models/recommendations.py with fields: dimension, direction, slope, confidence, current_value, start_value, affected_commits
- [x] T006 [P] Create `SignificantChange` model in src/archi_c4_score/models/recommendations.py with fields: commit_sha, date, magnitude, direction, affected_dimensions
- [x] T007 [P] Create `DateRange` model in src/archi_c4_score/models/recommendations.py with fields: start, end
- [x] T008 Create `TrendContext` model in src/archi_c4_score/models/recommendations.py with fields: repository_url, repository_name, date_range, dimensions, significant_changes
- [x] T009 Create `RecommendationSet` model in src/archi_c4_score/models/recommendations.py with fields: recommendations, llm_available, generated_at, model_used, error_message
- [x] T010 Create `__init__.py` in src/archi_c4_score/models/ exporting all recommendation models

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View AI-Generated Recommendations (Priority: P1) 🎯 MVP

**Goal**: Generate AI-powered recommendations based on architecture score trends with priority levels and expected impact

**Independent Test**: Request dashboard with recommendations and verify recommendations are generated based on trend data

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US1] Unit test for GeminiClient initialization in tests/unit/test_llm_service.py
- [x] T012 [P] [US1] Unit test for generate_recommendations with mock LLM response in tests/unit/test_llm_service.py
- [x] T013 [P] [US1] Unit test for fallback behavior when LLM unavailable in tests/unit/test_llm_service.py
- [x] T014 [P] [US1] Unit test for priority ordering (HIGH → MEDIUM → LOW) in tests/unit/test_llm_service.py

### Implementation for User Story 1

- [x] T015 [P] [US1] Implement GeminiClient class in src/archi_c4_score/llm_service.py with __init__ accepting api_key and model_name
- [x] T016 [P] [US1] Implement _build_system_prompt method in src/archi_c4_score/llm_service.py with trend dimension definitions
- [x] T017 [P] [US1] Implement _build_user_prompt method in src/archi_c4_score/llm_service.py with TrendContext data injection
- [x] T018 [US1] Implement _call_gemini_with_retry method in src/archi_c4_score/llm_service.py with exponential backoff for rate limits
- [x] T019 [US1] Implement generate_recommendations method in src/archi_c4_score/llm_service.py returning RecommendationSet
- [x] T020 [US1] Implement _format_recommendations method to parse Gemini function call response into Recommendation models
- [x] T021 [US1] Add structured logging for LLM calls (request/response/errors) in src/archi_c4_score/llm_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Contextual Recommendations (Priority: P2)

**Goal**: Generate recommendations that reference specific trends or commits and acknowledge positive progress

**Independent Test**: Provide known trend patterns and verify recommendations address specific detected issues

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T022 [P] [US2] Unit test for token limit handling (max 5 recommendations) in tests/unit/test_llm_service.py
- [x] T023 [P] [US2] Unit test for caching behavior with repository + date range key in tests/unit/test_llm_service.py
- [x] T024 [P] [US2] Unit test for positive trend acknowledgment in recommendations in tests/unit/test_llm_service.py

### Implementation for User Story 2

- [x] T025 [P] [US2] Implement in-memory LRU cache in src/archi_c4_score/llm_service.py using cachetools with TTL
- [x] T026 [P] [US2] Implement _generate_cache_key method using repository_url + date_range in src/archi_c4_score/llm_service.py
- [x] T027 [US2] Implement _include_trend_refs in prompt to reference specific commits in src/archi_c4_score/llm_service.py
- [x] T028 [US2] Update system prompt to include positive acknowledgment instructions for improving trends in src/archi_c4_score/llm_service.py
- [x] T029 [US2] Implement cache retrieval in generate_recommendations before LLM call in src/archi_c4_score/llm_service.py
- [x] T030 [US2] Implement cache storage after successful LLM response in src/archi_c4_score/llm_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Integration with Dashboard (Priority: P3)

**Goal**: Embed recommendations into existing dashboard API, Hugo export, and CLI output

**Independent Test**: Access existing dashboard endpoint and verify recommendations appear in the response

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T031 [P] [US3] Contract test for GET /api/v1/dashboard with recommendations field in tests/contract/test_api.py
- [x] T032 [P] [US3] Unit test for CLI dashboard command with --recommendations flag in tests/unit/test_cli.py

### Implementation for User Story 3

- [x] T033 [P] [US3] Add RecommendationSetResponse Pydantic model in src/archi_c4_score/api.py
- [x] T034 [P] [US3] Add RecommendationResponse Pydantic model in src/archi_c4_score/api.py
- [x] T035 Extend DashboardResponse in src/archi_c4_score/api.py with recommendations: RecommendationSetResponse field
- [x] T036 [US3] Update GET /api/v1/dashboard endpoint in src/archi_c4_score/api.py to call GeminiClient and include recommendations
- [x] T037 [P] [US3] Update HugoTimelineData dataclass in src/archi_c4_score/hugo_export.py with recommendations field
- [x] T038 [P] [US3] Update generate method in src/archi_c4_score/hugo_export.py to accept recommendations parameter
- [x] T039 [US3] Update _write_json method in src/archi_c4_score/hugo_export.py to include recommendations section
- [x] T040 [P] [US3] Add recommendations shortcode template in src/archi_c4_score/hugo_export.py for Hugo display
- [x] T041 [US3] Add --include-recommendations flag to dashboard command in src/archi_c4_score/cli.py
- [x] T042 [US3] Update dashboard command output in src/archi_c4_score/cli.py to display recommendations when flag is set

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T043 [P] Update AGENTS.md with new dependencies (google-genai, cachetools)
- [x] T044 Run `uv run ruff check .` and fix any linting issues
- [x] T045 Run `uv run python -m pytest tests/unit/test_llm_service.py -v` to verify all tests pass
- [x] T046 Run `uv run python -m pytest tests/contract/test_api.py -v` to verify contract tests pass
- [x] T047 Update quickstart.md in specs/004-llm-dashboard-recommendations/ with recommendation examples

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 caching and trend refs
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates US1/US2 into existing dashboard

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Test-First)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational model tasks marked [P] can run in parallel (T004-T008)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for GeminiClient initialization in tests/unit/test_llm_service.py"
Task: "Unit test for generate_recommendations with mock LLM response in tests/unit/test_llm_service.py"

# Launch all models for User Story 1 together:
Task: "Implement GeminiClient class in src/archi_c4_score/llm_service.py"
Task: "Implement _build_system_prompt method in src/archi_c4_score/llm_service.py"
Task: "Implement _build_user_prompt method in src/archi_c4_score/llm_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (llm_service core)
   - Developer B: User Story 2 (caching, trend refs)
   - Developer C: User Story 3 (API, Hugo, CLI integration)
3. Stories complete and integrate independently

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 47 |
| **Phase 1 (Setup)** | 3 |
| **Phase 2 (Foundational)** | 7 |
| **Phase 3 (US1 - MVP)** | 10 |
| **Phase 4 (US2)** | 9 |
| **Phase 5 (US3)** | 12 |
| **Phase 6 (Polish)** | 5 |
| **Parallelizable Tasks** | 22 |

### Suggested MVP Scope

**User Story 1 only**: Generate basic recommendations with priority and impact

### Task Count per User Story

| User Story | Tasks | Priority |
|------------|-------|----------|
| US1: View AI-Generated Recommendations | 10 | P1 🎯 |
| US2: Contextual Recommendations | 9 | P2 |
| US3: Integration with Dashboard | 12 | P3 |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (Test-First)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
