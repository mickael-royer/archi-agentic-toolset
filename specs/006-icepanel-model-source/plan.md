# Implementation Plan: IcePanel Model Source

**Spec**: spec.md · **ADR**: 0031 · **Created**: 2026-10-11

## Technical context

Python 3.12+, existing deps (click, FastAPI, pydantic, python-dotenv) plus `mcp` (MCP SDK 2.x, `MCPServer`).
IcePanel REST v1 via stdlib `urllib` (no new HTTP client). No Neo4j needed for IcePanel scoring.

## Design

| Module | Role |
|---|---|
| `model_source.py` | `ModelSource` protocol (`load(version)`, `list_versions()`), `ArchimateModelSource` (legacy) |
| `icepanel_source.py` | `IcePanelModelSource` (REST, pagination, Interaction tags) and pure `to_c4()` mapping |
| `scoring.py` | `SYNC_WEIGHT`, `ASYNC_WEIGHT`, `coupling_band()` shared with the legacy Neo4j path; `C4ModelScorer`, `compare_reports()` |
| `scoring_service.py` | `build_source`, `score_to_dict`, `compare_versions`; loads the toolset `.env` |
| `cli.py` | `score --source`, `compare-versions`, `versions`, `dashboard --source icepanel` |
| `api.py` | `POST /api/v1/score` real scoring, Dapr cache only for named versions |
| `mcp_server.py` | stdio server `archi-scoring`, script `archi-c4-mcp` |

## Constitution / repo rules

- Formulas stay in `scoring.py`; README weight table updated in the same change.
- Legacy band pinned by `tests/unit/test_legacy_coupling_characterization.py` before extraction.
- IcePanel is a `ModelSource`, no special case in scoring.
