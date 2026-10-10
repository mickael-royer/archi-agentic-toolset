# Feature Specification: IcePanel Model Source

**Feature Branch**: `006-icepanel-model-source`
**Created**: 2026-10-11
**Status**: Draft
**ADR**: 0031 Score architecture from the IcePanel C4 model (supersedes 0028)
**Input**: "IcePanel is now the C4 referential (ADR 0030). Score the architecture from IcePanel instead of the Archi export, keep the same coupling metrics, track scores per IcePanel version, and expose scoring to the CLI/API, the Hugo dashboard and the Claude Code harness (/arch-check) through an MCP server."

## Assumptions

- IcePanel REST API v1 (`https://api.icepanel.io/v1`), authenticated with `X-API-Key`; same endpoints as the backend RAG ingestion (`python-service/app/kb.py`).
- Sync/async is carried by an IcePanel tag group named `Interaction` with tags `Sync` and `Async`. Untagged connections are sync.
- Weights and coupling band are the ones the legacy Neo4j path already uses: sync 1.5, async 1.0, band 30/40/50/60/70.
- The legacy ArchiMate path keeps its current output.

## C4 mapping

| IcePanel object type | C4 level | Scored |
|---|---|---|
| `system` (internal) | System | consolidated from its containers |
| `app`, `store` | Container | yes |
| `component` | Component | yes |
| `actor`, `group`, `root`, external objects | none | no, dependency endpoint only |

## User Scenarios & Testing

### US1 - Score the current IcePanel landscape (P1)

As an architect, I run `archi-c4 score --source icepanel` and get a system score, per-container and per-component scores.

1. **Given** a landscape with apps and components, **When** scoring runs, **Then** each internal app/store gets Ca, Ce, instability, coupling and composite = 100 - coupling.
2. **Given** a connection tagged `Async`, **When** scoring runs, **Then** it weighs 1.0 instead of 1.5.
3. **Given** a component-to-component connection across two apps, **When** container scores are computed, **Then** it counts for both parent apps; **Given** one inside a single app, **Then** it does not count for container coupling.
4. **Given** a `bidirectional` connection, **Then** it counts as a dependency in both directions.
5. **Given** `future` connections, **Then** they are ignored unless `--include-future`; `removed` connections and objects are always ignored.

### US2 - Compare two IcePanel versions (P1)

As the architecture-reviewer agent, I call `compare_versions(from, to)` and get the system delta and per-container deltas (added, removed, changed).

### US3 - Timeline by version (P2)

`archi-c4 dashboard --source icepanel --format hugo` scores each landscape version and the latest draft, and writes `timeline.json` with real `c4_scoring` and treemap data.

### US4 - API (P2)

`POST /api/v1/score` with `{"source": "icepanel", "version": "latest"}` returns real scores (contract in `contracts/score-api.md`).

### US5 - MCP server (P1)

`archi-c4-mcp` (stdio) exposes read-only tools `score_landscape`, `compare_versions`, `list_versions`.

## Requirements

- FR-001: model sources implement a `ModelSource` protocol returning `C4ConversionResult`; scoring has no IcePanel special case.
- FR-002: the coupling band is a single function shared by the legacy Neo4j path and the in-memory scorer.
- FR-003: secrets come from env (`ICEPANEL_API_KEY`, `ICEPANEL_LANDSCAPE_ID`, optional `ICEPANEL_VERSION_ID`); never logged.
- FR-004: the IcePanel client follows `nextCursor` pagination.
- FR-005: the MCP server and CLI are read-only towards IcePanel.

## Success Criteria

- Golden test: a fixture landscape gives fixed expected scores.
- Characterization test: legacy band output unchanged.
- `archi-c4 score --source icepanel` works against the real Unicorn landscape.
