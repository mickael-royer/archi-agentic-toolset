"""Repository operations for coArchi2 architecture models."""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """Repository operation error."""

    def __init__(self, message: str, path: str | None = None) -> None:
        self.path = path
        detail = f" [{path}]" if path else ""
        super().__init__(f"{message}{detail}")


class Repository:
    """Repository operations for architecture models."""

    def __init__(
        self,
        path: str | Path,
        commit: str | None = None,
    ) -> None:
        """Initialize repository with path and optional commit."""
        self.path = Path(path) if isinstance(path, str) else path
        self.commit = commit

    def validate(self) -> bool:
        """Validate repository path exists and is accessible."""
        if not self.path.exists():
            logger.warning(f"Repository path does not exist: {self.path}")
            return False
        if not self.path.is_dir():
            logger.warning(f"Repository path is not a directory: {self.path}")
            return False
        return True

    def clone(self, url: str) -> None:
        """Clone repository from URL."""
        logger.info(f"Cloning repository from {url}")
        try:
            subprocess.run(
                ["git", "clone", "--quiet", url, str(self.path)],
                capture_output=True,
                check=True,
            )
            logger.info(f"Repository cloned to {self.path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Git clone failed: {e.stderr}")
            raise RepositoryError(f"Clone failed: {e.stderr}", path=str(self.path))

    def get_current_commit(self) -> str:
        """Get current HEAD commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            commit = result.stdout.strip()
            logger.debug(f"Current commit: {commit}")
            return commit
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get current commit: {e.stderr}")
            raise RepositoryError(
                "Failed to get current commit",
                path=str(self.path),
            )

    def get_commit_info(self, commit_sha: str) -> dict[str, str]:
        """Get commit information."""
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--format=%H|%an|%ad|%s",
                    "-1",
                    commit_sha,
                ],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            parts = result.stdout.strip().split("|")
            if len(parts) >= 4:
                return {
                    "sha": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3],
                }
            return {"sha": commit_sha}
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get commit info: {e.stderr}")
            raise RepositoryError(
                "Failed to get commit info",
                path=str(self.path),
            )

    def find_model_files(self, pattern: str = "*.json") -> list[Path]:
        """Find architecture model files matching pattern."""
        logger.info(f"Finding model files with pattern: {pattern}")
        model_files = list(self.path.rglob(pattern))
        logger.debug(f"Found {len(model_files)} model files")
        return model_files

    def is_git_repository(self) -> bool:
        """Check if path is a git repository."""
        git_dir = self.path / ".git"
        return git_dir.exists() and git_dir.is_dir()
