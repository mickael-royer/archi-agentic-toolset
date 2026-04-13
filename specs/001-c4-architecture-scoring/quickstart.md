# Quickstart: C4 Graph Scoring

**Feature**: 002-c4-architecture-scoring  
**Date**: 2026-04-13

## Installation

```bash
pip install archi-c4-score
```

Or from source:

```bash
git clone <repo>
cd archi-c4-score
pip install -e .
```

## Prerequisites

- Python 3.12+
- Neo4j (local Docker or Aura)

## Setup

```bash
# Start Neo4j locally
podman run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Set connection string
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
```

## Usage

### CLI

```bash
# Import architecture model from coArchi2 repository
archi-c4 import ./my-archimate-repo

# Score the imported model
archi-c4 score

# View history
archi-c4 history

# Query relationships
archi-c4 query "MATCH (c:Component)-[r]->() RETURN c.name, count(r) as deps"
```

### REST API

```bash
# Start server
archi-c4 serve --port 8000

# Import model
curl -X POST http://localhost:8000/api/v1/import \
  -H "Content-Type: application/json" \
  -d '{"repository_url": "./my-archimate-repo"}'

# Score
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"commit_sha": "abc123"}'
```

## Scoring Weights

| Relationship | Weight | Type |
|------------|--------|------|
| flow-to | 3 | Synchronous |
| trigger | 1 | Asynchronous |
| other | 1.5 | Default |

## Examples

See `examples/` directory for sample coArchi2 models.
