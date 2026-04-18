# Feature Specification: C4 Architecture Scoring Engine

**Feature Branch**: `006-c4-scoring-engine`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "Refactor model loader to convert Archimate element to C4 entities and scoring engine to relies on resulting C4 model (Software System, Container, Component). Architecture score defined at Container level and consolidated at Software System level. Complexity assessment based on afferent/efferent coupling with distinct weight between sync and async relation. Async is less complex (lower coupling). Keep scoring evolution (track) based on commit history for timeline review. Dashboard access scoring result by API. Update dashboard export for timeline, trends and recommendation. Add detailled architecture score report by container/component with treemap representation."

## Assumptions

- Architecture models are stored in Archimate format with C4 entity types defined as Stereotype attributes on Application elements
- Architecture scores are treated as public data; no authentication required for API access

## User Roles & Personas

- **Software Architects**: Primary users who create and maintain architecture models; focus on detailed coupling metrics and improvement recommendations
- **Developers**: Consume architecture scores to understand component dependencies; use for refactoring decisions
- **Stakeholders**: View system-level health scores and trends; use for strategic architecture decisions
- C4 hierarchy: Software System contains multiple Containers, each Container contains multiple Components
- Relations between elements use Flow (synchronous API calls) or Trigger (asynchronous events)
- Scoring history is tracked through commit history timestamps
- Existing scoring metrics and data structures will be extended rather than replaced

## User Scenarios & Testing

### User Story 1 - View Architecture Scores by Container (Priority: P1)

As a user, I want to view the architecture quality score for each container in my software system so that I can identify areas requiring improvement.

**Why this priority**: Container-level scoring provides the most actionable insight for architects to understand coupling and complexity within their system boundaries.

**Independent Test**: Can be tested by loading a model with multiple containers and verifying each container receives a distinct score without requiring the full dashboard integration.

**Acceptance Scenarios**:

1. **Given** a software system with 3 containers, **When** the scoring engine processes the model, **Then** each container receives an individual score based on its afferent/efferent coupling
2. **Given** a container with both synchronous (Flow) and asynchronous (Trigger) relations, **When** scoring is calculated, **Then** asynchronous relations contribute less to the complexity score than synchronous ones
3. **Given** a container with no incoming or outgoing relations, **When** scoring is calculated, **Then** the container receives a neutral score indicating no coupling

---

### User Story 2 - View Consolidated Software System Score (Priority: P1)

As a user, I want to see an overall architecture score for the entire software system so that I can understand the overall health of my architecture.

**Why this priority**: System-level score provides a quick health indicator for stakeholders and enables tracking over time.

**Independent Test**: Can be tested by verifying the system score is calculated from container scores without requiring dashboard visualization.

**Acceptance Scenarios**:

1. **Given** a software system with multiple containers, **When** the scoring engine calculates the system score, **Then** the result reflects the aggregate of all container scores
2. **Given** a software system with containers having varying quality scores, **When** system score is calculated, **Then** the system score indicates the range of container scores

---

### User Story 3 - Track Score Evolution Over Time (Priority: P2)

As a user, I want to see how architecture scores change over time based on commit history so that I can identify trends and the impact of architectural decisions.

**Why this priority**: Historical tracking enables architects to measure the effect of their improvements and identify degradation patterns.

**Independent Test**: Can be tested by comparing scores at different commit timestamps without requiring timeline visualization.

**Acceptance Scenarios**:

1. **Given** multiple commits with architecture changes, **When** the timeline is generated, **Then** each snapshot shows scores at that point in time
2. **Given** a score improvement between commits, **When** the timeline is displayed, **Then** the improvement is visually indicated

---

### User Story 4 - Access Scores via Dashboard API (Priority: P1)

As a user, I want to retrieve architecture scores through a programmatic API so that I can integrate with other tools and automation pipelines.

**Why this priority**: API access enables integration with CI/CD pipelines and external monitoring systems.

**Independent Test**: Can be tested by calling the API endpoint and verifying JSON response structure without requiring UI.

**Acceptance Scenarios**:

1. **Given** a valid request to the scoring API, **When** the user requests container scores, **Then** the response includes scores for all containers in the software system
2. **Given** an invalid or missing model, **When** the user requests scores, **Then** the API returns an appropriate error message

---

### User Story 5 - Export Dashboard Reports (Priority: P2)

As a user, I want to export dashboard data including timeline, trends, and recommendations so that I can share reports with stakeholders.

