---
description: "Task list for C4 Graph Scoring - TDD approach"
---

# Tasks: C4 Graph Scoring

**Input**: Design documents from `specs/001-c4-architecture-scoring/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli.md
**Branch**: `001-c4-architecture-scoring`

**Testing Strategy**: TDD with RED → GREEN → REFACTOR cycles per operation.

---

## Phase 1: Setup

**Purpose**: Create project structure and install dependencies

- [ ] T001 Create directory structure per plan.md in `src/archi_c4_score/` and `tests/`
- [ ] T002 [P] Initialize Python project with `pyproject.toml` in `src/`
- [ ] T003 [P] Add dependencies: neo4j-driver, fastapi, click, pydantic, pytest to pyproject.toml
- [ ] T004 Create `src/archi_c4_score/__init__.py` with package exports

**Checkpoint**: Project structure ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data models and Neo4j connection that all features depend on

### Group 2A: Data Models (TDD)

#### RED Phase
- [ ] T005 [P] Write test for ArchimateElement dataclass in `tests/unit/test_models.py`
- [ ] T006 [P] Write test for C4Node dataclass in `tests/unit/test_models.py`
- [ ] T007 [P] Write test for C4Relationship dataclass in `tests/unit/test_models.py`

#### GREEN Phase
- [ ] T008 [P] Implement ArchimateElement dataclass in `src/archi_c4_score/models.py`
- [ ] T009 [P] Implement C4Node dataclass in `src/archi_c4_score/models.py`
- [ ] T010 [P] Implement C4Relationship dataclass in `src/archi_c4_score/models.py`

#### REFACTOR Phase
- [ ] T011 Add C4Level enum with Python 3.12+ `|` union syntax to `src/archi_c4_score/models.py`

**Review Checkpoint 1**: Data models complete

---

### Group 2B: Neo4j Connection (TDD)

#### RED Phase
- [ ] T012 [P] Write test for Neo4j connection in `tests/unit/test_graph.py`
- [ ] T013 [P] Write test for connection pooling in `tests/unit/test_graph.py`
- [ ] T014 [P] Write test for error handling on connection failure in `tests/unit/test_graph.py`

#### GREEN Phase
- [ ] T015 [P] Implement Neo4j connection manager in `src/archi_c4_score/graph.py`
- [ ] T016 [P] Implement connection pool management in `src/archi_c4_score/graph.py`
- [ ] T017 Implement health check and reconnection logic in `src/archi_c4_score/graph.py`

#### REFACTOR Phase
- [ ] T018 Add structured logging for connection events in `src/archi_c4_score/graph.py`

**Review Checkpoint 2**: Neo4j connection working

---

## Phase 3: User Story 1 - Retrieve Architecture Model (P1)

**Goal**: Fetch architecture models from coArchi2 repositories

### Group 3A: Repository Retrieval (TDD)

#### RED Phase
- [ ] T019 [P] [US1] Write test for git clone in `tests/unit/test_repository.py`
- [ ] T020 [P] [US1] Write test for commit SHA extraction in `tests/unit/test_repository.py`
- [ ] T021 [P] [US1] Write test for repository validation in `tests/unit/test_repository.py`

#### GREEN Phase
- [ ] T022 [P] [US1] Implement git clone functionality in `src/archi_c4_score/repository.py`
- [ ] T023 [P] [US1] Implement commit SHA extraction in `src/archi_c4_score/repository.py`
- [ ] T024 [US1] Implement repository path validation in `src/archi_c4_score/repository.py`

#### REFACTOR Phase
- [ ] T025 Add error messages with guidance in `src/archi_c4_score/repository.py`

**Review Checkpoint 3**: Repository retrieval complete

---

## Phase 4: User Story 2 - Extract C4 Model (P2)

**Goal**: Map ArchiMate Application Components to C4 levels via Stereotype

### Group 4A: coArchi2 Parser (TDD)

#### RED Phase
- [ ] T026 [P] [US2] Write test for coArchi2 JSON parsing in `tests/unit/test_parser.py`
- [ ] T027 [P] [US2] Write test for element extraction in `tests/unit/test_parser.py`
- [ ] T028 [P] [US2] Write test for relationship parsing in `tests/unit/test_parser.py`

#### GREEN Phase
- [ ] T029 [P] [US2] Implement coArchi2 JSON parser in `src/archi_c4_score/parser.py`
- [ ] T030 [P] [US2] Implement element extraction in `src/archi_c4_score/parser.py`
- [ ] T031 [US2] Implement relationship parsing in `src/archi_c4_score/parser.py`

#### REFACTOR Phase
- [ ] T032 Add validation for required fields in `src/archi_c4_score/parser.py`

**Review Checkpoint 4**: Parser complete

---

### Group 4B: C4 Mapper (TDD)

#### RED Phase
- [ ] T033 [P] [US2] Write test for stereotype → C4Level mapping in `tests/unit/test_mapper.py`
- [ ] T034 [P] [US2] Write test for ApplicationComponent filtering in `tests/unit/test_mapper.py`
- [ ] T035 [P] [US2] Write test for unknown stereotype skipping in `tests/unit/test_mapper.py`

#### GREEN Phase
- [ ] T036 [P] [US2] Implement C4Mapper class in `src/archi_c4_score/mapper.py`
- [ ] T037 [P] [US2] Implement stereotype → C4Level mapping in `src/archi_c4_score/mapper.py`
- [ ] T038 [US2] Implement parent hierarchy detection in `src/archi_c4_score/mapper.py`

#### REFACTOR Phase
- [ ] T039 Add logging for skipped elements in `src/archi_c4_score/mapper.py`

**Review Checkpoint 5**: C4 mapping complete

---

## Phase 5: User Story 3 - Store C4 Model (P3)

**Goal**: Persist C4 models to Neo4j with nodes and weighted edges

### Group 5A: Neo4j Import (TDD)

#### RED Phase
- [ ] T040 [P] [US3] Write test for node creation in `tests/unit/test_graph.py`
- [ ] T041 [P] [US3] Write test for relationship creation with weights in `tests/unit/test_graph.py`
- [ ] T042 [P] [US3] Write test for git commit linking in `tests/unit/test_graph.py`

#### GREEN Phase
- [ ] T043 [P] [US3] Implement node import with Cypher in `src/archi_c4_score/graph.py`
- [ ] T044 [P] [US3] Implement relationship import with weights in `src/archi_c4_score/graph.py`
- [ ] T045 [US3] Implement git commit property assignment in `src/archi_c4_score/graph.py`

#### REFACTOR Phase
- [ ] T046 Add batch import optimization in `src/archi_c4_score/graph.py`

**Review Checkpoint 6**: Neo4j import complete

---

### Group 5B: Graph Queries (TDD)

#### RED Phase
- [ ] T047 [P] [US3] Write test for C4 hierarchy retrieval in `tests/unit/test_graph.py`
- [ ] T048 [P] [US3] Write test for relationship queries in `tests/unit/test_graph.py`
- [ ] T049 [P] [US3] Write test for history queries by commit in `tests/unit/test_graph.py`

#### GREEN Phase
- [ ] T050 [P] [US3] Implement C4 hierarchy query in `src/archi_c4_score/graph.py`
- [ ] T051 [P] [US3] Implement relationship query in `src/archi_c4_score/graph.py`
- [ ] T052 [US3] Implement history retrieval by commit in `src/archi_c4_score/graph.py`

#### REFACTOR Phase
- [ ] T053 Add parameterized query safety in `src/archi_c4_score/graph.py`

**Review Checkpoint 7**: Graph queries complete

---

## Phase 6: User Story 4 - Score Architecture (P4)

**Goal**: Calculate complexity scores using Instability Index and dependency weights

### Group 6A: Scoring Engine (TDD)

#### RED Phase
- [ ] T054 [P] [US4] Write test for Instability Index calculation in `tests/unit/test_scoring.py`
- [ ] T055 [P] [US4] Write test for dependency weight application in `tests/unit/test_scoring.py`
- [ ] T056 [P] [US4] Write test for dimension scoring in `tests/unit/test_scoring.py`

#### GREEN Phase
- [ ] T057 [P] [US4] Implement Instability Index calculation in `src/archi_c4_score/scoring.py`
- [ ] T058 [P] [US4] Implement dependency weight application in `src/archi_c4_score/scoring.py`
- [ ] T059 [P] [US4] Implement dimension scoring in `src/archi_c4_score/scoring.py`
- [ ] T060 [US4] Implement score aggregation (Component → Container → System) in `src/archi_c4_score/scoring.py`

#### REFACTOR Phase
- [ ] T061 Extract scoring weights to configuration in `src/archi_c4_score/scoring.py`

**Review Checkpoint 8**: Scoring engine complete

---

### Group 6B: Circular Dependency Detection (TDD)

#### RED Phase
- [ ] T062 [P] [US4] Write test for cycle detection in `tests/unit/test_scoring.py`
- [ ] T063 [P] [US4] Write test for penalty application in `tests/unit/test_scoring.py`

#### GREEN Phase
- [ ] T064 [P] [US4] Implement cycle detection using Neo4j Cypher in `src/archi_c4_score/scoring.py`
- [ ] T065 [US4] Implement complexity penalty for cycles in `src/archi_c4_score/scoring.py`

#### REFACTOR Phase
- [ ] T066 Add logging for detected cycles in `src/archi_c4_score/scoring.py`

**Review Checkpoint 9**: Circular dependency handling complete

---

### Group 6C: Recommendations (TDD)

#### RED Phase
- [ ] T067 [P] [US4] Write test for recommendation generation in `tests/unit/test_scoring.py`
- [ ] T068 [P] [US4] Write test for priority assignment in `tests/unit/test_scoring.py`

#### GREEN Phase
- [ ] T069 [P] [US4] Implement recommendation generator in `src/archi_c4_score/scoring.py`
- [ ] T070 [US4] Implement priority assignment in `src/archi_c4_score/scoring.py`

#### REFACTOR Phase
- [ ] T071 Extract recommendation templates in `src/archi_c4_score/scoring.py`

**Review Checkpoint 10**: Recommendations complete

---

## Phase 7: Interfaces

### Group 7A: CLI (TDD)

#### RED Phase
- [ ] T072 [P] Write CLI contract tests in `tests/contract/test_cli.py`
- [ ] T073 [P] Write CLI error handling tests in `tests/contract/test_cli.py`

#### GREEN Phase
- [ ] T074 [P] Implement CLI with click in `src/archi_c4_score/cli.py`
- [ ] T075 [P] Implement import command in `src/archi_c4_score/cli.py`
- [ ] T076 [P] Implement score command in `src/archi_c4_score/cli.py`
- [ ] T077 [P] Implement history command in `src/archi_c4_score/cli.py`
- [ ] T078 [P] Implement query command in `src/archi_c4_score/cli.py`

#### REFACTOR Phase
- [ ] T079 Add JSON and human output formatters in `src/archi_c4_score/cli.py`

**Review Checkpoint 11**: CLI complete

---

### Group 7B: REST API (TDD)

#### RED Phase
- [ ] T080 [P] Write API contract tests in `tests/contract/test_api.py`
- [ ] T081 [P] Write API error handling tests in `tests/contract/test_api.py`

#### GREEN Phase
- [ ] T082 [P] Implement FastAPI app in `src/archi_c4_score/api.py`
- [ ] T083 [P] Implement POST /api/v1/import endpoint in `src/archi_c4_score/api.py`
- [ ] T084 [P] Implement POST /api/v1/score endpoint in `src/archi_c4_score/api.py`
- [ ] T085 [P] Implement GET /api/v1/model/{commit} endpoint in `src/archi_c4_score/api.py`
- [ ] T086 [P] Implement GET /api/v1/history endpoint in `src/archi_c4_score/api.py`

#### REFACTOR Phase
- [ ] T087 Add OpenAPI documentation in `src/archi_c4_score/api.py`

**Review Checkpoint 12**: REST API complete

---

## Phase 8: Polish

**Purpose**: Finalization, documentation, and cleanup

- [ ] T088 [P] Run full test suite with coverage report
- [ ] T089 [P] Run ruff check and fix linting issues in `src/`
- [ ] T090 [P] Verify type hints with mypy in `src/archi_c4_score/`
- [ ] T091 [P] Create sample coArchi2 test file in `tests/fixtures/`
- [ ] T092 Write integration test for full pipeline in `tests/integration/test_pipeline.py`
- [ ] T093 [P] Update README.md with installation and usage in `src/`
- [ ] T094 Verify 80%+ test coverage meets QA requirements
- [ ] T095 Final validation against spec.md acceptance criteria

**Checkpoint**: All phases complete, feature ready for review

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Blocks |
|-------|-----------|--------|
| 1: Setup | None | All |
| 2: Foundational | Phase 1 | All user stories |
| 3: US1 | Phase 2 | None |
| 4: US2 | Phase 2 | None |
| 5: US3 | Phase 2, 4 | None |
| 6: US4 | Phase 2, 4, 5 | None |
| 7: Interfaces | Phase 3, 4, 5, 6 | None |
| 8: Polish | All | None |

### MVP Scope

Focus on Phase 1-4 (Setup, Foundational, US1, US2) for MVP:
- Repository retrieval working
- C4 mapping with Neo4j storage
- Basic query capability

---

## TDD Workflow

For each group:

1. **RED**: Write failing tests first (verify they fail)
2. **GREEN**: Implement minimum code to make tests pass
3. **REFACTOR**: Clean up code while keeping tests green

**Review checkpoints**: After each group, pause for human review before proceeding.

**Commit strategy**: After each successful checkpoint:
```bash
git add -A && git commit -m "feat: complete [group name] (TDD)"
```

---

## Notes

- All tests use pytest framework
- [P] = parallelizable (different files, no dependencies)
- [US1-US4] = which user story this task serves
- Reversibility: Each commit is self-contained; can revert any checkpoint
