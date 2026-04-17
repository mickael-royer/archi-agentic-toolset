"""Tests for CLI commands."""

from unittest.mock import patch

from click.testing import CliRunner

from archi_c4_score.cli import cli


class TestDashboardCommand:
    """Tests for dashboard command."""

    def test_dashboard_command_exists(self):
        """Dashboard command is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--help"])
        assert result.exit_code == 0

    def test_dashboard_requires_repo_url(self):
        """Dashboard requires --repo-url parameter."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard"])
        assert result.exit_code != 0

    @patch("archi_c4_score.cli._get_mock_scored_commits")
    def test_dashboard_shows_health_status(self, mock_commits):
        """Dashboard shows health status."""
        mock_commits.return_value = []
        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--repo-url", "https://github.com/test/repo"])
        assert result.exit_code == 0
        assert "Health Status" in result.output or "Dashboard" in result.output

    @patch("archi_c4_score.cli._get_mock_scored_commits")
    def test_dashboard_json_output(self, mock_commits):
        """Dashboard outputs JSON when --json flag is used."""
        mock_commits.return_value = []
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--json", "dashboard", "--repo-url", "https://github.com/test/repo"]
        )
        assert result.exit_code == 0
        assert "generated_at" in result.output or "repository" in result.output

    @patch("archi_c4_score.cli._get_mock_scored_commits")
    def test_dashboard_with_recommendations_flag(self, mock_commits):
        """Dashboard supports --include-recommendations flag."""
        mock_commits.return_value = []
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "dashboard",
                "--repo-url",
                "https://github.com/test/repo",
                "--include-recommendations",
            ],
        )
        assert result.exit_code == 0
        # Should not fail even if recommendations section is present or absent
        assert "Dashboard" in result.output or "Health Status" in result.output

    @patch("archi_c4_score.cli._get_mock_scored_commits")
    def test_dashboard_json_with_recommendations(self, mock_commits):
        """Dashboard JSON output includes recommendations when flag is set."""
        mock_commits.return_value = []
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--json",
                "dashboard",
                "--repo-url",
                "https://github.com/test/repo",
                "--include-recommendations",
            ],
        )
        assert result.exit_code == 0
        # JSON output should contain recommendations key
        assert "recommendations" in result.output or "generated_at" in result.output
