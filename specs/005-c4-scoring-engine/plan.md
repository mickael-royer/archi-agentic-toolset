# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Refactor Archimate model loader to convert elements to C4 entities (Software System, Container, Component). Container-level architecture scoring with weighted sync/async coupling. Timeline tracking via commit history. Dashboard API access, export capability, and treemap visualization.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: neo4j-driver, networkx, FastAPI, pydantic, click  
**Storage**: Neo4j (existing), Dapr State Store  
**Testing**: pytest (existing)  
**Target Platform**: Linux server (containerized)  
**Project Type**: Python CLI + API service  
**Performance Goals**: API response <5s for 500 containers  
**Constraints**: No external system integration  
**Scale/Scope**: Up to 500 containers per software system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| IX. Test-First Development | ✅ Pass | Existing pytest in project |
| X. Contract Testing Mandate | ✅ Pass | API contracts will be defined in Phase 1 |
| XIV. FastAPI-First API Design | ✅ Pass | FastAPI required per User Story 4 |
| VIII. CLI-First Interface | ✅ Pass | Existing CLI with click |
| XVIII. Local Deployment (Podman) | ✅ Pass | podman-compose used for deployment |
| XIII. Python Standards | ✅ Pass | Python 3.12+, uv, type hints |

## Project Structure

### Documentation (this feature)

```text
specs/006-c4-scoring-engine/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/archi_c4_score/
├── __init__.py
├── api.py              # FastAPI endpoints (existing)
├── cli.py             # CLI commands (existing)
├── scoring.py         # ScoringEngine (existing)
├── archimate_scorer.py  # ArchimateScorer (existing)
├── archimate_xml_parser.py  # Model parsing (existing)
├── models.py          # Data models (existing)
├── graph.py          # Neo4j operations (existing)
├── hugo_export.py    # Hugo export (existing)
├── timeline.py       # Timeline analysis (existing)
└── repository.py    # Repository access (existing)

tests/
├── contract/         # API contract tests
├── integration/     # Integration tests
└── unit/           # Unit tests
```

**Structure Decision**: Single project extending existing archi-c4-score library. All new code follows existing package structure.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No violations | - |

## Phase 1 Summary

Successfully completed:
- ✅ Technical Context filled
- ✅ Constitution Check passed all gates
- ✅ Project Structure documented
- ✅ Phase 0: Research completed (research.md)
- ✅ Phase 1: Data model defined (data-model.md)
- ✅ Phase 1: API contracts defined (contracts/api.md)
- ✅ Phase 1: Agent context updated
