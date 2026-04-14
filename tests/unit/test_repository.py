"""Unit tests for repository operations."""

from pathlib import Path
from unittest.mock import patch, MagicMock
from archi_c4_score.repository import Repository, RepositoryError


class TestRepository:
    """Tests for repository operations."""

    def test_repository_initialization(self):
        """Repository initializes with path."""
        repo = Repository(path="/tmp/test-repo")
        assert repo.path == Path("/tmp/test-repo")

    def test_repository_with_commit(self):
        """Repository can specify commit."""
        repo = Repository(path="/tmp/test-repo", commit="abc123")
        assert repo.commit == "abc123"

    def test_validate_path_exists(self):
        """Path validation succeeds for existing directory."""
        repo = Repository(path=".")
        assert repo.validate() is True

    def test_validate_path_not_exists(self):
        """Path validation fails for non-existent directory."""
        repo = Repository(path="/nonexistent/path")
        assert repo.validate() is False

    @patch("subprocess.run")
    def test_clone_repository(self, mock_run):
        """Git clone executes correctly."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository(path="/tmp/test-repo")
        repo.clone("https://github.com/user/repo.git")
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "git" in call_args[0][0]
        assert "clone" in call_args[0][0]

    @patch("subprocess.run")
    def test_get_current_commit(self, mock_run):
        """Get current commit SHA."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123def456\n",
        )
        repo = Repository(path="/tmp/test-repo")
        commit = repo.get_current_commit()
        assert commit == "abc123def456"

    @patch("subprocess.run")
    def test_get_commit_info(self, mock_run):
        """Get commit information."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123|author|date|message\n",
        )
        repo = Repository(path="/tmp/test-repo")
        info = repo.get_commit_info("abc123")
        assert "abc123" in info.get("sha", "")


class TestRepositoryError:
    """Tests for repository error handling."""

    def test_error_message(self):
        """Error has descriptive message."""
        error = RepositoryError("Test error")
        assert "Test error" in str(error)

    def test_error_with_path(self):
        """Error includes path context."""
        error = RepositoryError("Clone failed", path="/tmp/repo")
        assert "/tmp/repo" in str(error)
