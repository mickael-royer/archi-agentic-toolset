---

description: "Task list for ArchiMate Timeline Dashboard feature implementation"
---

# Tasks: ArchiMate Timeline Dashboard

**Input**: Design documents from `/specs/004-archimate-timeline-dashboard/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/timeline-api.yaml

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/archi_c4_score/`, `tests/` at repository root
- Hugo output: `output/data/`, `output/layouts/shortcodes/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization for timeline feature

- [x] T001 [P] Create timeline module structure in src/archi_c4_score/timeline.py
- [x] T002 [P] Create Hugo export module in src/archi_c4_score/hugo_export.py
- [x] T003 [P] Add timeline dependencies to pyproject.toml (if needed) - No additional dependencies required
- [x] T004 Configure structured logging for timeline operations - Uses existing DaprJsonFormatter

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create ScoredCommit Pydantic model in src/archi_c4_score/models.py
- [x] T006 Create TrendLine Pydantic model in src/archi_c4_score/models.py
- [x] T007 Create ScoreDelta Pydantic model in src/archi_c4_score/models.py
- [x] T008 Create CommitDiff Pydantic model in src/archi_c4_score/models.py
- [x] T009 Create DashboardReport Pydantic model in src/archi_c4_score/models.py
- [x] T010 [P] Add Neo4j schema migration for ScoredCommit node in src/archi_c4_score/graph.py
- [x] T011 [P] Add Neo4j indexes for scored_commit_repo_date and scored_commit_sha in src/archi_c4_score/graph.py
- [x] T012 [P] Implement ScoredCommitRepository with save and find methods in src/archi_c4_score/graph.py
- [x] T013 [P] Implement commit history retrieval by repository in src/archi_c4_score/repository.py
- [x] T014 Implement git history iteration for scoring multiple commits in src/archi_c4_score/repository.py
- [x] T015 Add backfill orchestration logic in src/archi_c4_score/scoring.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Architecture Change Timeline (Priority: P1) 🎯 MVP

**Goal**: Display chronological architecture score history with significant change highlighting

**Independent Test**: Provide repository with multiple commits, verify timeline shows scores chronologically with SHA, date, author, composite score, dimension scores, and highlights significant changes

### Implementation for User Story 1

- [x] T016 [US1] Implement TimelineService with get_timeline method in src/archi_c4_score/timeline.py
- [x] T017 [US1] Implement TimelinePoint calculation with score_delta and is_significant logic in src/archi_c4_score/timeline.py
- [x] T018 [US1] Implement pagination for timeline queries in src/archi_c4_score/timeline.py
- [x] T019 [US1] Add GET /api/v1/timeline endpoint in src/archi_c4_score/api.py
- [x] T020 [US1] Add timeline CLI command in src/archi_c4_score/cli.py
- [x] T021 [US1] Add gap handling for unscored commits in timeline in src/archi_c4_score/timeline.py
- [x] T022 [US1] Add logging for timeline retrieval operations in src/archi_c4_score/timeline.py

### Tests for User Story 1

- [x] T023 [P] [US1] Unit tests for TimelineService.get_timeline in tests/unit/test_timeline.py
- [x] T024 [P] [US1] Unit tests for TimelinePoint calculation in tests/unit/test_timeline.py
- [x] T025 [P] [US1] Contract test for GET /api/v1/timeline in tests/contract/test_api.py

**Checkpoint**: Timeline view functional - User Story 1 MVP complete

---

## Phase 4: User Story 2 - Track Complexity Trends Over Time (Priority: P2)

**Goal**: Calculate and display trend direction for each scoring dimension

**Independent Test**: Provide repository with known complexity changes, verify trend line accurately reflects expected direction (INCREASING/DECREASING/STABLE) per dimension

### Implementation for User Story 2

- [x] T026 [P] [US2] Implement TrendCalculator with linear regression in src/archi_c4_score/timeline.py
- [x] T027 [US2] Implement trend direction classification (slope threshold logic) in src/archi_c4_score/timeline.py
- [x] T028 [US2] Implement commit identification for largest changes in src/archi_c4_score/timeline.py
- [x] T029 [US2] Add GET /api/v1/timeline/trends endpoint in src/archi_c4_score/api.py
- [x] T030 [US2] Add trends CLI command in src/archi_c4_score/cli.py
- [x] T031 [US2] Add confidence (R²) calculation to TrendLine in src/archi_c4_score/timeline.py

### Tests for User Story 2

- [x] T032 [P] [US2] Unit tests for TrendCalculator.linear_regression in tests/unit/test_timeline.py
- [x] T033 [P] [US2] Unit tests for trend direction classification in tests/unit/test_timeline.py
- [x] T034 [P] [US2] Contract test for GET /api/v1/timeline/trends in tests/contract/test_api.py

**Checkpoint**: Trend analysis functional - User Story 2 complete

---

## Phase 5: User Story 3 - Generate Dashboard Report (Priority: P3)

**Goal**: Produce Hugo-compatible dashboard with timeline chart, health status, and top concerns

**Independent Test**: Request dashboard report, verify it contains timeline chart data, health status, top 3 concerns, and change detection

### Implementation for User Story 3

- [x] T035 [US3] Implement DashboardGenerator service in src/archi_c4_score/hugo_export.py
- [x] T036 [US3] Implement health_status calculation (IMPROVING/DECLINING/STABLE) in src/archi_c4_score/hugo_export.py
- [x] T037 [US3] Implement top_concerns generation (top 3) in src/archi_c4_score/hugo_export.py
- [x] T038 [US3] Implement JSON export for Hugo data/timeline.json in src/archi_c4_score/hugo_export.py
- [x] T039 [US3] Implement Hugo shortcode generation in src/archi_c4_score/hugo_export.py
- [x] T040 [US3] Implement significant_change detection for dashboard in src/archi_c4_score/hugo_export.py
- [x] T041 [US3] Add GET /api/v1/dashboard endpoint in src/archi_c4_score/api.py
- [x] T042 [US3] Add dashboard CLI command in src/archi_c4_score/cli.py
- [x] T043 [US3] Add Chart.js timeline chart template in output/layouts/shortcodes/archi-timeline.html

### Tests for User Story 3

- [x] T044 [P] [US3] Unit tests for DashboardGenerator in tests/unit/test_timeline.py
- [x] T045 [P] [US3] Unit tests for health_status calculation in tests/unit/test_timeline.py
- [x] T046 [P] [US3] Integration test for Hugo export in tests/integration/test_pipeline.py

**Checkpoint**: Dashboard report functional - User Story 3 complete

---

## Phase 6: User Story 4 - Compare Specific Commits (Priority: P4)

**Goal**: Diff two commits showing element/relationship changes and scoring impact

**Independent Test**: Compare two commits with known differences, verify diff accurately reflects element and relationship changes with scoring impact explanation

### Implementation for User Story 4

- [x] T047 [US4] Implement CommitComparator service in src/archi_c4_score/timeline.py
- [x] T048 [US4] Implement element diff (added/removed/modified) in src/archi_c4_score/timeline.py
- [x] T049 [US4] Implement relationship diff (added/removed/weight changes) in src/archi_c4_score/timeline.py
- [x] T050 [US4] Implement scoring_impact explanation in src/archi_c4_score/timeline.py
- [x] T051 [US4] Add GET /api/v1/timeline/compare endpoint in src/archi_c4_score/api.py
- [x] T052 [US4] Add compare CLI command in src/archi_c4_score/cli.py

### Tests for User Story 4

- [x] T053 [P] [US4] Unit tests for CommitComparator in tests/unit/test_timeline.py
- [x] T054 [P] [US4] Unit tests for element diff calculation in tests/unit/test_timeline.py
- [x] T055 [P] [US4] Contract test for GET /api/v1/timeline/compare in tests/contract/test_api.py

**Checkpoint**: Commit comparison functional - User Story 4 complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories

- [x] T056 [P] Integration test for end-to-end scoring pipeline in tests/integration/test_pipeline.py
- [x] T057 [P] Update pyproject.toml with new CLI entry points
- [x] T058 [P] Add POST /api/v1/scoring/backfill endpoint in src/archi_c4_score/api.py
- [x] T059 Add backfill CLI command in src/archi_c4_score/cli.py
- [x] T060 Performance test for SC-001 (100 commits < 30s) in tests/integration/test_pipeline.py
- [x] T061 Update README.md with timeline commands
- [x] T062 Run quickstart.md validation - All tests passing
- [x] T063 Run lint: `uv run ruff check .` - All checks passed!
- [x] T064 Run typecheck: `uv run mypy src/archi_c4_score/` - 2 pre-existing errors in github_importer.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational
  - US1, US2, US3, US4 can proceed in parallel (if staffed)
  - Or sequentially: US1 → US2 → US3 → US4
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: MVP - Can start after Foundational - No dependencies on other stories
- **US2 (P2)**: Can start after Foundational - Uses timeline data from US1
- **US3 (P3)**: Can start after Foundational - Uses timeline and trends from US1/US2
- **US4 (P4)**: Can start after Foundational - Independent diff implementation

### Within Each User Story

- Models before services (Phase 2 establishes models)
- Core implementation before endpoints
- Unit tests before integration tests
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: All tasks marked [P] can run in parallel
- Phase 2: Index and repository tasks marked [P] can run in parallel
- Phase 3-6: User stories can run in parallel if team capacity allows
- Tests within each story marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch unit tests for User Story 1 together:
Task: T023 - Unit tests for TimelineService.get_timeline
Task: T024 - Unit tests for TimelinePoint calculation

# Implementation can proceed sequentially within story:
Task: T016 - TimelineService.get_timeline
Task: T017 - TimelinePoint calculation (depends on T016)
Task: T018 - Pagination (depends on T016)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test timeline independently
5. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo

### Parallel Team Strategy

With multiple developers:

1. Complete Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3 + 4

---

## Task Summary

| Phase | Tasks | User Story |
|-------|-------|------------|
| 1: Setup | T001-T004 | None |
| 2: Foundational | T005-T015 | None |
| 3: US1 Timeline | T016-T025 | US1 |
| 4: US2 Trends | T026-T034 | US2 |
| 5: US3 Dashboard | T035-T046 | US3 |
| 6: US4 Compare | T047-T055 | US4 |
| 7: Polish | T056-T064 | None |

**Total Tasks**: 64
**Parallelizable**: ~40 tasks marked [P]

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies
