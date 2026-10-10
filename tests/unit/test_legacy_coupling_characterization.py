"""Characterization of the legacy ArchiMate (Neo4j) container/component scoring output.

Pins the current coupling band so extracting it into a shared function cannot change legacy scores.
"""

from unittest.mock import AsyncMock, patch

import pytest

from archi_c4_score.scoring import BackfillOrchestrator, ScoringEngine

# (flow_in, flow_out, trigger_in, trigger_out) -> expected coupling
CASES = [
    ((0, 0, 0, 0), 30.0),
    ((0, 0, 1, 0), 30.0),  # 1.0
    ((1, 0, 0, 0), 40.0),  # 1.5
    ((1, 0, 1, 0), 40.0),  # 2.5
    ((2, 0, 0, 0), 40.0),  # 3.0
    ((2, 0, 1, 0), 50.0),  # 4.0
    ((4, 0, 0, 0), 50.0),  # 6.0
    ((4, 0, 1, 0), 60.0),  # 7.0
    ((6, 0, 1, 0), 60.0),  # 10.0
    ((6, 1, 0, 0), 70.0),  # 10.5
]


def _record(flow_in: int, flow_out: int, trigger_in: int, trigger_out: int) -> dict:
    return {
        "node_id": "n1",
        "node_name": "N1",
        "stereotype": "Container",
        "afferent_coupling": flow_in + trigger_in,
        "efferent_coupling": flow_out + trigger_out,
        "flow_in": flow_in,
        "flow_out": flow_out,
        "trigger_in": trigger_in,
        "trigger_out": trigger_out,
        "parents": [],
    }


def _orchestrator() -> BackfillOrchestrator:
    return BackfillOrchestrator(scoring_engine=ScoringEngine(), repository=None)  # type: ignore[arg-type]


@pytest.mark.parametrize("counts,expected", CASES)
async def test_legacy_container_coupling_band(counts, expected):
    conn = AsyncMock()
    conn.execute_query.return_value = [_record(*counts)]
    with patch("archi_c4_score.graph.Neo4jConnection", return_value=conn):
        scores = await _orchestrator().get_container_scores("repo", "sha")
    assert scores[0].coupling == expected
    assert scores[0].composite == 100.0 - expected


@pytest.mark.parametrize("counts,expected", CASES)
async def test_legacy_component_coupling_band(counts, expected):
    conn = AsyncMock()
    conn.execute_query.return_value = [_record(*counts)]
    with patch("archi_c4_score.graph.Neo4jConnection", return_value=conn):
        scores = await _orchestrator().get_component_scores("repo", "sha")
    assert scores[0].coupling == expected
    assert scores[0].composite == 100.0 - expected
