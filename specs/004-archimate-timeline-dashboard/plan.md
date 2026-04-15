# Implementation Plan: ArchiMate Timeline Dashboard

**Branch**: `004-archimate-timeline-dashboard` | **Date**: 2026-04-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-archimate-timeline-dashboard/spec.md`

## Summary

Extend the existing `archi-c4-score` library to support architecture change analysis over commit history. The system will:
1. Auto-backfill scoring for last 30 commits on initial run
2. Persist scored history in Neo4j with commit SHA linking
3. Generate timeline data and trend analysis
4. Export Hugo-compatible dashboard with Chart.js visualization

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: neo4j-driver, networkx, click, pydantic, FastAPI (extends existing)  
**Storage**: Neo4j (existing graph database, extends scoring history)  
**Testing**: pytest (existing test framework)  
**Target Platform**: Linux server, CLI + API interface  
**Performance Goals**: Timeline for 100 commits in <30s (SC-001)  
**Constraints**: Score threshold 10 points default, pagination 30 per page  
**Scale/Scope**: Repositories up to 100+ commits, single model per commit  

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Library-First Architecture | ✅ PASS | Extends archi-c4-score library, new module `archi_c4_score/timeline.py` |
| CLI-First Interface | ✅ PASS | Existing CLI extended with `history`, `compare` commands |
| FastAPI-First API Design | ✅ PASS | Existing API extended with `/api/v1/timeline` endpoints |
| Python Standards | ✅ PASS | Uses uv, type hints, dataclasses per existing codebase |
| Test-First Development | ✅ PASS | Tests in `tests/unit/test_timeline.py`, `tests/contract/test_api.py` |
| Observability | ✅ PASS | Structured logging for all timeline operations |

**GATE**: All constitutional principles satisfied - Phase 0 research approved.

## Project Structure

### Documentation (this feature)

```text
specs/004-archimate-timeline-dashboard/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── timeline-api.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (existing library extension)

```text
src/
├── archi_c4_score/
│   ├── __init__.py
│   ├── cli.py           # Extended: history, compare commands
│   ├── api.py           # Extended: /timeline endpoints
│   ├── timeline.py      # NEW: Timeline generation, trend analysis
│   ├── hugo_export.py   # NEW: Hugo-compatible output
│   └── existing modules...
└── tests/
    ├── unit/
    │   └── test_timeline.py  # NEW
    ├── integration/
    │   └── test_pipeline.py  # Extended
    └── contract/
        └── test_api.py       # Extended

# Hugo output directory (generated)
output/
├── data/
│   └── timeline.json
├── content/
│   └── architecture/
│       └── timeline-report.md
└── layouts/
    └── shortcodes/
        └── archi-timeline.html
```

**Structure Decision**: Library extension to existing `archi-c4-score` project. New modules added for timeline (`timeline.py`, `hugo_export.py`). Existing CLI and API extended. Hugo output generated to configurable directory for CI/CD integration.

## Complexity Tracking

No violations requiring justification. All decisions align with existing architecture.

## Phase 0: Research

Completed inline - all technical decisions derived from existing codebase patterns and clarified requirements.

## Phase 1: Design

### Data Model (see data-model.md)

### API Contracts (see contracts/timeline-api.yaml)

### Hugo Integration (see quickstart.md)

## Implementation Phases

| Phase | Description | Key Deliverables |
|-------|-------------|------------------|
| 1 | Neo4j schema extension for scored history | Migration, repository methods |
| 2 | Timeline generation module | Score history retrieval, trend calculation |
| 3 | CLI commands | `history`, `compare` subcommands |
| 4 | API endpoints | `/api/v1/timeline/*` endpoints |
| 5 | Hugo export | JSON data files, shortcodes, template |
| 6 | Integration tests | End-to-end pipeline test |
