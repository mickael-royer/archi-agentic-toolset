# ArchiToolset

Architecture scoring and analysis toolkit for ArchiMate models.

## Features

### C4 Architecture Scoring (001-c4-architecture-scoring)

Retrieve architecture models from version-controlled repositories, extract C4 models, store to Neo4j, and score based on complexity and dependency metrics.

### Dapr Scoring Microservice (002-dapr-scoring-microservice)

Containerized scoring service with Dapr integration for deployment on Podman (local) and Azure Container Apps (production).

### ArchiMate Timeline Dashboard (003-archimate-timeline-dashboard)

Track architecture changes over commit history and generate timeline dashboards with trend analysis.

## Installation

```bash
pip install archi-c4-score
```

Or install from source:

```bash
cd src
pip install -e .
```

## Quick Start

### Score a Repository

```bash
archi-c4 import https://github.com/example/archimate-repo
```

### View Timeline

```bash
archi-c4 timeline --repo-url https://github.com/example/repo
```

### Generate Dashboard

```bash
archi-c4 dashboard --repo-url https://github.com/example/repo --format hugo --output ./hugo-site/
```

## Architecture

```
src/
├── archi_c4_score/    # Main library
│   ├── api.py         # FastAPI endpoints
│   ├── cli.py         # CLI commands
│   ├── graph.py      # Neo4j operations
│   ├── scoring.py     # Scoring engine
│   ├── timeline.py    # Timeline analysis
│   └── hugo_export.py # Hugo integration
└── tests/             # Test suite
```

## Development

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

## Scoring Metrics

| Dimension | Weight | Description |
|----------|--------|-------------|
| Coupling | 30% | Measure of inter-dependencies |
| Modularity | 20% | Architecture decomposition |
| Cohesion | 20% | Component relatedness |
| Extensibility | 15% | Ease of adding features |
| Maintainability | 15% | Overall changeability |

## License

MIT
