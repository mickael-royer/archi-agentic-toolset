# Data Model: C4 Architecture Scoring Engine

## Entities

### C4Node
A node in the C4 model hierarchy.

| Field | Type | Description |
|-------|------|-------------|
| id | str | Unique identifier |
| name | str | Display name |
| c4_level | C4Level | SYSTEM, CONTAINER, or COMPONENT |
| parent_id | str | Parent node ID (optional) |
| git_commit | str | Associated commit SHA |
| imported_at | datetime | Import timestamp |
| properties | dict | Additional properties |

### C4Relationship
A weighted relationship between C4 nodes.

| Field | Type | Description |
|-------|------|-------------|
| source_id | str | Source node ID |
| target_id | str | Target node ID |
| relationship_type | str | Flow (sync) or Trigger (async) |
| weight | float | Weight (1.0=Flow, 0.5=Trigger) |
| is_circular | bool | Whether relationship is circular |

### ContainerScore
Score data for a container.

| Field | Type | Description |
|-------|------|-------------|
| node_id | str | Container node ID |
| node_name | str | Container name |
| composite | float | Composite score (0-100) |
| coupling | float | Coupling score (0-100) |
| component_count | int | Number of components |

### ComponentScore
Score data for a component.

| Field | Type | Description |
|-------|------|-------------|
| node_id | str | Component node ID |
| node_name | str | Component name |
| composite | float | Composite score (0-100) |
| coupling | float | Coupling score (0-100) |
| instability_index | float | I = Ce / (Ca + Ce) |
| efferent_coupling | int | Outgoing dependencies |
| afferent_coupling | int | Incoming dependencies |

### ScoringReport
Comprehensive report for a software system.

| Field | Type | Description |
|-------|------|-------------|
| report_id | str | Unique report ID |
| timestamp | datetime | Report timestamp |
| git_commit | str | Commit SHA |
| composite_score | float | System-level composite |
| system_score | float | System aggregation |
| container_scores | list[ContainerScore] | Per-container scores |
| component_scores | list[ComponentScore] | Per-component scores |
| recommendations | list[Recommendation] | Improvement items |

### TreemapCell
Data for treemap visualization.

| Field | Type | Description |
|-------|------|-------------|
| id | str | Node ID |
| name | str | Node name |
| level | str | C4 level |
| score | float | Score for this node |
| size | int | Cell size (component count) |
| parent_id | str | Parent node ID |

## Enumerations

### C4Level
```
SYSTEM     = "System"
CONTAINER = "Container"
COMPONENT = "Component"
```

## Relationships

```
Software System (1) ──┬── (N) Container
Container (1) ──┬── (N) Component
C4Node (N) ──┬── (N) C4Relationship
```

## Validation Rules

- C4Level must be one of: SYSTEM, CONTAINER, COMPONENT
- Relationship weight must be: 1.0 (Flow) or 0.5 (Trigger)
- Scores must be between 0.0 and 100.0
- Container must have valid parent (Software System) or be root