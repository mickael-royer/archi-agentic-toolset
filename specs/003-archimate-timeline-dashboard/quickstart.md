# Quickstart: ArchiMate Timeline Dashboard

**Date**: 2026-04-15
**Feature**: 003-archimate-timeline-dashboard

## Overview

This feature generates architecture timeline dashboards for Hugo websites. It scores ArchiMate models across commit history and produces Hugo-compatible output with Chart.js visualizations.

## Prerequisites

- Python 3.12+
- `uv` package manager
- Neo4j database (running)
- Git repository with `model.archimate` file

## Installation

```bash
# Install from local development
cd /Users/royerm/Dev/ArchiToolset
uv pip install -e .
```

## CLI Usage

### Score Repository History

```bash
# Auto-backfill last 30 commits (default)
archi-c4-score score-history \
  --repo-url https://github.com/mickael-royer/archimate-ear \
  --neo4j-uri bolt://localhost:7687

# Custom commit range
archi-c4-score score-history \
  --repo-url https://github.com/mickael-royer/archimate-ear \
  --commit-count 50
```

### View Timeline

```bash
# Get timeline as JSON
archi-c4-score timeline \
  --repo-url https://github.com/mickael-royer/archimate-ear \
  --json

# View trends
archi-c4-score trends \
  --repo-url https://github.com/mickael-royer/archimate-ear
```

### Compare Commits

```bash
archi-c4-score compare \
  --repo-url https://github.com/mickael-royer/archimate-ear \
  --from abc123 \
  --to def456
```

### Generate Dashboard

```bash
# JSON output (programmatic)
archi-c4-score dashboard \
  --repo-url https://github.com/mickael-royer/archimate-ear \
  --output-format json \
  --output ./timeline-data.json

# Hugo output (for site integration)
archi-c4-score dashboard \
  --repo-url https://github.com/mickael-royer/archimate-ear \
  --output-format hugo \
  --output ./hugo-site/
```

## Hugo Integration

### Directory Structure

```
hugo-site/
├── data/
│   └── timeline.json          # Generated timeline data
├── content/
│   └── architecture/
│       └── timeline-report.md # Generated report content
└── layouts/
    └── shortcodes/
        └── archi-timeline.html # Chart.js shortcode
```

### Generated Output

#### `data/timeline.json`

```json
{
  "generated": "2026-04-15T10:00:00Z",
  "repository": {
    "url": "https://github.com/mickael-royer/archimate-ear",
    "name": "archimate-ear"
  },
  "summary": {
    "health_status": "STABLE",
    "commits_analyzed": 30,
    "date_range": {
      "start": "2026-03-01T00:00:00Z",
      "end": "2026-04-15T00:00:00Z"
    }
  },
  "commits": [
    {
      "sha": "abc123",
      "date": "2026-04-01T12:00:00Z",
      "author": "John Doe",
      "composite_score": 85.0,
      "dimensions": {
        "coupling": 82.0,
        "modularity": 88.0,
        "cohesion": 85.0,
        "extensibility": 80.0,
        "maintainability": 87.0
      },
      "element_count": 42,
      "relationship_count": 156,
      "score_delta": null,
      "is_significant": false
    }
  ],
  "trends": [
    {
      "dimension": "coupling",
      "direction": "DECREASING",
      "slope": -0.12,
      "confidence": 0.85
    }
  ],
  "significant_changes": [
    {
      "magnitude": 12.5,
      "direction": "improvement",
      "commit": "def456",
      "affected_dimensions": ["coupling", "maintainability"]
    }
  ],
  "concerns": [
    {
      "dimension": "modularity",
      "description": "Modularity score decreased 15 points in last 10 commits",
      "magnitude": 75,
      "introduced_at": "ghi789"
    }
  ]
}
```

#### `layouts/shortcodes/archi-timeline.html`

```html
{{ $data := index .Site.Data "timeline" }}
{{ if $data }}
<div class="archi-timeline">
  <canvas id="timelineChart"></canvas>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const commits = {{ $data.commits | jsonify }};
    const labels = commits.map(c => c.sha.substring(0,7));
    const scores = commits.map(c => c.composite_score);
    
    new Chart(document.getElementById('timelineChart'), {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Composite Score',
          data: scores,
          borderColor: '#3498db',
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: { min: 0, max: 100 }
        }
      }
    });
  </script>
</div>
{{ end }}
```

#### Usage in Markdown

```markdown
# Architecture Timeline

{{< archi-timeline >}}

## Trends

| Dimension | Trend | Status |
|-----------|-------|--------|
{{ range $data.trends }}
| {{ .dimension }} | {{ .direction }} | {{ if eq .direction "DECREASING" }}⚠️{{ else if eq .direction "INCREASING" }}✅{{ else }}➖{{ end }} |
{{ end }}
```

## API Usage

### Start the service

```bash
# Using Dapr
dapr run --app-id archi-timeline \
  --app-port 8080 \
  -- uv run uvicorn archi_c4_score.api:app

# Direct
uv run uvicorn archi_c4_score.api:app --port 8080
```

### Endpoints

```bash
# Get timeline
curl "http://localhost:8080/api/v1/timeline?repository_url=https://github.com/example/repo"

# Get trends
curl "http://localhost:8080/api/v1/timeline/trends?repository_url=https://github.com/example/repo"

# Compare commits
curl "http://localhost:8080/api/v1/timeline/compare?repository_url=https://github.com/example/repo&from_commit=abc123&to_commit=def456"

# Generate dashboard
curl "http://localhost:8080/api/v1/dashboard?repository_url=https://github.com/example/repo"

# Trigger backfill
curl -X POST "http://localhost:8080/api/v1/scoring/backfill?repository_url=https://github.com/example/repo"
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Architecture Timeline
on:
  push:
    branches: [main]

jobs:
  dashboard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install uv
      - run: uv pip install archi-c4-score
      - run: |
          archi-c4-score dashboard \
            --repo-url ${{ github.server_url }}/${{ github.repository }} \
            --output-format hugo \
            --output ./hugo-site/
      - uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
      - run: hugo -d ../public
```

## Troubleshooting

### Neo4j Connection Issues

```bash
# Check Neo4j is running
curl http://localhost:7474

# Verify connection
archi-c4-score health --neo4j-uri bolt://localhost:7687
```

### Empty Timeline

- Verify repository has commits with `model.archimate` files
- Check backfill completed: `archi-c4-score score-history --repo-url <url>`
- Review logs for parse errors

### Chart Not Rendering

- Ensure Hugo is in server mode or run `hugo`
- Check browser console for JavaScript errors
- Verify Chart.js CDN is accessible

## Next Steps

1. Configure repository URL in CLI or API
2. Run initial backfill: `archi-c4-score score-history --repo-url <url>`
3. Generate dashboard: `archi-c4-score dashboard --output-format hugo --output ./hugo-site/`
4. Commit Hugo output to your site repository
5. Add to CI/CD pipeline for automated updates
