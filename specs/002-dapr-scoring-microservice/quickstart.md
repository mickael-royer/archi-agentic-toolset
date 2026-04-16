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
podman build -t scoring-service:latest -f deploy/Dockerfile .
```

Or using docker-compose:
```bash
podman-compose -f deploy/docker-compose.yaml build
```

### 3. Start with Podman Compose

```bash
podman-compose -f deploy/docker-compose.yaml up -d
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

## Troubleshooting

### Dapr Health Check Shows "Not Ready" but Service Works

If Dapr shows `ERR_HEALTH_NOT_READY` but scoring service is healthy, the issue is network connectivity between Dapr sidecar and the scoring service:

```bash
# Check metadata - look for channelAddress
curl -s http://localhost:3500/v1.0/metadata | jq .appConnectionProperties
# {"port":8000,"protocol":"http","channelAddress":"127.0.0.1"}  <- Problem
```

**Fix**: Add `--app-channel-address scoring-service` to the Dapr command in docker-compose.yaml. The container name gets resolved by Podman's internal DNS.

### Check Status

```bash
podman-compose ps
podman logs deploy_scoring-service_1
```

## Stop Services

```bash
podman-compose down
```

## Production Deployment

See `deploy/README.md` for Azure Container Apps deployment with Dapr.
