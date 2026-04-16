# Research: Dapr Scoring Microservice Deployment

## 1. Dapr Integration with Python

### Decision
Use Dapr Python SDK with FastAPI HTTP binding

### Rationale
- Dapr provides HTTP endpoints for service invocation (`/v1.0/invoke/{app-id}/method/{method}`)
- Python SDK supports publish/subscribe, state management, and service invocation
- FastAPI can easily integrate with Dapr sidecar via middleware

### Alternatives Considered
- **gRPC**: More performant but adds complexity; HTTP sufficient for MVP
- **Dapr Cli**: Manual steps; SDK integration preferred for programmatic control

## 2. Distroless Python Container

### Decision
Use `gcr.io/distroless/python3` base image

### Rationale
- Minimal attack surface (no shell, package manager)
- Official Google distroless images for Python
- Multi-stage build keeps dev/build tools separate

### Dockerfile Pattern
```dockerfile
FROM python:3.12-slim AS builder
COPY src/ /app/
RUN pip install --target=/app/requirements.txt

FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app/ /app/
WORKDIR /app
CMD ["api.py"]
```

## 3. Podman Local Development

### Decision
Use `podman-compose` for local multi-container orchestration

### Rationale
- Rootless containers match constitution requirement
- docker-compose compatibility via podman-compose
- Dapr requires container runtime for sidecar injection

### docker-compose.yaml Structure
```yaml
services:
  scoring-service:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - dapr sidecar
    dapr:
      app-id: scoring-service
      port: 8000

  dapr:
    image: daprio/dapr:latest
    command: "./dapr init --slim"
    ports:
      - "3500:3500"
```

## 4. Dapr Building Blocks Used

| Building Block | Purpose |
|----------------|---------|
| Service Invocation | HTTP calls between services |
| State Management | Store scoring results, cache |
| Pub/Sub | Future: async scoring triggers |
| Secrets | Neo4j credentials via Dapr secrets |

## 5. Health Endpoint Pattern

### Decision
Implement `/health` + `/dapr/health` endpoints

### Rationale
- Kubernetes/Dapr liveness probes
- Dapr sidecar health checkable via sidecar injector

```python
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/dapr/health")
async def dapr_health():
    # Dapr calls this on sidecar startup
    return {"status": "dapr-ready"}
```

## 6. Azure Container Apps Deployment

### Decision
Use Dapr on Azure Container Apps (ACA)

### Rationale
- Native Dapr support in ACA
- Managed infrastructure per constitution
- Bicep IaC for declarative deployment

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to inject Dapr sidecar locally? | podman-compose with dapr cli |
| Distroless image entry point? | Multi-stage build with python:3.12-slim |
| Neo4j connection from Dapr? | Dapr secrets for credentials |
