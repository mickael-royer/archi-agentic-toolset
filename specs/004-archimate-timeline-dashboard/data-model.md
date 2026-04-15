# Data Model: ArchiMate Timeline Dashboard

**Date**: 2026-04-15
**Feature**: 004-archimate-timeline-dashboard

## Entities

### ScoredCommit

Represents a commit with its architecture score data.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | str | Unique identifier (UUID) | Required |
| commit_sha | str | Git commit SHA | Required, 40 chars |
| repository_url | str | Source repository URL | Required |
| commit_date | datetime | When commit was made | Required |
| author | str | Commit author name | Required |
| message | str | Commit message | Optional |
| composite_score | float | Overall score (0-100) | Required, 0-100 |
| coupling_score | float | Coupling dimension (0-100) | Required |
| modularity_score | float | Modularity dimension (0-100) | Required |
| cohesion_score | float | Cohesion dimension (0-100) | Required |
| extensibility_score | float | Extensibility dimension (0-100) | Required |
| maintainability_score | float | Maintainability dimension (0-100) | Required |
| element_count | int | Number of elements in model | Required, >= 0 |
| relationship_count | int | Number of relationships | Required, >= 0 |
| scored_at | datetime | When scoring occurred | Required |

**Relationships**:
- `STORED_IN` → Repository
- `HAS_ELEMENT` → C4Element (existing)
- `NEXT_COMMIT` → ScoredCommit (ordered by date)

---

### TimelinePoint

A point in the timeline representing a scored commit with trend context.

| Field | Type | Description |
|-------|------|-------------|
| position | int | Position in timeline (0-indexed) |
| scored_commit | ScoredCommit | Reference to scored commit |
| score_delta | float | Change from previous point (null for first) |
| is_significant | bool | Whether delta exceeds threshold |
| delta_threshold | float | Threshold used for significance |

---

### TrendLine

Calculated trend for a scoring dimension.

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| dimension | str | Scoring dimension name | coupling, modularity, etc. |
| direction | TrendDirection | Trend direction | INCREASING, DECREASING, STABLE |
| slope | float | Linear regression slope | negative/positive |
| confidence | float | R² correlation coefficient | 0-1 |

**State Machine**:
```
TrendDirection: INCREASING | DECREASING | STABLE
  - STABLE: |slope| < threshold (default 0.1)
  - INCREASING: slope > 0.1
  - DECREASING: slope < -0.1
```

---

### ScoreDelta

Represents a significant score change between commits.

| Field | Type | Description |
|-------|------|-------------|
| magnitude | float | Absolute score change |
| direction | str | "improvement" or "degradation" |
| affected_dimensions | list[str] | Dimensions with notable changes |
| commit | ScoredCommit | The commit that introduced the change |

---

### CommitDiff

Element and relationship changes between two commits.

| Field | Type | Description |
|-------|------|-------------|
| from_commit | ScoredCommit | Earlier commit |
| to_commit | ScoredCommit | Later commit |
| elements_added | list[C4Element] | Elements in to but not from |
| elements_removed | list[C4Element] | Elements in from but not to |
| elements_modified | list[ElementDiff] | Common elements with changes |
| relationships_added | list[C4Relationship] | New dependencies |
| relationships_removed | list[C4Relationship] | Removed dependencies |
| relationships_modified | list[RelationshipDiff] | Changed relationships |

**ElementDiff**:
| Field | Type | Description |
|-------|------|-------------|
| element | C4Element | The element reference |
| changes | dict | Field name → old/new value |

**RelationshipDiff**:
| Field | Type | Description |
|-------|------|-------------|
| relationship | C4Relationship | Reference |
| old_weight | float | Previous weight |
| new_weight | float | New weight |

---

### DashboardReport

Generated output containing timeline visualization data.

| Field | Type | Description |
|-------|------|-------------|
| generated_at | datetime | Report generation time |
| repository_url | str | Source repository |
| repository_name | str | Extracted repo name |
| time_range | TimeRange | First to last commit |
| health_status | HealthStatus | IMPROVING, DECELING, STABLE |
| commits_analyzed | int | Count of commits |
| timeline_data | list[TimelinePoint] | Chronological points |
| trends | list[TrendLine] | Per-dimension trends |
| significant_changes | list[ScoreDelta] | Notable score deltas |
| top_concerns | list[Concern] | Top 3 architectural concerns |

**HealthStatus**:
- IMPROVING: Majority of trends show score improvement
- DECLINING: Majority of trends show score degradation
- STABLE: Trends roughly balanced

**TimeRange**:
| Field | Type | Description |
|-------|------|-------------|
| start | datetime | Earliest commit |
| end | datetime | Latest commit |
| commit_count | int | Number of commits |

**Concern**:
| Field | Type | Description |
|-------|------|-------------|
| dimension | str | Affected dimension |
| description | str | Human-readable concern |
| magnitude | float | Severity (0-100) |
| introduced_at | str | Commit SHA |

---

## Schema Extensions (Neo4j)

### New Node Labels

```cypher
// ScoredCommit node
(:ScoredCommit {
  commit_sha: String,
  repository_url: String,
  commit_date: DateTime,
  author: String,
  message: String,
  composite_score: Float,
  coupling_score: Float,
  modularity_score: Float,
  cohesion_score: Float,
  extensibility_score: Float,
  maintainability_score: Float,
  element_count: Integer,
  relationship_count: Integer,
  scored_at: DateTime
})
```

### New Relationships

```cypher
// Commit ordering
(sc1:ScoredCommit)-[:NEXT_COMMIT]->(sc2:ScoredCommit)

// Repository linkage
(sc:ScoredCommit)-[:STORED_IN]->(r:Repository)
```

### Indexes

```cypher
CREATE INDEX scored_commit_repo_date IF NOT EXISTS
FOR (sc:ScoredCommit) ON (sc.repository_url, sc.commit_date);

CREATE INDEX scored_commit_sha IF NOT EXISTS
FOR (sc:ScoredCommit) ON (sc.commit_sha);
```

## API Models (Pydantic)

See `contracts/timeline-api.yaml` for OpenAPI schema.

## Hugo Output Schema

```json
// data/timeline.json
{
  "$schema": "https://architoolset.dev/schemas/timeline-v1.json",
  "generated": "2026-04-15T10:00:00Z",
  "repository": {
    "url": "https://github.com/example/repo",
    "name": "repo"
  },
  "summary": {
    "health_status": "STABLE",
    "commits_analyzed": 30,
    "date_range": {
      "start": "2026-03-01T00:00:00Z",
      "end": "2026-04-15T00:00:00Z"
    }
  },
  "commits": [...],
  "trends": [...],
  "concerns": [...]
}
```
