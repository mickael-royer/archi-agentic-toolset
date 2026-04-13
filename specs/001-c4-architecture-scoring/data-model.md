# Data Model: C4 Graph Scoring

**Feature**: 002-c4-architecture-scoring  
**Date**: 2026-04-13

## Neo4j Graph Model

### Nodes

#### SoftwareSystem
```cypher
(:SoftwareSystem {
  id: string,
  name: string,
  git_commit: string,
  imported_at: datetime,
  properties: map
})
```

#### Container
```cypher
(:Container {
  id: string,
  name: string,
  parent_id: string,
  git_commit: string,
  imported_at: datetime,
  properties: map
})
```

#### Component
```cypher
(:Component {
  id: string,
  name: string,
  parent_id: string,
  git_commit: string,
  imported_at: datetime,
  properties: map
})
```

### Relationships

```cypher
(:Component)-[:DEPENDS_ON {
  relationship_type: string,
  weight: float,
  is_circular: boolean
}]->(:Component | :Container | :SoftwareSystem)
```

### Indexes

```cypher
CREATE INDEX software_system_id IF NOT EXISTS FOR (s:SoftwareSystem) ON (s.id);
CREATE INDEX container_id IF NOT EXISTS FOR (c:Container) ON (c.id);
CREATE INDEX component_id IF NOT EXISTS FOR (c:Component) ON (c.id);
CREATE INDEX git_commit IF NOT EXISTS FOR ()-[r]-() ON (r.git_commit);
```

## Python Data Models

### ArchimateModel (Input)
```python
@dataclass
class ArchimateModel:
    version: str
    elements: list[ArchimateElement]
    relationships: list[Relationship]
    metadata: ModelMetadata
```

### C4Node (Internal)
```python
@dataclass
class C4Node:
    id: str
    name: str
    c4_level: C4Level
    parent_id: str | None
    git_commit: str
    imported_at: datetime
```

### C4Relationship (Internal)
```python
@dataclass
class C4Relationship:
    source_id: str
    target_id: str
    relationship_type: str
    weight: float
    is_circular: bool = False
```

### ScoringReport (Output)
```python
@dataclass
class ScoringReport:
    report_id: str
    timestamp: datetime
    git_commit: str
    composite_score: float
    system_score: float
    container_scores: list[ContainerScore]
    component_scores: list[ComponentScore]
    recommendations: list[Recommendation]
```

## State Transitions

### Import Flow
```
coArchi2 JSON → Parse → C4 Mapping → Neo4j Import
```

### Scoring Flow
```
Git Commit → Query Graph → Calculate Metrics → Generate Report
```

### Version Tracking
```
Each import creates timestamped snapshot linked to git_commit
```
