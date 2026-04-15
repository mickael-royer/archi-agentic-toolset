# archi-c4-score

C4 Architecture Scoring with Neo4j and ArchiMate timeline analysis.

## Installation

```bash
pip install archi-c4-score
```

## Usage

### Import and Score

```bash
archi-c4 import ./my-archimate-repo
archi-c4 score <commit-sha>
```

### Timeline Analysis

```bash
# View architecture score timeline
archi-c4 timeline --repo-url https://github.com/example/repo

# View trends
archi-c4 trends --repo-url https://github.com/example/repo

# Compare two commits
archi-c4 compare --repo-url https://github.com/example/repo --from-commit abc123 --to-commit def456

# Generate dashboard report
archi-c4 dashboard --repo-url https://github.com/example/repo --output ./dashboard.json
```

### Hugo Integration

Generate Hugo-compatible dashboard output:

```bash
archi-c4 dashboard --repo-url https://github.com/example/repo --format hugo --output ./hugo-site/
```

This generates:
- `data/timeline.json` - Timeline data for Hugo
- `layouts/shortcodes/archi-timeline.html` - Chart.js shortcode

Use in your Hugo content:

```markdown
{{< archi-timeline >}}
```

## API

Start the API server:

```bash
uvicorn archi_c4_score.api:app --port 8080
```

Endpoints:
- `GET /api/v1/timeline` - Get timeline data
- `GET /api/v1/timeline/trends` - Get trend analysis
- `GET /api/v1/timeline/compare` - Compare commits
- `GET /api/v1/dashboard` - Generate dashboard report
- `POST /api/v1/scoring/backfill` - Trigger historical scoring
