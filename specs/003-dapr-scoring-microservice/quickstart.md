# Quickstart: Dapr Scoring Microservice

## Prerequisites

- Podman installed
- Python 3.12+
- `uv` package manager

## Local Development Setup

### 1. Clone and Install Dependencies

```bash
cd src
uv sync
```

### 2. Build Container Image

```bash
cd deploy
podman build -t scoring-service:latest .
```

### 3. Start with Podman Compose

```bash
podman-compose up -d
```

This starts:
- `scoring-service`: The FastAPI application
- `dapr`: Dapr sidecar (slim mode)
- `neo4j`: Graph database (for scoring data)

### 4. Verify Health

```bash
curl http://localhost:8000/health
# {"status": "healthy"}

curl http://localhost:3500/v1.0/healthz
# "ok" (Dapr sidecar)
```

### 5. Test Scoring API

```bash
# Score at a commit
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"commit": "abc123"}'

# Get cached result
curl http://localhost:8000/api/v1/model/abc123
```

## Development Commands

```bash
# Run tests
cd src && uv run python -m pytest tests/

# Run linter
cd src && uv run ruff check .

# Type check
cd src && uv run mypy src/archi_c4_score/

# Local run without container
cd src && uv run uvicorn archi_c4_score.api:app --reload
```

## Stop Services

```bash
podman-compose down
```

## Production Deployment

See `deploy/README.md` for Azure Container Apps deployment with Dapr.
