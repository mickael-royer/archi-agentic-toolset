# Feature Specification: Architecture Scoring Agent

**Feature Branch**: `001-architecture-scoring`  
**Created**: 2026-04-12  
**Status**: Draft  
**Input**: Archimate model (via coArchi2 export structure) translated to C4 notation

## User Scenarios & Testing

### User Story 1 - Request Architecture Analysis (Priority: P1)

As a developer or architect, I want to submit a coArchi2 export of an Archimate model so that it is translated into a C4 representation (System, Container, Component layers) for automated scoring.

**Why this priority**: Core value proposition - without this, no other features matter.

**Independent Test**: Can be fully tested by submitting a sample coArchi2 structured Archimate model and receiving a score report mapped to C4 layers.

**Acceptance Scenarios**:

1. **Given** a coArchi2 export artifact, **When** the user invokes the scoring agent, **Then** the system returns aggregated architecture scores based on System, Container, and Component layers.
2. **Given** valid input, **When** scoring completes, **Then** detailed feedback is provided for each scored dimension.

---

### User Story 2 - Review Scoring Criteria (Priority: P2)

As a user, I want to understand what criteria are used for scoring so I can make informed architectural decisions.

**Why this priority**: Transparency builds trust and enables improvement.

**Independent Test**: Can be tested by requesting criteria documentation and verifying completeness.

**Acceptance Scenarios**:

1. **Given** the scoring agent is available, **When** a user requests scoring criteria, **Then** they receive a documented list of all scoring dimensions and their weights.

---

### User Story 3 - Track Score History (Priority: P3)

As a user, I want to track architecture scores over time so I can measure improvement or regression.

**Why this priority**: Historical tracking enables measuring progress and setting goals.

**Independent Test**: Can be tested by running scores at different points and verifying history is maintained.

**Acceptance Scenarios**:

1. **Given** previous scores exist, **When** a user requests their history, **Then** scores are displayed chronologically with change indicators.
2. **Given** multiple projects, **When** viewing history, **Then** scores are filterable by project.

---

### Edge Cases

- What happens when the input is empty or contains no analyzable architecture?
- What occurs if an "Application Component" in the model lacks the "Stereotype" attribute required for C4 mapping?
- How does the system handle malformed or unexpected coArchi2 export structures?
- What happens when scoring fails partially (e.g. mapping fails for some elements)?

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept Archimate models formatted according to the coArchi2 export structure
- **FR-002**: System MUST identify C4 elements by extracting "Application Component" entities and resolving their C4 type (System, Container, Component) strictly based on their "Stereotype" attribute
- **FR-003**: System MUST calculate and report architecture scores at three distinct C4 layer levels: System, Container, and Component
- **FR-004**: System MUST aggregate scores upward from the Component layer through the Container layer to the System layer
- **FR-004a**: System MUST produce a composite score (0-100 scale) based on multiple dimensions and aggregations
- **FR-004b**: System MUST base the primary component architecture score on Coupling metric evaluations
- **FR-004c**: System MUST provide dimension-level scores for: modularity, coupling, cohesion, extensibility, and maintainability
- **FR-004d**: System MUST calculate coupling using directed graphs (e.g. `networkx`), deriving an Instability Index (`i_index = ce / (ci + ce)`) from Efferent (`ce`, out-degree) and Afferent (`ci`, in-degree) edges
- **FR-004e**: System MUST apply complexity weights based on relationship type: "flow to" (synchronous) relations MUST be evaluated as strictly more complex than "trigger" (asynchronous) relations
- **FR-005**: System MUST document scoring criteria and their relative weights
- **FR-006**: System MUST support storing scores for historical comparison
- **FR-007**: System MUST support multiple programming languages and architecture patterns

### Key Entities

- **Score Report**: Contains composite score, aggregated scores by layer (System, Container, Component), dimensional breakdowns, timestamp, and recommendations
- **Layer Aggregation**: Represents the rollup of metric scores from sub-components to parent containers to system architectures
- **Archimate Element**: Specifically an "Application Component" node parsed from the coArchi2 structure
- **C4 Node**: The internal representation mapped via the "Stereotype" attribute (System, Container, Component)
- **Scoring Criteria**: Defines dimensions, weights, and evaluation rules
- **History Entry**: Links a score report to a point in time for a given artifact
- **Recommendation**: Suggests specific improvements with priority levels

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can complete an architecture scoring request in under 30 seconds for repositories under 1k files
- **SC-002**: Score reports provide actionable recommendations that address at least one dimension with a score below 70
- **SC-003**: Users can retrieve scoring criteria documentation in under 5 seconds
- **SC-004**: Historical scores are queryable by artifact with trend visualization
