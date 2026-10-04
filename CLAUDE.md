# archi-agentic-toolset

@AGENTS.md

Architecture scoring: model -> C4 entities -> coupling-based score, Neo4j graph, FastAPI + CLI (`archi-c4`).
Python managed with uv. Specs live in `specs/` and `.specify/` (Spec Kit).

## Commands
- Install: `uv pip install -e ".[dev]"`
- Test: `uv run pytest tests/`   Lint: `uv run ruff check src/ tests/`   Types: `uv run mypy src/`

## Rules
- Scoring formulas live in `src/archi_c4_score/scoring.py`. Changing weights or formulas requires updating
  the README tables and the golden test fixtures in the same commit.
- Do not change scoring output for the legacy ArchiMate path without a characterization test first.
- New model sources (IcePanel) implement the model-source interface, not special cases in scoring.
