# Contracts: C4 Graph Scoring

**Feature**: 002-c4-architecture-scoring  
**Date**: 2026-04-13

## CLI Interface

### Commands

```bash
# Retrieve and import architecture model
archi-c4 import <repository-path> [--commit <sha>]

# Score an imported model
archi-c4 score [--commit <sha>] [--output <file>]

# Query graph
archi-c4 query <cql> [--params <json>]

# View history
archi-c4 history [--limit <n>]

# Export model
archi-c4 export [--format json|cypher] [--commit <sha>]
```

### Options

| Flag | Description |
|------|-------------|
| `--commit` | Specific git commit SHA |
| `--output` | Output file path |
| `--format` | Output format |
| `--limit` | Max results |

## REST API (FastAPI)

### Endpoints

```python
# Import model from repository
POST /api/v1/import
Body: {"repository_url": string, "commit_sha": string | null}
Response: {"import_id": string, "commit_sha": string, "nodes_count": int}

# Score a model
POST /api/v1/score
Body: {"commit_sha": string}
Response: ScoringReport

# Get C4 hierarchy
GET /api/v1/model/{commit_sha}
Response: {"software_systems": [...], "containers": [...], "components": [...]}

# Query relationships
POST /api/v1/query
Body: {"cypher": string, "params": object}
Response: {"results": [...]}

# Get history
GET /api/v1/history?limit=10
Response: {"entries": [...]}

# Get scoring criteria
GET /api/v1/criteria
Response: ScoringCriteria
```

### OpenAPI

Auto-generated via FastAPI at `/docs`
