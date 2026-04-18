# Tasks: C4 Architecture Scoring Engine

**Feature**: 006-c4-scoring-engine  
**Generated**: 2026-04-18  
**Spec**: specs/006-c4-scoring-engine/spec.md  
**Plan**: specs/006-c4-scoring-engine/plan.md

## Dependency Graph

```
User Story Phases (Priority Order):
┌─────────────────────────────────────────────────────────┐
│  US1 (P1) → US2 (P1) → US3 (P2) → US4 (P1)  │
│    ↓                              ↓              │
│  US5 (P2) ──────────────────────────→ US6 (P3)│
└─────────────────────────────────────────────────────────┘

US1: Container scoring (independent MVP)
US2: System consolidation (depends on US1 scoring data)
US3: Timeline tracking (independent)
US4: API endpoints (independent)
US5: Export (depends on US3 timeline data)
US6: Treemap (depends on US1/US2 container data)
```

## Phase 1: Setup

- [X] T001 Verify existing scoring dependencies (archimate_scorer.py, models.py)
- [X] T002 Verify existing API structure (api.py, cli.py)

## Phase 2: Foundational

- [X] T003 [P] Add C4Level enum to src/archi_c4_score/models.py
- [X] T004 [P] Add C4Node and C4Relationship datatypes to src/archi_c4_score/models.py

## Phase 3: User Story 1 - View Architecture Scores by Container (P1)

**Goal**: Calculate architecture score at container level with weighted sync/async coupling

**Independent Test**: Load model with 3 containers, verify each receives distinct score based on coupling

**Implementation**:
- [X] T005 [US1] Implement C4 entity converter in src/archi_c4_score/c4_converter.py
- [X] T006 [US1] Add weighted coupling calculation in src/archi_c4_score/scoring.py
- [X] T007 [US1] Add ContainerScore model to src/archi_c4_score/models.py
- [X] T008 [US1] Create container_scoring method in src/archi_c4_score/scoring.py

## Phase 4: User Story 2 - View Consolidated Software System Score (P1)

**Goal**: Aggregate container scores into system-level score

**Independent Test**: Verify system score = average of container scores (or weighted aggregate)

**Implementation**:
- [X] T009 [US2] Implement system_score aggregation in src/archi_c4_score/scoring.py
- [X] T010 [US2] Add ScoringReport model to src/archi_c4_score/models.py

## Phase 5: User Story 3 - Track Score Evolution Over Time (P2)

**Goal**: Store and retrieve historical scores by commit timestamp

**Independent Test**: Compare scores at different commits without requiring UI

**Implementation**:
- [X] T011 [US3] Add ScoreSnapshot entity to src/archi_c4_score/models.py
- [X] T012 [US3] Implement timeline storage in src/archi_c4_score/storage.py
- [X] T013 [US3] Add timeline retrieval method in src/archi_c4_score/scoring.py

## Phase 6: User Story 4 - Access Scores via Dashboard API (P1)

**Goal**: Expose scoring endpoints via FastAPI

**Independent Test**: Call API, verify JSON response structure

**Implementation**:
- [X] T014 [US4] Add GET /scores/container endpoint in src/archi_c4_score/api.py
- [X] T015 [US4] Add GET /scores/system endpoint in src/archi_c4_score/api.py
- [X] T016 [US4] Add GET /scores/timeline endpoint in src/archi_c4_score/api.py

## Phase 7: User Story 5 - Export Dashboard Reports (P2)

**Goal**: Export timeline, trends, recommendations data

**Independent Test**: Request export, verify file contains expected data

**Implementation**:
- [X] T017 [US5] Add GET /scores/export endpoint in src/archi_c4_score/api.py
- [X] T018 [US5] Implement export generation in src/archi_c4_score/exporter.py

## Phase 8: User Story 6 - View Treemap Visualization (P3)

**Goal**: Generate treemap data structure for visualization

**Independent Test**: Generate treemap data, verify cell sizing

**Implementation**:
- [X] T019 [US6] Add TreemapCell model to src/archi_c4_score/models.py
- [X] T020 [US6] Implement treemap generation in src/archi_c4_score/treemap.py
- [X] T021 [US6] Add GET /scores/treemap endpoint in src/archi_c4_score/api.py

## Phase 9: Polish

- [X] T022 [P] Verify all endpoints match contracts/api.md specification
- [X] T023 [P] Add contract tests for new endpoints in tests/contract/
- [X] T024 Run full test suite and fix any failures
- [X] T025 Update README.md with scoring formula documentation

## Implementation Strategy

### MVP Scope (User Story 1 only)
- T001, T002 → T003, T004 → T005, T006, T007, T008
- Total: 8 tasks for MVP

### Incremental Delivery
1. **Sprint 1**: Container-level scoring (US1) - T001-T008
2. **Sprint 2**: System consolidation (US2) - T009-T010
3. **Sprint 3**: Timeline + API (US3+US4) - T011-T016
4. **Sprint 4**: Export + Treemap (US5+US6) - T017-T021
5. **Sprint 5**: Polish - T022-T025

### Parallel Opportunities
- T003 and T004 can run in parallel (both model additions)
- T017 and T019 can run in parallel (different output formats)
- T022 and T023 can run in parallel (verification and testing)

## Summary

| Phase | Tasks | User Story |
|-------|-------|------------|
| Setup | 2 | - |
| Foundational | 2 | - |
| US1 (P1) | 4 | Container scoring |
| US2 (P1) | 2 | System consolidation |
| US3 (P2) | 3 | Timeline tracking |
| US4 (P1) | 3 | API endpoints |
| US5 (P2) | 2 | Export |
| US6 (P3) | 3 | Treemap |
| Polish | 4 | - |
| **Total** | **25** | - |