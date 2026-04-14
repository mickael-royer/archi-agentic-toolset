# ArchiToolset Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-12

## Active Technologies
- Neo4j (graph database) (002-c4-architecture-scoring)
- Python 3.12+ (existing archi-c4-score library) + FastAPI, Dapr SDK, neo4j-driver, distroless/python3, podman-compose (003-dapr-scoring-microservice)
- Neo4j (existing), Dapr State Store (scaling metadata) (003-dapr-scoring-microservice)

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
- 003-dapr-scoring-microservice: Added Python 3.12+ (existing archi-c4-score library) + FastAPI, Dapr SDK, neo4j-driver, distroless/python3, podman-compose
- 002-c4-architecture-scoring: Added Python 3.12+

- 001-architecture-scoring: Added Python 3.12+ + networkx (graph algorithms), click (CLI framework), pydantic (data validation)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
