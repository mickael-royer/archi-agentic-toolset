# Feature Specification: ArchiMate Timeline Dashboard

**Feature Branch**: `004-archimate-timeline-dashboard`  
**Created**: 2026-04-15  
**Status**: Draft  
**Input**: User description: "Refactor Architectore Score service to assess Architecture Model changes based on commit history (eg. https://github.com/mickael-royer/archimate-ear/blob/main/model.archimate) to generate a dashboard with a timeline report"

## User Scenarios & Testing

### User Story 1 - View Architecture Change Timeline (Priority: P1)

As an architect, I want to see a timeline of architecture changes over time so that I can understand how the system has evolved and identify trends in complexity.

**Why this priority**: Without historical analysis, architects cannot understand architectural evolution or justify refactoring decisions with data.

**Independent Test**: Can be fully tested by providing a repository with multiple commits and verifying the timeline shows scores and changes at each point in time.

**Acceptance Scenarios**:

1. **Given** an ArchiMate repository with multiple scored commits, **When** the user requests the timeline view, **Then** the system displays scores chronologically from oldest to newest commit.
2. **Given** the timeline data, **When** the user views it, **Then** each data point includes the commit SHA, date, author, composite score, and key dimension scores.
3. **Given** a repository with changes between commits, **When** the user views the timeline, **Then** the system highlights significant score changes (positive or negative delta exceeding threshold).

---

### User Story 2 - Track Complexity Trends Over Time (Priority: P2)

As an architect, I want to track how architectural complexity changes across commits so that I can identify when and why the architecture became more complex.

**Why this priority**: Trend analysis helps identify problematic periods where complexity increased without corresponding business value, enabling better governance.

**Independent Test**: Can be fully tested by providing a repository with known complexity changes and verifying the trend line accurately reflects the expected direction.

**Acceptance Scenarios**:

1. **Given** a series of scored commits, **When** trend analysis is requested, **Then** the system calculates the direction (increasing/decreasing/stable) for each scoring dimension.
2. **Given** multiple scoring dimensions, **When** trends are displayed, **Then** each dimension (Coupling, Modularity, Cohesion, etc.) shows its own trend line.
3. **Given** the trend data, **When** the user views results, **Then** the system identifies the commits where the largest changes occurred.

---

### User Story 3 - Generate Dashboard Report (Priority: P3)

As an architect, I want to generate a dashboard report summarizing architecture health over time so that I can share findings with stakeholders and track improvement initiatives.

**Why this priority**: Stakeholder communication requires clear, visual representations of architecture health that non-technical audiences can understand.

**Independent Test**: Can be fully tested by requesting a dashboard report and verifying it contains all required sections and visualizations.

**Acceptance Scenarios**:

1. **Given** scored history data, **When** the user generates a dashboard report, **Then** the report includes a timeline chart showing score evolution.
2. **Given** the dashboard report, **When** it is generated, **Then** it includes a summary section with overall health status (Improving/Declining/Stable) and key metrics.
3. **Given** the dashboard report, **When** it is generated, **Then** it highlights top 3 concerns identified from historical analysis.
4. **Given** the dashboard report, **When** it is generated, **Then** it includes change detection showing which commits introduced significant architectural changes.

---

### User Story 4 - Compare Specific Commits (Priority: P4)

As an architect, I want to compare two specific commits side-by-side so that I can understand exactly what changed between them and why scores changed.

**Why this priority**: Detailed comparison enables root cause analysis of architectural degradation or improvement.

**Independent Test**: Can be fully tested by comparing two commits with known differences and verifying the diff accurately reflects element and relationship changes.

**Acceptance Scenarios**:

1. **Given** two commits in the scored history, **When** the user requests comparison, **Then** the system lists elements added, removed, and modified between the commits.
2. **Given** the comparison data, **When** the user views results, **Then** relationship changes (new dependencies, removed dependencies, weight changes) are displayed.
3. **Given** the comparison, **When** it is displayed, **Then** the system explains the scoring impact (e.g., "Coupling increased by X due to 3 new dependencies").

