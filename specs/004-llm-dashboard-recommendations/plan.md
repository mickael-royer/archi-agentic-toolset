# Implementation Plan: LLM Dashboard Recommendations

**Branch**: `004-llm-dashboard-recommendations` | **Date**: 2026-04-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-llm-dashboard-recommendations/spec.md`

## Summary

Add LLM-generated recommendations to the existing ArchiMate Timeline Dashboard based on architecture score trends. Use Google Gemini 2.0 API with function calling for structured JSON output. Integrate recommendations into existing dashboard API response, Hugo export, and CLI output.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: `google-genai`, `pydantic`, `FastAPI`, `cachetools`  
**Storage**: Neo4j (existing) + in-memory cache (LLM responses)  
**Testing**: pytest (existing) + new unit tests for llm_service  
**Target Platform**: Linux server (container)  
**Project Type**: Single Python library  
**Performance Goals**: <5 seconds for dashboard with LLM (from SC-003)  
**Constraints**: Graceful fallback when LLM unavailable  
**Scale/Scope**: Single repository per request, last 30 commits  

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Domain-Driven Design | ✅ | Recommendation/TrendContext as domain entities |
| II. Object-Oriented Design | ✅ | Classes with single responsibility |
| III. Code Quality | ✅ | SOLID, DRY, KISS, explicit error handling |
| VII. Library-First | ✅ | Self-contained llm_service module |
| VIII. CLI-First | ✅ | CLI with `--recommendations` flag |
| IX. Test-First | ✅ | Tests before implementation |
| X. Contract Testing | ✅ | API contracts for recommendations |
| XI. Observability | ✅ | Structured logging for LLM calls |
| XIII. Python Standards | ✅ | Type hints, docstrings, dataclasses |
| XIV. FastAPI-First | ✅ | FastAPI for HTTP API |

**Gate Result**: PASS - All principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/004-llm-dashboard-recommendations/
├── plan.md              # This file
├── research.md          # Phase 0 output (Gemini API research)
├── data-model.md        # Phase 1 output (entity definitions)
├── quickstart.md        # Phase 1 output (usage guide)
└── contracts/           # Phase 1 output (API schemas)
```

### Source Code (repository root)

```text
src/archi_c4_score/
├── __init__.py
├── llm_service.py           # NEW: Gemini API client + recommendation generation
├── models/
│   └── recommendations.py    # NEW: Pydantic models for recommendations
├── api.py                    # MODIFIED: DashboardResponse with recommendations
├── hugo_export.py           # MODIFIED: Add recommendations to Hugo export
└── cli.py                    # MODIFIED: Add --recommendations flag

tests/
├── unit/
│   └── test_llm_service.py  # NEW: Unit tests
└── contract/
    └── test_api.py           # MODIFIED: Add recommendation contracts
```

**Structure Decision**: Extend existing `archi_c4_score` library with new modules. No new projects needed.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | - | - |

## Phase 1: Design Artifacts

### Data Models

See [`data-model.md`](./data-model.md)

### API Contracts

See [`contracts/`](./contracts/)

### Quickstart

See [`quickstart.md`](./quickstart.md)

## Next Steps

1. Create data-model.md with entity definitions
2. Create contracts/ directory with API schemas
3. Create quickstart.md with usage examples
4. Run `/sp.tasks` to generate task breakdown
