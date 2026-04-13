# Implementation Plan: C4 Graph Scoring

**Branch**: `001-c4-architecture-scoring` | **Date**: 2026-04-13 | **Spec**: [spec.md](./spec.md)

## Summary

Retrieve architecture models from coArchi2 repositories, extract C4 models via ArchiMate Stereotype mapping, store in Neo4j graph database, and score using complexity metrics (Instability Index with dependency weights).

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: 
- neo4j-driver (Neo4j Python driver with async)
- FastAPI (REST API)
- click (CLI framework)
- pydantic (data validation)

**Storage**: Neo4j (graph database)  
**Testing**: pytest with pytest-asyncio  
**Target Platform**: Linux/macOS  
**Project Type**: CLI library with REST API  
**Performance Goals**: Score models with 500 dependencies in under 10 seconds  
**Constraints**: <500MB memory, Neo4j connection required  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **VII. Library-First Architecture**: Standalone `archi-c4-score` library
- [x] **VIII. CLI-First Interface**: CLI with JSON + human output
- [x] **IX. Test-First Development**: pytest with TDD cycle
- [x] **X. Contract Testing Mandate**: CLI and API contract tests
- [x] **XI. Observability by Default**: Structured logging
- [x] **XII. Semantic Versioning**: MAJOR.MINOR.PATCH
- [x] **XIII. Python Standards**: Python 3.12+, type hints, dataclasses
- [x] **XIV. FastAPI-First API**: FastAPI for REST API

**Gate Status**: ✅ PASSED

## Architecture Sketch

```
┌─────────────────────────────────────────────────────────────────┐
│                      archi_c4_score                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  repository  │───▶│   parser    │───▶│   mapper     │     │
│  │  (git clone) │    │  (coArchi2)  │    │  (C4 levels) │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                  │                │
│                                                  ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   scoring    │◀───│   graph      │◀───│   neo4j      │     │
│  │  (metrics)  │    │  (cypher)    │    │  (storage)   │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐                          │
│  │     cli      │    │   fastapi    │                          │
│  │  (click)    │    │  (REST API)  │                          │
│  └──────────────┘    └──────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

### Documentation

```text
specs/002-c4-architecture-scoring/
├── plan.md              # This file
├── research.md          # Technical research
├── data-model.md        # Neo4j schema + Python models
├── quickstart.md        # User guide
├── contracts/           # CLI + REST API contracts
│   └── cli.md
└── tasks.md            # (/sp.tasks output)
```

### Source Code

```text
src/archi_c4_score/
├── __init__.py
├── cli.py              # click CLI
├── api.py              # FastAPI app
├── models.py           # Pydantic + dataclasses
├── parser.py           # coArchi2 parser
├── mapper.py           # C4 mapping
├── graph.py            # Neo4j operations
├── scoring.py          # Scoring engine
└── config.py          # Configuration

tests/
├── unit/
├── contract/
└── integration/
```

## Phase 0: Research ✅

Research completed in `research.md`:
- Neo4j with neo4j-driver for async Python integration
- Docker container for local development
- Parameterized Cypher queries for safety

## Phase 1: Design ✅

Design artifacts created:
- `data-model.md`: Neo4j schema, Python models
- `contracts/cli.md`: CLI commands, REST API endpoints
- `quickstart.md`: User guide with examples

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Next Steps

1. Run `/sp.tasks` to generate implementation task list
2. Implement in Red-Green-Refactor cycle
3. Maintain 80%+ test coverage
