---
description: "Task list for Dapr Scoring Microservice - TDD approach with containerization"
---

# Tasks: Dapr Scoring Microservice

**Input**: Design documents from `/specs/003-dapr-scoring-microservice/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

## Format

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create deploy directory and container infrastructure

- [x] T001 [P] Create deploy directory structure per plan.md
- [x] T002 [P] Create Dockerfile with distroless Python base image
- [x] T003 [P] Create multi-stage build in deploy/Dockerfile
- [x] T004 [P] Create docker-compose.yaml with Dapr + Neo4j services

**Checkpoint**: ✅ Phase 1 Complete - deploy directory created with Dockerfile and compose

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core container/sidecar infrastructure that enables all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Create Dapr component specs in deploy/components/statestore.yaml
- [x] T006 [P] Create Dapr component specs in deploy/components/pubsub.yaml
- [x] T007 Create health endpoints (/health, /dapr/health) in src/archi_c4_score/api.py
- [x] T008 Configure Dapr secrets for Neo4j credentials in deploy/components/
- [x] T009 Add structured logging to API for observability

**Checkpoint**: ✅ Phase 2 Complete - Container can build and start with Dapr sidecar

---

## Phase 3: User Story 1 - Local Development (Priority: P1) 🎯 MVP

**Goal**: Developer can run `podman-compose up` to start scoring service locally

**Independent Test**: `podman-compose up` starts all services; curl localhost:8000/health returns healthy

### Tests for User Story 1

> Write these tests FIRST, ensure they FAIL before implementation

- [x] T010 [P] [US1] Contract test for /health endpoint in tests/contract/test_api.py
- [x] T011 [P] [US1] Integration test for podman-compose startup in tests/integration/test_local_dev.py

### Implementation for User Story 1

- [x] T012 [US1] Update docker-compose.yaml with scoring-service, dapr, neo4j
- [x] T013 [US1] Create deploy/scripts/wait-for-neo4j.sh
- [x] T014 [US1] Configure uvicorn to run api:app in Dockerfile
- [x] T015 [US1] Verify container builds successfully
- [x] T016 [US1] Test podman-compose up and health endpoint

**Checkpoint**: ✅ Phase 3 Complete - `podman-compose up` works, service is reachable

---

## Phase 4: User Story 2 - Microservice Deployment (Priority: P2)

**Goal**: Service uses Dapr sidecar for state management and observability

**Independent Test**: Dapr sidecar responds, state store caches scoring results

### Tests for User Story 2

- [x] T017 [P] [US2] Contract test for POST /api/v1/score with Dapr binding
- [x] T018 [P] [US2] Integration test for Dapr state store caching

### Implementation for User Story 2

- [x] T019 [US2] Install dapr/sdka-python in src/pyproject.toml
- [x] T020 [US2] Create Dapr client wrapper in src/archi_c4_score/dapr_client.py
- [x] T021 [US2] Implement state store caching in scoring endpoint
- [x] T022 [US2] Add Dapr service invocation support
- [x] T023 [US2] Configure Dapr observability (tracing, metrics)
- [x] T024 [US2] Test /dapr/health endpoint

**Checkpoint**: Dapr sidecar enables state management and observability

---

## Phase 5: User Story 3 - Container Security (Priority: P3)

**Goal**: Production containers use distroless images with minimal attack surface

**Independent Test**: Container has no shell, passes security scan

### Tests for User Story 3

- [x] T025 [P] [US3] Test container has no shell available
- [x] T026 [P] [US3] Test container image scan passes (trivy/grype)

### Implementation for User Story 3

- [x] T027 [US3] Verify Dockerfile uses gcr.io/distroless/python3-debian12
- [x] T028 [US3] Ensure no shell or package manager in production image
- [x] T029 [US3] Add non-root user in Dockerfile (security best practice)
- [x] T030 [US3] Configure read-only filesystem where possible
- [x] T031 [US3] Add health checks (HEALTHCHECK) in Dockerfile
- [x] T032 [US3] Run Trivy/Grype scan and document results

**Checkpoint**: Distroless image with no shell, security scan passes

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [x] T033 [P] Update deploy/README.md with local dev and production deployment
- [x] T034 [P] Validate quickstart.md commands work
- [x] T035 Run full test suite with coverage
- [x] T036 Run ruff linting and mypy type check
- [x] T037 Create Azure Container Apps deployment guide in deploy/aca/
- [x] T038 Create Bicep IaC files for Azure deployment
- [x] T039 Verify 80%+ test coverage meets QA requirements

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3-5 (User Stories)**: All depend on Phase 2, can proceed in parallel
- **Phase 6 (Polish)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - no dependencies on other stories
- **US2 (P2)**: Can start after Foundational - uses archi-c4-score library
- **US3 (P3)**: Can start after Foundational - independent of other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Core implementation before integration
- Story complete before moving to next priority

---

## Parallel Opportunities

### Phase 1 (Setup)
```bash
T001: Create deploy directory structure
T002: Create Dockerfile
T003: Create multi-stage build
T004: Create docker-compose.yaml
```

### Phase 2 (Foundational)
```bash
T005: Create statestore.yaml
T006: Create pubsub.yaml
```

### Phase 3 (US1)
```bash
T010: Contract test for /health
T011: Integration test for compose
```

### Phase 4 (US2)
```bash
T017: Contract test for scoring
T018: Integration test for state
```

### Phase 5 (US3)
```bash
T025: Test no shell
T026: Test security scan
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup → T001-T004
2. Complete Phase 2: Foundational → T005-T009
3. Complete Phase 3: US1 → T010-T016
4. **STOP and VALIDATE**: Test podman-compose up
5. Deploy/demo if ready

### Incremental Delivery

1. Phase 1-2 → Foundation ready
2. Phase 3 (US1) → Test independently → Deploy/Demo (MVP!)
3. Phase 4 (US2) → Test independently → Deploy/Demo
4. Phase 5 (US3) → Test independently → Deploy/Demo
5. Phase 6 → Polish and finalize

---

## Task Summary

| Phase | Tasks | User Story |
|-------|-------|------------|
| Phase 1: Setup | T001-T004 | - |
| Phase 2: Foundational | T005-T009 | - |
| Phase 3: US1 | T010-T016 | Local Dev |
| Phase 4: US2 | T017-T024 | Dapr Microservice |
| Phase 5: US3 | T025-T032 | Security |
| Phase 6: Polish | T033-T039 | - |

**Total**: 39 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- US1 is the MVP - deliver first for quick feedback
