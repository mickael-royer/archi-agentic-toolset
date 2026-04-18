# Quick Start: C4 Architecture Scoring Engine

## Test Scenarios

### Scenario 1: Container-Level Scoring (US1)
Test that each container receives an individual score.

```bash
# 1. Import a repository with Archimate model
archi-c4 import https://github.com/example/archimate-repo

# 2. Get container scores
curl "http://localhost:8000/scores/container?repository_url=https://github.com/example/archimate-repo"
```

Expected: Response with container scores for each container in the model.

### Scenario 2: System-Level Consolidation (US2)
Test system-level score aggregation.

```bash
curl "http://localhost:8000/scores/system?repository_url=https://github.com/example/archimate-repo"
```

Expected: Response with aggregated system score.

### Scenario 3: Timeline Tracking (US3)
Test score history over commits.

```bash
curl "http://localhost:8000/scores/timeline?repository_url=https://github.com/example/archimate-repo&limit=50"
```

Expected: Response with score history for up to 50 commits.

### Scenario 4: API Access (US4)
Test API endpoint availability.

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/scores/container?repository_url=https://github.com/example/repo"
```

### Scenario 5: Export (US5)
Test export file generation.

```bash
curl "http://localhost:8000/scores/export?repository_url=https://github.com/example/repo&format=timeline,trends"
```

### Scenario 6: Treemap (US6)
Test treemap data structure.

```bash
curl "http://localhost:8000/scores/treemap?repository_url=https://github.com/example/repo"
```

## Running Tests

```bash
# Unit tests
pytest tests/unit/

# Contract tests
pytest tests/contract/

# Integration tests
pytest tests/integration/
```

## Local Deployment

```bash
# Start services
podman-compose -f deploy/docker-compose.yaml up -d

# Check status
podman ps

# View logs
podman logs deploy_scoring-service_1

# Stop services
podman-compose -f deploy/docker-compose.yaml down
```