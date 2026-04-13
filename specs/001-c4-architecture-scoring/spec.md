# Feature Specification: C4 Graph Scoring

**Feature Branch**: `001-c4-architecture-scoring`  
**Created**: 2026-04-13  
**Status**: Draft  
**Input**: Retrieve architecture model, extract C4 model, store to graph database, and score based on complexity and dependency using shared metrics

## User Scenarios & Testing

### User Story 1 - Retrieve Architecture Model from Repository (Priority: P1)

As an architect, I want to retrieve architecture models from a version-controlled repository so that I can analyze the current state of the architecture.

**Why this priority**: Without repository access, no other workflows can proceed. This is the foundation for all subsequent operations.

**Independent Test**: Can be fully tested by providing a repository path and verifying the architecture model is retrieved and parsed correctly.

**Acceptance Scenarios**:

1. **Given** a valid repository path containing architecture models, **When** the user invokes the retrieval command, **Then** the system returns the architecture model in a standardized format.
2. **Given** an invalid or inaccessible repository path, **When** the user attempts retrieval, **Then** the system returns an appropriate error with guidance.

---

### User Story 2 - Extract C4 Model from ArchiMate Model (Priority: P2)

As an architect, I want to extract a C4 model from an ArchiMate model by mapping Application Components to C4 levels based on their Stereotype Attributes, so that I can analyze the architecture at different levels of abstraction.

**Why this priority**: C4 model extraction enables meaningful architecture analysis at System, Container, and Component levels.

**Independent Test**: Can be fully tested by submitting an ArchiMate model and verifying correct C4 level assignment based on Stereotype Attributes.

**Acceptance Scenarios**:

1. **Given** an ArchiMate model with Application Components, **When** extraction is invoked, **Then** each Application Component is mapped to the correct C4 level based on its Stereotype: `<<Software System>>` maps to Software System, `<<Container>>` maps to Container, `<<Component>>` maps to Component.
2. **Given** an Application Component without a Stereotype Attribute, **When** extraction is invoked, **Then** the component is skipped and a warning is logged.
3. **Given** the extracted C4 model, **When** extraction completes, **Then** the system displays the C4 hierarchy with element counts per level.

---

### User Story 3 - Store C4 Model in Graph Database (Priority: P3)

As an architect, I want to store the extracted C4 model in a graph database so that I can perform complex queries and analyze relationships between architecture elements over time.

**Why this priority**: Graph database storage enables efficient querying of architecture relationships and supports historical analysis.

**Independent Test**: Can be fully tested by storing a C4 model and verifying all nodes and edges are correctly persisted and queryable.

**Acceptance Scenarios**:

1. **Given** an extracted C4 model, **When** the user invokes the store command, **Then** all C4 nodes are persisted with their properties to the graph database.
2. **Given** the C4 model with relationships, **When** storage completes, **Then** all edges are persisted with correct source, target, and weight attributes.
3. **Given** a previously stored C4 model, **When** the user queries the graph database, **Then** the system returns the complete C4 hierarchy with relationships.

---

### User Story 4 - Score Architecture Based on Complexity and Dependency (Priority: P4)

As an architect, I want to score architecture models based on complexity and dependency relationships so that I can identify areas of technical risk and prioritize refactoring efforts.

**Why this priority**: Scoring provides actionable insights for architecture improvement decisions.

**Independent Test**: Can be fully tested by providing a C4 model with known relationships and verifying the calculated scores match expected values.

**Acceptance Scenarios**:

1. **Given** a C4 model with dependencies, **When** scoring is invoked, **Then** the system calculates complexity scores using the defined dependency weights: trigger (asynchronous) = 1, flow-to (synchronous) = 3.
2. **Given** the scored architecture, **When** the user views results, **Then** scores are displayed per C4 level (Software System, Container, Component) with drill-down capability.
3. **Given** components with high complexity scores, **When** recommendations are generated, **Then** the system identifies the top 5 areas for architecture improvement.

---

### Edge Cases

- What happens when the repository contains no valid architecture model files?
- How does the system handle Application Components with unknown Stereotype values?
- What occurs when the graph database is unavailable during store operation?
- How are circular dependencies handled in the scoring calculation? (Circular dependencies receive a complexity penalty)
- What happens when scoring is requested for an empty C4 model?

## Requirements

### Functional Requirements