**Why this priority**: Export capability enables offline analysis and stakeholder communication.

**Independent Test**: Can be tested by requesting export and verifying file contents match expected data structure.

**Acceptance Scenarios**:

1. **Given** a request for timeline export, **When** the export is generated, **Then** the file contains score history with timestamps
2. **Given** a request for trends export, **When** the export is generated, **Then** the file shows score progression over time

---

### User Story 6 - View Treemap Visualization (Priority: P3)

As a user, I want to see a treemap visualization of architecture scores by container and component so that I can quickly identify high-risk areas.

**Why this priority**: Treemap provides intuitive visual representation of architecture complexity and health.

**Independent Test**: Can be tested by generating treemap data structure without requiring full UI rendering.

**Acceptance Scenarios**:

1. **Given** a software system with containers and components, **When** the treemap is generated, **Then** each container and component is represented as a cell sized proportionally to its complexity
2. **Given** a component with a poor score, **When** the treemap is displayed, **Then** the cell is visually distinguished (color coding)

---

### Edge Cases

- What happens when a software system has no containers defined?
- How does the system handle orphaned components not assigned to any container?
- What happens when relation targets are missing or invalid?
- How are scores handled when there are no relations (both sync and async)?

## Requirements

### Functional Requirements

- **FR-001**: System MUST convert Archimate Application elements with C4 Stereotypes (SoftwareSystem, Container, Component) into C4 model entities
- **FR-002**: System MUST calculate architecture scores at the Container level based on afferent (incoming) and efferent (outgoing) coupling
- **FR-003**: System MUST apply lower weight to asynchronous (Trigger) relations compared to synchronous (Flow) relations when calculating complexity
- **FR-004**: System MUST consolidate Container scores into a Software System level score
- **FR-005**: System MUST track scoring history by commit timestamp to enable timeline review
- **FR-006**: System MUST provide API endpoint to retrieve scoring results for dashboard consumption
- **FR-007**: System MUST generate export data for timeline, trends, and recommendations
- **FR-008**: System MUST generate detailed score report with treemap data representing container and component scores

### Key Entities

- **Software System**: Top-level C4 entity representing the entire application; contains Containers; has consolidated score
- **Container**: C4 entity representing a deployable application component; contains Components; has individual score based on coupling
- **Component**: C4 entity representing a code module within a Container; contributes to Container complexity
- **Flow Relation**: Synchronous relationship between C4 entities (API calls); counted with full weight in complexity
- **Trigger Relation**: Asynchronous relationship between C4 entities (Events); counted with reduced weight in complexity
- **Score Snapshot**: Point-in-time record of architecture scores linked to a specific commit

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can retrieve container-level scores within 5 seconds of requesting the API
- **SC-002**: Scoring engine correctly differentiates sync (Flow) vs async (Trigger) relations with distinct weight application
- **SC-003**: Timeline displays score history for at least the last 50 commits with valid architecture changes
- **SC-004**: Treemap visualization accurately represents relative complexity through cell sizing based on coupling metrics
- **SC-005**: Export files contain complete data for timeline, trends, and recommendations without truncation for systems up to 500 containers
- **SC-006**: Dashboard API returns structured JSON that can be consumed by standard visualization libraries

### Dependencies

- Existing Archimate model loader and parser
- Existing commit history access
- Existing Neo4j graph database for scoring storage

### Risks

- C4 Stereotype naming convention must be consistently applied in source Archimate models
- Legacy models without proper Stereotype attributes may require migration

### Out of Scope

- External system integration (Jira, GitHub, CI/CD pipelines)
- Automated refactoring or code generation
- IDE integration or plugin support
- Security vulnerability scanning
- Real-time notifications or alerting

## Notes

- Scoring algorithm uses weighted afferent/efferent coupling with formula: Score = w_sync * (Ca + Ce) + w_async * 0.5 * (Ca + Ce)
  - Where Ca = afferent coupling (incoming relations), Ce = efferent coupling (outgoing relations), w_sync = 1.0, w_async = 0.5
- Treemap sizing uses component count and coupling intensity as primary factors

## Clarifications

### Session 2026-04-18

- Q: Should scoring API require authentication? → A: No auth required, public architecture scores (Option A)
- Q: Who are primary users? → A: Architects + developers + stakeholders (Option C)
- Q: Max scale (containers)? → A: Up to 500 containers (Option B)
- Q: What's not included? → A: No external system integration (Option C)
- Q: Scoring formula? → A: Summary(Ca + Ce) with weights (Option B)