# ArchiToolset

Architecture scoring and analysis toolkit for C4 models. The source of truth is the IcePanel
landscape (ADR 0030, 0031); ArchiMate models are a legacy, read-only source.

## Features

### IcePanel Model Source (006-icepanel-model-source)

Scores the C4 model read from the IcePanel REST API, per landscape version.

| IcePanel object | C4 level | Scored |
|---|---|---|
| `system` (internal) | System | consolidated from its containers |
| `app`, `store` | Container | yes |
| `component` | Component | yes |
| `actor`, `group`, external objects | - | no, dependency endpoint only |

Connections carry sync/async through the IcePanel tag group **`Interaction`** with tags **`Sync`**
and **`Async`**. Untagged connections count as sync. Bidirectional connections count both ways.
Component connections roll up to their container; connections inside one container don't count for
container coupling. Only `live`/`deprecated` items are scored, `--include-future` adds `future` ones.

```bash
cp .env.example .env            # set ICEPANEL_API_KEY and ICEPANEL_LANDSCAPE_ID
uv run archi-c4 score            # latest draft
uv run archi-c4 versions
uv run archi-c4 compare-versions <version-id> latest
uv run archi-c4 dashboard --source icepanel --format hugo --output ../../../unicorn-hugo-website
uv run archi-c4-mcp              # read-only MCP server (stdio): score_landscape, compare_versions, list_versions
```

### C4 Architecture Scoring (005-c4-scoring-engine)

Refactored model loader to convert Archimate elements to C4 entities (Software System, Container, Component). Architecture score defined at Container level and consolidated at Software System level. Complexity assessment based on afferent/efferent coupling with distinct weight between synchronous (Flow) and asynchronous (Trigger) relations. Scoring evolution tracked based on commit history for timeline review. Dashboard access via API. Export for timeline, trends, and recommendations. Detailed treemap representation by container/component.

**Scoring Formula** (`scoring.py`: `SYNC_WEIGHT`, `ASYNC_WEIGHT`, `coupling_band`):
- Sync relations (ArchiMate Flow, IcePanel `Sync` or untagged): weight = 1.5
- Async relations (ArchiMate Triggering, IcePanel `Async`): weight = 1.0
- weighted = sum of weights of distinct incoming and outgoing relations
- coupling = 30 (≤1), 40 (≤3), 50 (≤6), 60 (≤10), 70 (>10); composite = 100 - coupling
- instability I = Ce / (Ca + Ce); system score = mean container composite, -10% if containers form a cycle

### C4 Component Filtering

The scoring engine filters ArchiMate elements to only include C4-relevant components:

| ArchiMate Type | Stereotype | C4 Level |
|----------------|------------|----------|
| ApplicationComponent | "Container" | Container |
| ApplicationComponent | "Software System" / "SoftwareSystem" | Software System |
| ApplicationFunction | "Component" | Component |

All other elements are excluded from scoring to focus on software architecture.

### Scoring Process

1. **Import Model**: Fetch `model.archimate` from GitHub raw URL
2. **Parse Elements**: Extract elements with stereotype properties
3. **Store in Neo4j**: Save elements with stereotype attribute
4. **Query C4 Components**: Filter elements based on type + stereotype
5. **Calculate Scores**: Compute coupling and composite scores
6. **Generate Treemap**: Create visualization data with stereotype labels
7. **Serve Dashboard**: Provide JSON API with timeline and treemap data

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

### Import Model

```bash
# Import from raw GitHub URL (model.archimate file)
curl -X POST "http://localhost:8000/api/v1/import" \
  -H "Content-Type: application/json" \
  -d '{"model_url": "https://raw.githubusercontent.com/owner/repo/main/model.archimate"}'
```

### Trigger Scoring (Backfill)

```bash
# Score all commits in repository history
curl -X POST "http://localhost:8000/api/v1/scoring/backfill?repository_url=https://github.com/owner/repo&commit_count=10"
```

### View Dashboard

```bash
# Get dashboard JSON with treemap
curl "http://localhost:8000/api/v1/dashboard?repository_url=https://github.com/owner/repo"
```

### View Timeline

```bash
archi-c4 timeline --repo-url https://github.com/example/repo
```

### Generate Dashboard

```bash
archi-c4 dashboard --repo-url https://github.com/example/repo --format hugo --output ./hugo-site/
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/score` | Score a model source: `{"source": "icepanel", "version": "latest"}` |
| `POST /api/v1/import` | Import ArchiMate model from GitHub URL |
| `POST /api/v1/scoring/backfill` | Score historical commits |
| `GET /api/v1/dashboard` | Get dashboard with treemap data |
| `GET /api/v1/scores/timeline` | Get scoring timeline |
| `GET /api/v1/scores/treemap` | Get treemap visualization data |
| `GET /api/v1/scores/container` | Get container scores |

## Architecture

```
src/
├── archi_c4_score/    # Main library
│   ├── api.py         # FastAPI endpoints
│   ├── cli.py         # CLI commands
│   ├── graph.py      # Neo4j operations
│   ├── scoring.py     # Scoring engine
│   ├── treemap.py     # Treemap generation
│   ├── timeline.py    # Timeline analysis
│   ├── c4_converter.py # C4 entity conversion
│   ├── github_importer.py # GitHub model import
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
