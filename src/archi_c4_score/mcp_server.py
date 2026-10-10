"""Read-only MCP server (stdio) exposing architecture scoring to the Claude Code harness (ADR 0031).

Used by the architecture-reviewer agent (/arch-check) to report per-container score deltas.
"""

from dataclasses import asdict
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from archi_c4_score import scoring_service

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=True)

server = MCPServer(
    name="archi-scoring",
    instructions=(
        "Architecture scoring of the IcePanel C4 model (Unicorn). Composite score is 0-100, "
        "higher is better; coupling 30-70, sync connections weigh 1.5, async 1.0. "
        "To check a change: compare_versions(<last published version>, 'latest'), or "
        "score_landscape(include_future=True) for modelled-but-not-live changes."
    ),
)


@server.tool(annotations=READ_ONLY)
def score_landscape(version: str = "latest", include_future: bool = False) -> dict[str, Any]:
    """Score an IcePanel landscape version: system, container and component scores."""
    model_source = scoring_service.build_source("icepanel", include_future)
    return scoring_service.score_to_dict(model_source, "icepanel", version)


@server.tool(annotations=READ_ONLY)
def compare_versions(
    from_version: str, to_version: str = "latest", include_future: bool = False
) -> dict[str, Any]:
    """Per-container composite deltas between two IcePanel versions (added/removed/changed)."""
    model_source = scoring_service.build_source("icepanel", include_future)
    return scoring_service.compare_versions(model_source, from_version, to_version)


@server.tool(annotations=READ_ONLY)
def list_versions() -> list[dict[str, Any]]:
    """IcePanel landscape versions, oldest first. Use an id as from_version in compare_versions."""
    return [asdict(v) for v in scoring_service.build_source("icepanel").list_versions()]


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
