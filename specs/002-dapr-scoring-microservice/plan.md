# Implementation Plan: [FEATURE]

**Branch**: `002-dapr-scoring-microservice` | **Date**: 2026-04-14 | **Spec**: spec.md
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Package the archi-c4-score library as a containerized Dapr microservice running on Python 3.12 distroless. The service exposes FastAPI endpoints with Dapr sidecar for service invocation and state management. Local development uses podman-compose. Production deploys to Azure Container Apps.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12 (distroless)  
**Primary Dependencies**: archi-c4-score library, dapr/sdk-python, FastAPI + Uvicorn  
**Storage**: Dapr State Store (Redis or in-memory for local dev)  
**Testing**: pytest  
**Target Platform**: Linux server (Podman local, Azure Container Apps production)  
**Project Type**: single microservice  
**Performance Goals**: TBD (performance not critical for initial implementation)  
**Constraints**: Distroless container (no shell), Dapr sidecar required, structured logging  
**Scale/Scope**: Single service, multiple deployments (local, staging, production)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Validation |
|-----------|-------------|-----------|
| IX. Test-First Development | Tests MUST be written before implementation using pytest | WILL_VERIFY: unit tests exist before implementation |
| X. Contract Testing Mandate | Contract tests REQUIRED for inter-service protocols | WILL_VERIFY: contract tests for API endpoints |
| XIX. Distroless Container Security | All container images MUST use Distroless base images | WILL_VERIFY: Distroless base image in Dockerfile |
| V. Distributed Applications with Dapr | Dapr building blocks MUST be used for service invocation, state management | WILL_VERIFY: Dapr SDK integration present |
| XIV. FastAPI-First API Design | All HTTP APIs MUST be defined using FastAPI | WILL_VERIFY: FastAPI routes defined |
| XVIII. Local Deployment (Podman) | Local development MUST use Podman | WILL_VERIFY: podman-compose.yml present |
| XI. Observability by Default | Structured logs with required fields | WILL_VERIFY: structured logging implemented |

**Status**: PASS (all gates achievable)

## Project Structure

### Documentation (this feature)

```text
specs/002-dapr-scoring-microservice/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/archi-c4-score/      # Existing library (archi-c4-score)
src/scoring-dapr/         # NEW: Dapr microservice
├── __init__.py
├── main.py               # FastAPI app with Dapr integration
├── config.py             # Configuration management
├── routes/
│   ├── __init__.py
│   └── score.py         # Scoring endpoints
├── services/
│   ├── __init__.py
│   └── scoring.py       # Scoring service wrapper
└── logging.py           # Structured logging

tests/
├── unit/
│   └── test_scoring_dapr.py
├── contract/
│   └── test_api_contracts.py
└── integration/
    └── test_dapr_scoring.py

compose.yaml              # Podman Compose for local dev
Dockerfile               # Distroless container build
```

**Structure Decision**: Dapr microservice builds on existing archi-c4-score library. Service runs as container with Dapr sidecar. Uses podman-compose for local development with Neo4j and Redis state store.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
