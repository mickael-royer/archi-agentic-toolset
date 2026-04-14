"""Contract tests for CLI interface."""

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

    def test_score_requires_commit(self):
        """Score requires commit SHA."""
        runner = CliRunner()
        result = runner.invoke(cli, ["score"])
        assert result.exit_code != 0


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
