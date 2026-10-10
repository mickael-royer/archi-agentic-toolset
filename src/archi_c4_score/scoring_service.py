"""Score a model source and serialise the result. Shared by the CLI, the API and the MCP server."""

from dataclasses import asdict
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from archi_c4_score.c4_converter import C4ConversionResult
from archi_c4_score.model_source import ArchimateModelSource, ModelSource
from archi_c4_score.models import ScoringReport
from archi_c4_score.scoring import C4ModelScorer, compare_reports

# Load the toolset's own .env whatever the current directory is (CLI, MCP stdio, uvicorn).
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def build_source(
    source: str = "icepanel", include_future: bool = False, model_path: str | None = None
) -> ModelSource:
    """Build a model source by name: 'icepanel' (default) or 'archimate' (legacy, needs a path)."""
    if source == "archimate":
        if not model_path:
            raise ValueError("the archimate source needs a model path")
        return ArchimateModelSource(model_path)
    if source == "icepanel":
        from archi_c4_score.icepanel_source import IcePanelModelSource

        return IcePanelModelSource.from_env(include_future=include_future)
    raise ValueError(f"unknown model source: {source}")


def score_version(
    model_source: ModelSource, version: str = "latest"
) -> tuple[ScoringReport, C4ConversionResult]:
    model = model_source.load(version)
    return C4ModelScorer().score(model, version=version), model


def report_to_dict(report: ScoringReport, model: C4ConversionResult, source: str) -> dict[str, Any]:
    """Serialise a report in the /api/v1/score contract shape (specs/006 contracts/score-api.md)."""
    system = next((n for n in model.nodes if n.id == model.system_id), None)
    return {
        "commit": report.git_commit,
        "source": source,
        "composite_score": report.composite_score,
        "system_scores": [
            {"node_id": system.id, "node_name": system.name, "composite": report.system_score}
        ]
        if system
        else [],
        "container_scores": [asdict(c) for c in report.container_scores],
        "component_scores": [asdict(c) for c in report.component_scores],
        "recommendations": [asdict(r) for r in report.recommendations],
        "scored_at": report.timestamp.isoformat(),
    }


def score_to_dict(model_source: ModelSource, source: str, version: str = "latest") -> dict[str, Any]:
    report, model = score_version(model_source, version)
    return report_to_dict(report, model, source)


def compare_versions(
    model_source: ModelSource, from_version: str, to_version: str = "latest"
) -> dict[str, Any]:
    before, _ = score_version(model_source, from_version)
    after, _ = score_version(model_source, to_version)
    return compare_reports(before, after)
