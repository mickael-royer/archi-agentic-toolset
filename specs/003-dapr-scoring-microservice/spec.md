# Feature Specification: Dapr Scoring Microservice

## Overview

Package the archi-c4-score library as a containerized Dapr microservice for deployment on Podman (local) and Azure Container Apps (production).

## Requirements

1. **Containerization**: Python distroless image deployment
2. **Dapr Integration**: Service invocation, state management
3. **Local Dev**: Podman + podman-compose for local development
4. **API**: FastAPI HTTP endpoints with Dapr sidecar
5. **Observability**: Structured logging, health endpoints

## User Stories

### US1: Local Development
As a developer, I want to run the scoring service locally with `podman-compose up` so I can test integrations without cloud deployment.

### US2: Microservice Deployment
As an operator, I want to deploy the service with Dapr sidecar so I can leverage built-in observability, state management, and pub/sub.

### US3: Container Security
As a security engineer, I want distroless images so production containers have minimal attack surface.

## Technical Decisions

- **Runtime**: Python 3.12 distroless
- **Orchestration**: Dapr 1.x
- **Local Containers**: Podman + podman-compose
- **API**: FastAPI with Dapr HTTP binding
- **State**: Dapr State Store (Redis or in-memory for local dev)

## Dependencies

- archi-c4-score library (existing)
- dapr/sdk-python
- FastAPI + Uvicorn
- Distroless Python image

## Acceptance Criteria

1. `podman-compose up` starts Dapr sidecar + scoring service + Neo4j
2. Service responds to `/health` endpoint
3. `/api/v1/score` endpoint scores architecture via Dapr service invocation
4. Container image is distroless (no shell)
5. CI/CD validates container builds locally before deployment
