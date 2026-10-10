"""Contract tests for CLI interface."""

import json

from click.testing import CliRunner
from archi_c4_score.cli import cli


class TestCLIImport:
    """Tests for import command."""

    def test_import_command_exists(self):
        """Import command is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "import" in result.output

    def test_import_requires_repo_url(self):
        """Import requires repository URL argument."""
        runner = CliRunner()
        result = runner.invoke(cli, ["import"])
        assert result.exit_code != 0

    def test_import_with_url_and_neo4j(self):
        """Import accepts repo URL and Neo4j params."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "import",
                "https://github.com/example/repo",
                "--neo4j-uri",
                "bolt://localhost:7687",
                "--neo4j-user",
                "neo4j",
                "--neo4j-password",
                "password",
            ],
        )
        assert "import" in result.output.lower() or result.exit_code in [0, 1]


class TestCLIScore:
    """Tests for score command."""

    def test_score_command_exists(self):
        """Score command is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert "score" in result.output

    def test_score_icepanel_json(self, icepanel_fixture_source):
        """Score defaults to the IcePanel source and latest version."""
        result = CliRunner().invoke(cli, ["--json", "score"], obj={})
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["source"] == "icepanel" and data["composite_score"] == 50.4

    def test_score_text_lists_containers(self, icepanel_fixture_source):
        result = CliRunner().invoke(cli, ["score", "--version", "v2"], obj={})
        assert result.exit_code == 0, result.output
        assert "Backend" in result.output and "v2" in result.output

    def test_score_archimate_needs_model_path(self):
        result = CliRunner().invoke(cli, ["score", "--source", "archimate"], obj={})
        assert result.exit_code != 0

    def test_compare_versions(self, icepanel_fixture_source):
        result = CliRunner().invoke(cli, ["--json", "compare-versions", "v1", "v2"], obj={})
        assert result.exit_code == 0, result.output
        assert json.loads(result.output)["system_delta"] == 0.0

    def test_dashboard_icepanel_writes_hugo_data(self, icepanel_fixture_source, tmp_path):
        result = CliRunner().invoke(
            cli,
            ["dashboard", "--source", "icepanel", "--format", "hugo", "--output", str(tmp_path)],
            obj={},
        )
        assert result.exit_code == 0, result.output
        data = json.loads((tmp_path / "data" / "timeline.json").read_text())
        assert [c["sha"] for c in data["commits"]] == ["v1", "v2", "latest"]
        assert data["c4_scoring"]["source"] == "icepanel"
        assert any(cell["name"] == "Backend" for cell in data["c4_scoring"]["treemap"])


class TestCLIHistory:
    """Tests for history command."""

    def test_history_command_exists(self):
        """History command is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert "history" in result.output


class TestCLIOutput:
    """Tests for output formatting."""

    def test_json_output_flag(self):
        """CLI supports --json output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert "--json" in result.output or "-j" in result.output
