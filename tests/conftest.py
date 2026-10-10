"""Shared fixtures."""

import json
from pathlib import Path

import pytest

from archi_c4_score.icepanel_source import IcePanelModelSource

ICEPANEL_FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "icepanel_landscape.json").read_text()
)


@pytest.fixture
def icepanel_fixture_source(monkeypatch):
    """Route every 'icepanel' model source to the fixture landscape (no network, no env)."""

    def build(source="icepanel", include_future=False, model_path=None):
        return IcePanelModelSource(
            "landscape", lambda path, key, params: ICEPANEL_FIXTURE[key], include_future
        )

    monkeypatch.setattr("archi_c4_score.scoring_service.build_source", build)
    return build
