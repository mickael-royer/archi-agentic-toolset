# Dapr Scoring Microservice - Deployment Guide

## Local Development

### Prerequisites

- Podman installed
- Python 3.12+
- `uv` package manager

### Quick Start

```bash
# Build and start services
cd deploy
podman-compose up -d

# Verify health
curl http://localhost:8000/health

# Stop services
podman-compose down
```

### Services Started

| Service | Port | Description |
|---------|------|-------------|
| scoring-service | 8000 | FastAPI application |
| dapr | 3500 | Dapr sidecar |
| neo4j | 7687 | Graph database |

## Production Deployment

### Azure Container Apps

See `deploy/aca/README.md` for Azure deployment.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DAPR_API_TOKEN` | Dapr API token | - |
| `DAPR_GRPC_ENDPOINT` | Dapr gRPC endpoint | `localhost:50001` |
| `NEO4J_URI` | Neo4j connection | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/dapr/health` | GET | Dapr readiness |
| `/api/v1/score` | POST | Score architecture |
| `/api/v1/model/{commit}` | GET | Get C4 model |
| `/api/v1/history` | GET | Get import history |
