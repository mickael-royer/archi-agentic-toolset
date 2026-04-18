# ArchiToolset Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-12

## Active Technologies
- Neo4j (graph database) (002-c4-architecture-scoring)
- Python 3.12+ (existing archi-c4-score library) + FastAPI, Dapr SDK, neo4j-driver, distroless/python3, podman-compose (002-dapr-scoring-microservice)
- Neo4j (existing), Dapr State Store (scaling metadata) (002-dapr-scoring-microservice)
- Python 3.12+ + neo4j-driver, networkx, click, pydantic, FastAPI (extends existing) (003-archimate-timeline-dashboard)
- Neo4j (existing graph database, extends scoring history) (003-archimate-timeline-dashboard)
- Python 3.12+ + neo4j-driver, networkx, FastAPI, pydantic, click (006-c4-scoring-engine)

- Python 3.12+ + networkx (graph algorithms), click (CLI framework), pydantic (data validation) (001-architecture-scoring)

## Project Structure

```text
src/
tests/
```

## Commands

```bash
uv run python -m pytest tests/unit/
uv run ruff check .
```

## Code Style

Python 3.12+: Follow standard conventions

## Recent Changes
- 006-c4-scoring-engine: Added Python 3.12+ + neo4j-driver, networkx, FastAPI, pydantic, click
- 003-archimate-timeline-dashboard: Added Python 3.12+ + neo4j-driver, networkx, click, pydantic, FastAPI (extends existing)
- 002-dapr-scoring-microservice: Added Python 3.12+ (existing archi-c4-score library) + FastAPI, Dapr SDK, neo4j-driver, distroless/python3, podman-compose


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
