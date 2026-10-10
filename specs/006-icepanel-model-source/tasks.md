# Tasks: IcePanel Model Source

**Feature**: 006-icepanel-model-source · **Spec**: spec.md · **Plan**: plan.md

## Phase 1: Safety net
- [X] T001 Characterization test of the legacy coupling band (tests/unit/test_legacy_coupling_characterization.py)
- [X] T002 Extract `coupling_band`, `SYNC_WEIGHT`, `ASYNC_WEIGHT` in src/archi_c4_score/scoring.py

## Phase 2: Model source (US1)
- [X] T003 `ModelSource` protocol + `ArchimateModelSource` (model_source.py)
- [X] T004 `IcePanelModelSource` + `to_c4` (icepanel_source.py)
- [X] T005 Fixture landscape (tests/fixtures/icepanel_landscape.json) and mapping tests

## Phase 3: Scoring (US1, US2)
- [X] T006 `C4ModelScorer` and `compare_reports` (scoring.py), Ca/Ce/instability on `ContainerScore`
- [X] T007 Golden scores test (tests/unit/test_icepanel_source.py)

## Phase 4: Integration (US2-US5)
- [X] T008 scoring_service.py shared by CLI/API/MCP
- [X] T009 CLI `score`, `compare-versions`, `versions`, `dashboard --source icepanel`
- [X] T010 API `POST /api/v1/score` contract + contract tests
- [X] T011 MCP server `archi-c4-mcp` + tests
- [X] T012 `.env.example`, README

## Phase 5: Harness and model (outside this repo)
- [ ] T013 Register `archi-scoring` in workspace `.mcp.json`, update architecture-reviewer, `make score`
- [ ] T014 IcePanel: create tag group `Interaction` (Sync/Async) and tag connections
