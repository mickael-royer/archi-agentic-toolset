# Quickstart: ArchiMate Timeline Dashboard

**Date**: 2026-04-16
**Feature**: 003-archimate-timeline-dashboard

## Overview

This feature generates architecture timeline dashboards for Hugo websites. It scores ArchiMate models across commit history and produces Hugo-compatible output with Chart.js visualizations.

## Prerequisites

- Docker/Podman
- Docker Compose/Podman Compose
- Git repository with `model.archimate` file

## Deployment

### Start Services

```bash
cd deploy
podman-compose up -d
```

Services:
- API: http://localhost:8000
- Neo4j: bolt://localhost:7687 (user: neo4j, password: architoolset)

## Workflow

### Step 1: Trigger Backfill

Before querying timeline, you must backfill scored commits:

```bash
curl -X POST "http://localhost:8000/api/v1/scoring/backfill?repository_url=https://github.com/mickael-royer/archimate-ear&commit_count=30"
```

This will:
1. Clone the repository to `/tmp/archi-model`
2. Iterate through commits
3. Score each commit with `*.archimate` files
4. Save scores to Neo4j

### Step 2: Query Timeline

```bash
curl "http://localhost:8000/api/v1/timeline?repository_url=https://github.com/mickael-royer/archimate-ear"
```

Response:
```json
{
  "repository_url": "https://github.com/mickael-royer/archimate-ear",
  "commits": [
    {
      "sha": "abc123",
      "date": "2024-01-01T12:00:00Z",
      "author": "John Doe",
      "composite_score": 75.0,
      "score_delta": null,
      "is_significant": false
    }
  ],
  "pagination": {
    "total": 4,
    "limit": 30,
    "offset": 0,
    "has_more": false
  }
}
```

### Step 3: Get Trends

```bash
curl "http://localhost:8000/api/v1/timeline/trends?repository_url=https://github.com/mickael-royer/archimate-ear"
```

### Step 4: Compare Commits

```bash
curl "http://localhost:8000/api/v1/timeline/compare?repository_url=https://github.com/mickael-royer/archimate-ear&from_commit=abc123&to_commit=def456"
```

### Step 5: Generate Dashboard

```bash
# JSON output
curl "http://localhost:8000/api/v1/dashboard?repository_url=https://github.com/mickael-royer/archimate-ear&output_format=json"

# Hugo output (generates files to output/ directory)
curl "http://localhost:8000/api/v1/dashboard?repository_url=https://github.com/mickael-royer/archimate-ear&output_format=hugo"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/timeline` | Get timeline data |
| GET | `/api/v1/timeline/trends` | Get trend analysis |
| GET | `/api/v1/timeline/compare` | Compare two commits |
| GET | `/api/v1/dashboard` | Generate dashboard report |
| POST | `/api/v1/scoring/backfill` | Trigger historical scoring |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://deploy_neo4j_1:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `architoolset` | Neo4j password |

## Hugo Integration

### Generated Output Structure

```
output/
├── data/
│   └── timeline.json          # Timeline data for Hugo
├── content/
│   └── architecture/
│       └── timeline-report.md
└── layouts/
    └── shortcodes/
        └── archi-timeline.html # Chart.js shortcode
```

### Usage in Hugo

```markdown
{{< archi-timeline >}}

## Trends

| Dimension | Trend | Status |
|-----------|-------|--------|
{{ range $data.trends }}
| {{ .dimension }} | {{ .direction }} | {{ if eq .direction "DECREASING" }}⚠️{{ else if eq .direction "INCREASING" }}✅{{ else }}➖{{ end }} |
{{ end }}
```

## Troubleshooting

### Empty Timeline

1. First run backfill:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/scoring/backfill?repository_url=<your-repo>"
   ```

2. Check logs for errors:
   ```bash
   podman logs <container-name>
   ```

3. Verify commits have `*.archimate` files

### Neo4j Connection Failed

1. Check Neo4j is running:
   ```bash
   podman ps | grep neo4j
   ```

2. Check container logs:
   ```bash
   podman logs deploy_neo4j_1
   ```

### Scoring Errors

Check logs for:
- "Failed to clone repository"
- "Failed to checkout commit"
- "Failed to score commit"
- "Failed to query Neo4j"

## Local Development

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run API
uv run uvicorn archi_c4_score.api:app --port 8000

# Run tests
uv run pytest tests/

# Lint
uv run ruff check src/ tests/
```

## Next Steps

1. Configure your repository URL
2. Trigger backfill: `POST /api/v1/scoring/backfill`
3. Query timeline: `GET /api/v1/timeline`
4. Generate Hugo output for your site
