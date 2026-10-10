"""MCP tools return the same contract as the API (specs/006 contracts/score-api.md)."""

from archi_c4_score import mcp_server


def test_score_landscape(icepanel_fixture_source):
    data = mcp_server.score_landscape()
    assert data["composite_score"] == 50.4
    assert {c["node_name"] for c in data["container_scores"]} >= {"Backend", "Frontend"}


def test_compare_versions_with_future(icepanel_fixture_source):
    diff = mcp_server.compare_versions("v1", "latest", include_future=True)
    rows = {r["name"]: r for r in diff["containers"]}
    # include_future applies to both sides: same model, no delta
    assert rows["File Process"]["status"] == "unchanged"


def test_list_versions(icepanel_fixture_source):
    assert [v["id"] for v in mcp_server.list_versions()] == ["v1", "v2"]


def test_tools_are_registered_read_only():
    import asyncio

    tools = asyncio.run(mcp_server.server.list_tools())
    names = {t.name for t in tools}
    assert names == {"score_landscape", "compare_versions", "list_versions"}
    assert all(t.annotations and t.annotations.read_only_hint for t in tools)
