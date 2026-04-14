# Implementation Plan: Dapr Scoring Microservice

**Branch**: `003-dapr-scoring-microservice` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)
**Input**: Deploy archi-c4-score as a Dapr microservice with local Podman + distroless deployment

## Summary

Package archi-c4-score library as a containerized Dapr microservice using FastAPI, deployable locally via Podman with distroless Python images.

## Technical Context

**Language/Version**: Python 3.12+ (existing archi-c4-score library)  
**Primary Dependencies**: FastAPI, Dapr SDK, neo4j-driver, distroless/python3, podman-compose  
**Storage**: Neo4j (existing), Dapr State Store (scaling metadata)  
**Testing**: pytest, dapr-test (for local Dapr testing)  
**Target Platform**: Linux containers (Podman), Azure Container Apps (production)  
**Project Type**: Microservice (Dapr sidecar pattern)  
**Performance Goals**: <100ms p95 latency for scoring requests  
**Constraints**: Distroless images (no shell), local Podman for dev  
**Scale/Scope**: Single microservice, horizontal scaling via Dapr

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| V. Dapr | ✅ REQUIRED | Dapr sidecar for service invocation, state management |
| VIII. CLI-First | ✅ COMPLIANT | archi-c4-score already has CLI |
| XIV. FastAPI-First | ✅ REQUIRED | Existing FastAPI api.py |
| XVIII. Podman | ✅ REQUIRED | Local container dev |
| XIX. Distroless | ✅ REQUIRED | gcr.io/distroless/python3 |

**Gate Result**: ✅ PASS - All requirements align with constitution

## Project Structure

### Documentation (this feature)

```text
specs/003-dapr-scoring-microservice/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI, Dapr pub/sub)
└── tasks.md             # Phase 2 output
```

### Source Code

```text
src/archi_c4_score/          # Existing library
├── api.py                   # FastAPI app (entry point)
├── cli.py                   # CLI entry point

deploy/
├── Dockerfile               # Distroless Python container
├── docker-compose.yaml      # Podman local dev (Dapr + Neo4j)
└── components/              # Dapr component specs
    ├── statestore.yaml
    └── pubsub.yaml

tests/
├── contract/                # Existing API contract tests
└── integration/              # Dapr integration tests
```

**Structure Decision**: Library-first (existing), microservice wraps library with Dapr sidecar. No new projects needed - add deploy/ directory.

## Complexity Tracking

No violations - structure follows existing patterns.
