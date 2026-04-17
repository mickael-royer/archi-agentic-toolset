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

The composite score is a weighted average of five architecture quality dimensions, each scored 0-100 (higher is better).

| Dimension | Weight | Description |
|----------|--------|-------------|
| Coupling | 30% | Measure of inter-dependencies |
| Modularity | 20% | Architecture decomposition |
| Cohesion | 15% | Component relatedness |
| Extensibility | 15% | Ease of adding features |
| Maintainability | 20% | Overall changeability |

### Detailed Scoring Logic

#### Coupling (30% weight)
Measures dependencies between containers and components. Lower coupling = higher score.

**Calculation:**
```
instability = efferent / (efferent + afferent)
cycle_penalty = number_of_cycles * 5
score = 100 - (instability * 60) - cycle_penalty
```

- **Efferent coupling**: Number of outgoing dependencies
- **Afferent coupling**: Number of incoming dependencies
- **Cycle penalty**: Each dependency cycle reduces score by 5 points
- Score clamped to [0, 100]

#### Modularity (20% weight)
Measures how well components are grouped into containers.

**Calculation:**
```
size_score = max(0, 100 - variance_from_ideal * 10)
coverage = (grouped_components / total_components) * 100
score = (size_score * 0.5) + (coverage * 0.5)
```

- Ideal component distribution: `total_components / container_count`
- Components should have clear parent containers via composition/aggregation relationships

#### Cohesion (15% weight)
Measures how related components within a container are.

**Calculation:**
```
density = internal_relationships / possible_relationships
score = min(100, density * 100 + 20)
```

- Internal relationships are dependencies between components in the same logical group
- Possible relationships: `n * (n-1) / 2` where n = component count
- Baseline of 20 added to avoid penalizing sparse models

#### Extensibility (15% weight)
Measures how easy it is to add new components (abstraction and interface usage).

**Calculation:**
```
interfaces = elements with "interface" stereotype
abstractions = elements of type Interface/Abstract/Trait
abstraction_ratio = (interfaces + abstractions) / total_elements
score = min(100, max(30, abstraction_ratio * 500))
```

- Models with more interfaces and abstractions score higher
- Minimum score of 30 to avoid penalizing simple models

#### Maintainability (20% weight)
Measures overall code changeability based on complexity and structure.

**Calculation:**
```
size_penalty = min(30, avg_components_per_container * 5)
depth_penalty = min(20, dependency_depth * 5)
complexity_penalty = min(30, (relationships / elements) * 10)
score = 100 - size_penalty - depth_penalty - complexity_penalty
```

- **Size penalty**: Penalizes containers with too many components
- **Depth penalty**: Penalizes deep dependency chains
- **Complexity penalty**: Penalizes high relationship-to-element ratios

### Composite Score Formula

```
composite = (coupling * 0.30) + (modularity * 0.20) + (cohesion * 0.15) + (extensibility * 0.15) + (maintainability * 0.20)
```

## License

MIT