---

### Edge Cases

- What happens when the repository has only one commit with no history?
- How does the system handle gaps in the scoring history (commits that were not scored)?
- What occurs when architecture scores are identical across multiple consecutive commits?
- How are repositories with thousands of commits handled in timeline visualization?
- What happens when a commit cannot be parsed or scored (corrupted model file)?

## Requirements

### Functional Requirements

- **FR-001**: System MUST retrieve and score architecture models for all commits in a specified range (default: last 30 commits)
- **FR-002**: System MUST persist scored history with commit SHA, timestamp, author, and all dimension scores to enable historical queries
- **FR-003**: System MUST generate timeline data ordered chronologically showing score evolution
- **FR-004**: System MUST calculate trend direction (increasing/decreasing/stable) for each scoring dimension over the analyzed period
- **FR-005**: System MUST detect significant score changes exceeding a configurable threshold (default: 10 points delta)
- **FR-006**: System MUST identify commits associated with significant score changes
- **FR-007**: System MUST generate a dashboard report in Hugo-compatible format containing: timeline chart, trend summary, top concerns, and change detection
- **FR-008**: System MUST support comparison between any two commits in the scored history
- **FR-009**: System MUST list element-level changes (added/removed/modified) between two commits
- **FR-010**: System MUST explain scoring impact for each dimension change during comparison
- **FR-011**: System MUST handle gaps in scoring history gracefully, indicating which commits were not scored
- **FR-012**: System MUST support pagination for timeline data when repositories have large commit counts
- **FR-013**: System MUST export dashboard in standard formats (HTML for viewing, JSON for programmatic access)

### Key Entities

- **ScoredCommit**: A commit with its associated architecture score data, including composite score, dimension scores, and metadata (author, date, message)
- **TimelinePoint**: A single point in the timeline representing a ScoredCommit with its position in chronological order
- **TrendLine**: The calculated trend direction for a scoring dimension over the analyzed period
- **ScoreDelta**: A significant change in score between two commits, including the magnitude and affected dimensions
- **CommitDiff**: The element-level and relationship-level changes between two commits
- **DashboardReport**: The generated output containing timeline visualization, trend summary, concerns, and change detection

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can view a complete timeline of architecture scores for repositories with up to 100 commits in under 30 seconds
- **SC-002**: Trend analysis correctly identifies direction for 100% of analyzed scoring dimensions
- **SC-003**: Dashboard report generation completes in under 60 seconds for repositories with up to 100 scored commits
- **SC-004**: Commit comparison accurately identifies all element and relationship changes between two commits
- **SC-005**: Significant score changes (delta exceeding threshold) are identified with 100% accuracy compared to manual review

## Clarifications

### Session 2026-04-15

- Q: Dashboard report format and delivery? → A: Integrated into Hugo website (unicorn-hugo-website). Generate Hugo-compatible output (JSON data files, shortcodes, or content for `hugo new`).
- Q: Timeline visualization format? → A: Chart.js or similar JS library embedded via Hugo shortcode, with data loaded from JSON.
- Q: Historical commit scoring approach? → A: Auto-backfill last 30 commits on initial run, then incremental scoring on new commits.

## Assumptions

- Repository format: Git-based with model.archimate file in repository root
- Scoring history persists in Neo4j with commit SHA as the linking key (extending FR-011 from 001)
- Default score change threshold for "significant" detection: 10 points
- Timeline visualization: time-series chart via Hugo shortcode (Chart.js), data loaded from JSON
- Dashboard export: Hugo content/data files for site integration, plus raw JSON for programmatic access
- Significant change threshold applies to composite score by default
- Commits without model files or parse errors are skipped with warning logged
- Timeline pagination: default 30 commits per page, configurable
