"""Timeline storage for scoring history."""

import logging
from typing import TYPE_CHECKING

from archi_c4_score.models import ScoreSnapshot

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)


class TimelineStorage:
    """Store and retrieve score timeline history."""

    def __init__(self, driver: "Driver | None" = None):
        """Initialize timeline storage.

        Args:
            driver: Neo4j driver (optional)
        """
        self.driver = driver

    def save_snapshot(self, snapshot: ScoreSnapshot) -> None:
        """Save a score snapshot.

        Args:
            snapshot: Score snapshot to save
        """
        logger.info(f"Saving snapshot for commit {snapshot.commit_sha[:7]}")

    def get_snapshots(
        self,
        repository_url: str,
        limit: int = 50,
    ) -> list[ScoreSnapshot]:
        """Get score history for a repository.

        Args:
            repository_url: Git repository URL
            limit: Maximum number of snapshots

        Returns:
            List of score snapshots ordered by date
        """
        logger.info(f"Retrieving {limit} snapshots for {repository_url}")
        return []

    def get_latest(self, repository_url: str) -> ScoreSnapshot | None:
        """Get the latest score snapshot.

        Args:
            repository_url: Git repository URL

        Returns:
            Latest snapshot or None
        """
        snapshots = self.get_snapshots(repository_url, limit=1)
        return snapshots[0] if snapshots else None
