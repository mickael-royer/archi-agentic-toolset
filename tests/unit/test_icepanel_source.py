"""IcePanel model source: mapping, sync/async weights, statuses, versions, and golden scores."""

import json
from pathlib import Path

import pytest

from archi_c4_score.icepanel_source import IcePanelModelSource, to_c4
from archi_c4_score.models import C4Level
from archi_c4_score.scoring import C4ModelScorer, compare_reports

FIXTURE = json.loads((Path(__file__).parents[1] / "fixtures" / "icepanel_landscape.json").read_text())


def fake_fetch(path: str, list_key: str, params: dict[str, str]) -> list[dict]:
    return FIXTURE[list_key]


@pytest.fixture
def source() -> IcePanelModelSource:
    return IcePanelModelSource("landscape", fake_fetch)


def _by_name(items, attr="node_name"):
    return {getattr(i, attr): i for i in items}


class TestMapping:
    def test_levels_and_parents(self, source):
        nodes = {n.id: n for n in source.load().nodes}
        assert nodes["sys"].c4_level == C4Level.SYSTEM
        assert nodes["backend"].c4_level == C4Level.CONTAINER
        assert nodes["state"].c4_level == C4Level.CONTAINER
        assert nodes["c-list"].c4_level == C4Level.COMPONENT
        assert nodes["c-list"].parent_id == "backend"
        assert "root" not in nodes and "old" not in nodes

    def test_external_and_actors_are_not_scored(self, source):
        nodes = {n.id: n for n in source.load().nodes}
        assert nodes["gdrive"].properties["scored"] == "false"
        assert nodes["user"].properties["scored"] == "false"
        assert nodes["backend"].properties["scored"] == "true"

    def test_system_id(self, source):
        assert source.load().system_id == "sys"

    def test_async_tag_weight(self, source):
        rels = {(r.source_id, r.target_id): r for r in source.load().relationships}
        assert rels[("c-list", "c-process")].weight == 1.0
        assert rels[("c-list", "c-process")].rel_type == "async"
        assert rels[("c-list", "gdrive")].weight == 1.5
        assert rels[("c-drive", "backend")].rel_type == "sync"  # untagged = sync

    def test_bidirectional_counts_both_ways(self, source):
        pairs = {(r.source_id, r.target_id) for r in source.load().relationships}
        assert ("c-publish", "state") in pairs and ("state", "c-publish") in pairs

    def test_status_filter(self, source):
        pairs = {(r.source_id, r.target_id) for r in source.load().relationships}
        assert ("c-process", "c-list") not in pairs  # future
        assert ("frontend", "publish") not in pairs  # removed
        assert ("old", "backend") not in pairs  # removed origin

    def test_include_future(self):
        future = IcePanelModelSource("landscape", fake_fetch, include_future=True)
        pairs = {(r.source_id, r.target_id) for r in future.load().relationships}
        assert ("c-process", "c-list") in pairs

    def test_no_interaction_group_means_all_sync(self):
        result = to_c4(FIXTURE["modelObjects"], FIXTURE["modelConnections"], set())
        assert {r.weight for r in result.relationships} == {1.5}

    def test_versions_sorted_oldest_first(self, source):
        assert [v.id for v in source.list_versions()] == ["v1", "v2"]


class TestGoldenScores:
    """Expected values derived by hand in specs/006-icepanel-model-source/data-model.md rules."""

    @pytest.fixture
    def report(self, source):
        return C4ModelScorer().score(source.load(), version="v2")

    def test_containers(self, report):
        c = _by_name(report.container_scores)
        assert set(c) == {"Frontend", "Backend", "File Process", "File Publish", "Statestore"}
        # name: (Ca, Ce, coupling, instability)
        expected = {
            "Frontend": (1, 1, 40.0, 0.5),  # user->, ->backend : 3.0
            "Backend": (1, 2, 50.0, 2 / 3),  # 1.5 + 1.5 + 1.0 async = 4.0; intra Auth ignored
            "File Process": (1, 1, 40.0, 0.5),  # 1.0 + 1.0
            "File Publish": (2, 1, 50.0, 1 / 3),  # 1.0 + 1.5 + 1.5
            "Statestore": (1, 1, 40.0, 0.5),  # 1.5 + 1.5
        }
        for name, (ca, ce, coupling, instability) in expected.items():
            assert c[name].afferent_coupling == ca, name
            assert c[name].efferent_coupling == ce, name
            assert c[name].coupling == coupling, name
            assert c[name].composite == 100.0 - coupling, name
            assert c[name].instability_index == pytest.approx(instability), name
        assert c["Backend"].component_count == 2

    def test_components(self, report):
        c = _by_name(report.component_scores)
        assert c["List Files"].coupling == 50.0  # 1.5 + 1.0 + 1.5
        assert c["List Files"].parent == "Backend"
        assert c["Auth"].coupling == 40.0
        assert c["Auth"].instability_index == 0.0
        assert c["Publish"].coupling == 50.0

    def test_system_score_with_cycle_penalty(self, report):
        # mean(60, 50, 60, 50, 60) = 56, File Publish <-> Statestore cycle -> * 0.9
        assert report.composite_score == pytest.approx(50.4)
        assert report.git_commit == "v2"


class TestCompare:
    def test_compare_reports(self, source):
        before = C4ModelScorer().score(source.load(), "v1")
        future = IcePanelModelSource("landscape", fake_fetch, include_future=True)
        after = C4ModelScorer().score(future.load(), "latest")
        diff = compare_reports(before, after)
        rows = {r["name"]: r for r in diff["containers"]}
        # future callback File Process -> Backend: File Process 2.0 -> 3.5 crosses a band,
        # Backend 4.0 -> 5.5 stays in the same band
        assert rows["File Process"]["status"] == "changed"
        assert rows["File Process"]["delta"] == -10.0
        assert rows["Backend"]["status"] == "unchanged"
        assert rows["Frontend"]["status"] == "unchanged"
        assert diff["from_version"] == "v1" and diff["to_version"] == "latest"
