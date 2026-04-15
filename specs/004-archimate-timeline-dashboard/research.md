# Research: ArchiMate Timeline Dashboard

**Date**: 2026-04-15
**Feature**: 004-archimate-timeline-dashboard

## Decisions

### Decision 1: Historical Scoring Approach

**Choice**: Auto-backfill last 30 commits on initial run, then incremental on new commits.

**Rationale**: 
- Provides immediate value with bounded initial cost
- Avoids expensive full-history backfill
- Establishes continuous monitoring pattern

**Alternatives considered**:
- Full backfill on first run (rejected: too expensive for large repos)
- User-triggered batch only (rejected: reduces automation value)

---

### Decision 2: Hugo Integration Format

**Choice**: Generate Hugo-compatible output as JSON data files, Markdown content, and Chart.js shortcodes.

**Rationale**:
- Hugo supports JSON data files in `/data/` directory
- Markdown content files for report structure
- Shortcodes enable reusable Chart.js components
- Allows CI/CD integration via `hugo new` or direct file generation

**Alternatives considered**:
- Single HTML file (rejected: breaks Hugo workflow)
- API-only with frontend (rejected: adds deployment complexity)

---

### Decision 3: Trend Calculation Algorithm

**Choice**: Linear regression for trend direction (increasing/decreasing/stable).

**Rationale**:
- Simple, explainable calculation
- Sufficient for "increasing/decreasing/stable" classification
- No ML complexity needed for 3-class output

**Alternatives considered**:
- Moving average smoothing (deferred: future enhancement)
- Exponential smoothing (deferred: future enhancement)

---

### Decision 4: Neo4j Schema Extension

**Choice**: Add `ScoredCommit` node with relationship to `C4Element` nodes.

**Rationale**:
- Existing graph structure already links elements to commits
- Query pattern: MATCH scored commits by repository, order by date
- Enables efficient timeline retrieval with Cypher

**Alternatives considered**:
- Separate time-series database (rejected: adds infrastructure)
- Flat file storage (rejected: loses graph query benefits)

---

### Decision 5: Significant Change Detection

**Choice**: Configurable threshold (default 10 points) applied to composite score.

**Rationale**:
- Simple, measurable criteria
- Aligns with scoring normalization (0-100 scale)
- Configurable for repository-specific tuning

**Alternatives considered**:
- Statistical anomaly detection (rejected: overkill for simple threshold)
- Per-dimension thresholds (deferred: future enhancement)

## Integration Patterns

### Git History Iteration

```python
# Pattern for iterating commits with git
result = subprocess.run(
    ["git", "log", "--format=%H", "-n", "30"],
    cwd=repo_path,
    capture_output=True,
    text=True,
)
commits = result.stdout.strip().split("\n")
```

### Neo4j Timeline Query

```cypher
MATCH (r:Repository {url: $url})<-[:STORED_IN]-(sc:ScoredCommit)
WHERE sc.scored_at >= $since
RETURN sc
ORDER BY sc.commit_date ASC
LIMIT $limit
```

### Hugo Data File Structure

```json
// data/timeline.json
{
  "generated": "2026-04-15T10:00:00Z",
  "repository": "https://github.com/example/repo",
  "commits": [
    {
      "sha": "abc123",
      "date": "2026-04-01T12:00:00Z",
      "author": "John Doe",
      "composite_score": 85.0,
      "dimensions": {...}
    }
  ]
}
```

## References

- Hugo Data Files: https://gohugo.io/templates/data-templates/
- Chart.js Shortcodes: https://gohugo.io/templates/shortcode-templates/
- Neo4j Cypher: https://neo4j.com/docs/cypher-manual/current/
- GitPython: https://gitpython.readthedocs.io/
