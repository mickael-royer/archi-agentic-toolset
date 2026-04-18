# Research: C4 Architecture Scoring Engine

## Decisions

### Decision 1: Scoring Formula

**Chosen**: Weighted sum formula with distinct sync/async weights
- Formula: `Score = w_sync × (Ca + Ce) + w_async × 0.5 × (Ca + Ce)`
- Sync (Flow) weight: 1.0
- Async (Trigger) weight: 0.5

**Rationale**: Asynchronous dependencies are lower coupling because they're temporal (event-driven), so they reduce the complexity impact by half compared to synchronous API calls which create tighter coupling.

**Alternatives considered**:
- Ca - Ce (instability): Too focused on dependency direction, ignores magnitude
- Summary(Ca + Ce) without weights: Doesn't differentiate sync from async

### Decision 2: Container-Level Scoring

**Chosen**: Score calculated at container level, consolidated at system level

**Rationale**: Container is the right granularity for architectural analysis because:
- It represents a deployable unit
- It's the level where coupling decisions matter most
- Components within containers are internal implementation details

### Decision 3: C4 Conversion via Stereotype

**Chosen**: Map Archimate Application elements to C4 based on Stereotype attribute

**Rationale**:
- Stereotype in Archimate already designed for this purpose
- SoftwareSystem, Container, Component stereotypes map directly to C4 levels

**Implementation**: Filter elements by stereotype attribute in existing archimate_scorer.py

## Phase 0 Summary

No additional research required. Feature extends existing scoring system with:
1. C4 entity mapping via Stereotype
2. Weighted coupling calculation (sync/async)
3. Container-level scoring granularity
4. API/Export/Treemap outputs (existing infrastructure)