- **FR-001**: System MUST support retrieving architecture models from a version-controlled repository
- **FR-002**: System MUST parse ArchiMate models in coArchi2 export format
- **FR-003**: System MUST extract C4 model elements by mapping Application Components to C4 levels using the Stereotype Attribute
- **FR-004**: System MUST map Stereotype values as follows: `<<Software System >>` → Software System, `<<Container>>` → Container, `<<Component>>` → Component
- **FR-005**: System MUST skip Application Components with unknown Stereotype values and log a warning for each skipped element
- **FR-006**: System MUST store C4 models in a graph database with nodes and weighted edges
- **FR-007**: System MUST calculate architecture scores based on dependency complexity
- **FR-008**: System MUST apply dependency weights: trigger (asynchronous) = 1, flow-to (synchronous) = 3
- **FR-009**: System MUST produce scores at three C4 levels: Software System, Container, Component
- **FR-010**: System MUST provide actionable recommendations for components with high complexity scores
- **FR-011**: System MUST link stored C4 models to their source Git commit SHA for historical comparison
- **FR-012**: System MUST provide both CLI and REST API interfaces for all operations
- **FR-013**: System MUST detect circular dependencies and apply a complexity penalty while including them in score calculation

### Key Entities

- **Architecture Model**: Represents the source ArchiMate model retrieved from repository, containing elements and relationships
- **C4 Element**: A node in the extracted C4 model with level (Software System, Container, Component), name, and properties
- **C4 Relationship**: An edge between C4 elements representing dependencies with weight based on relationship type
- **Complexity Score**: A numeric value (0-100) representing the architectural complexity at a given C4 level
- **Scoring Report**: The output containing scores per C4 level, top complexity concerns, and recommendations
- **Git Commit**: A reference to a specific commit SHA in the source ArchiMate repository, linking stored C4 models to their version for historical comparison

## Success Criteria

### Measurable Outcomes

- **SC-001**: Architects can retrieve and parse architecture models from a repository in under 30 seconds for models with up to 500 elements
- **SC-002**: C4 model extraction correctly maps 100% of Application Components with valid Stereotype Attributes to their corresponding C4 level
- **SC-003**: Graph database queries return C4 hierarchy data in under 5 seconds for models with up to 1000 nodes
- **SC-004**: Scoring calculations complete in under 10 seconds for architectures with up to 500 dependencies
- **SC-005**: Score reports highlight at least one actionable recommendation for architectures with a Composite Score below 70

## Assumptions

- Repository format: coArchi2 Git-based repository structure
- Graph database: Neo4j (confirmed)
- Scoring algorithm: Weighted sum of dependency complexities, normalized to 0-100 scale
- Trigger relationship: Represents asynchronous communication between components (weight: 1)
- Flow-to relationship: Represents synchronous communication between components (weight: 3)

## Clarifications

### Session 2026-04-13

- Q: Dependency weights for trigger vs flow-to? → A: trigger=1 (asynchronous, lighter weight), flow-to=3 (synchronous, heavier weight)
- Q: How should C4 model versions be tracked? → A: Git commit linked - each store operation records the Git commit SHA from the ArchiMate repository for historical comparison
- Q: What interface should be provided? → A: CLI + REST API - both command-line interface and HTTP API for programmatic access
- Q: How handle unknown stereotypes? → A: Skip element - elements with unknown stereotypes are ignored and not included in the C4 model
- Q: How should circular dependencies affect scoring? → A: Apply penalty - add a complexity penalty for cycles while still including them in score calculation

## Scoring Metrics

This feature uses shared scoring metrics derived from 001-architecture-scoring.

### Scoring Dimensions

| Dimension | Weight | Description |
|----------|--------|-------------|
| Coupling | 30% | Measure of inter-dependencies using Instability Index |
| Modularity | 20% | How well the architecture is decomposed into distinct units |
| Cohesion | 20% | How related the components within each unit are |
| Extensibility | 15% | Ease of adding new functionality without modifying existing code |
| Maintainability | 15% | Overall ease of making changes |

### Instability Index Calculation

Using Robert C. Martin's formula: `I = Ce / (Ca + Ce)`
- **Ce (Efferent)**: Outgoing dependencies (out-degree in directed graph)
- **Ca (Afferent)**: Incoming dependencies (in-degree in directed graph)
- **I = 0**: Maximally stable (depended upon, no dependencies)
- **I = 1**: Maximally unstable (depends on others, nothing depends on it)

### Dependency Complexity Weights

| Relationship Type | Weight | Description |
|------------------|--------|-------------|
| flow-to | 3 | Synchronous communication |
| trigger | 1 | Asynchronous communication |
| other | 1.5 | Default weight |

### Score Aggregation

Scores aggregate upward: Component → Container → System
- Component scores average to Container score
- Container scores average to System score
- Composite score = weighted average of dimension scores
