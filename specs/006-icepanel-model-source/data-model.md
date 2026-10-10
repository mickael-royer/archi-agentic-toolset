# Data Model: IcePanel Model Source

Reuses `C4Node`, `C4Relationship`, `C4ConversionResult`, `ContainerScore`, `ComponentScore` (src/archi_c4_score/models.py, c4_converter.py).

## IcePanel -> C4

| IcePanel field | C4 field |
|---|---|
| modelObject.id | C4Node.id |
| modelObject.name | C4Node.name |
| modelObject.type | C4Node.c4_level (see spec mapping) |
| modelObject.parentId | C4Node.parent_id (only when the parent is mapped) |
| modelObject.external, caption, status | C4Node.properties |
| modelConnection.originId / targetId | C4Relationship.source_id / target_id |
| modelConnection.tagIds -> tag in group `Interaction` | C4Relationship.rel_type (`sync`/`async`) and weight (1.5/1.0) |
| modelConnection.name | C4Relationship.relationship_type |

`bidirectional` connections produce two `C4Relationship`s. Endpoints that are not mapped (actor, external system...) are kept as relationship endpoints so they count in Ca/Ce of the scored node; they get a node with `properties["scored"] = "false"`.

## Score per node

- Ca = number of distinct dependents, Ce = number of distinct dependencies (unweighted).
- weighted_total = sum of relationship weights touching the node (in + out).
- coupling = `coupling_band(weighted_total)`; composite = 100 - coupling.
- instability = Ce / (Ca + Ce), 0.5 when isolated (same as legacy component path).
- Container relationships = component relationships lifted to their container, plus direct container relationships; self-loops dropped.
- System score = mean of container composites, cycle penalty applied via `ScoringEngine.apply_cycle_penalty` when container dependencies have a cycle.

## Snapshot

`ScoringReport.git_commit` holds the IcePanel version id (or `latest`).
