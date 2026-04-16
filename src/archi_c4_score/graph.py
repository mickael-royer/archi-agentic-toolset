"""Neo4j graph database operations."""

import logging
from typing import Any

from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import ServiceUnavailable, AuthError

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Neo4j connection manager with async support."""

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
    ) -> None:
        """Initialize Neo4j connection."""
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        logger.info(f"Connecting to Neo4j at {self.uri}")
        self._driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
        )
        try:
            await self._driver.verify_authentication()
            logger.info("Neo4j connection established")
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Neo4j connection failed: {e}")
            await self.close()
            raise

    async def close(self) -> None:
        """Close Neo4j connection."""
        if self._driver:
            await self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")

    async def execute_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results."""
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j")

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def health_check(self) -> bool:
        """Check if Neo4j connection is healthy."""
        try:
            if not self._driver:
                return False
            async with self._driver.session(database=self.database) as session:
                await session.run("RETURN 1")
            return True
        except ServiceUnavailable:
            return False


class GraphQueries:
    """Parameterized Cypher query templates.

    All queries use parameterized inputs ($param) to prevent Cypher injection.
    User-provided values must NEVER be concatenated directly into queries.
    """

    @staticmethod
    def create_node(label: str, properties: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Generate node creation query."""
        props = ", ".join(f"n.{k} = ${k}" for k in properties.keys())
        query = f"""
        CREATE (n:{label} {{{props}}})
        RETURN n
        """
        return query, properties

    @staticmethod
    def create_relationship(
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Generate relationship creation query."""
        params = {
            "source_id": source_id,
            "target_id": target_id,
            **properties,
        }
        props = ", ".join(f"r.{k} = ${k}" for k in properties.keys())
        query = f"""
        MATCH (a), (b)
        WHERE a.id = $source_id AND b.id = $target_id
        CREATE (a)-[r:{rel_type} {{{props}}}]->(b)
        RETURN r
        """
        return query, params

    @staticmethod
    def match_by_commit(commit_sha: str) -> tuple[str, dict[str, Any]]:
        """Query nodes by git commit."""
        query = """
        MATCH (n)
        WHERE n.git_commit = $commit
        RETURN n
        """
        return query, {"commit": commit_sha}

    @staticmethod
    def get_hierarchy() -> str:
        """Get complete C4 hierarchy."""
        return """
        MATCH (s:System)
        OPTIONAL MATCH (s)-[:CONTAINS]->(c:Container)
        OPTIONAL MATCH (c)-[:CONTAINS]->(m:Component)
        RETURN s, collect(DISTINCT c) as containers, 
               collect(DISTINCT m) as components
        """

    @staticmethod
    def get_dependencies(node_id: str) -> tuple[str, dict[str, Any]]:
        """Get all dependencies for a node."""
        query = """
        MATCH (n {id: $node_id})-[r]->(dep)
        RETURN n, r, dep
        """
        return query, {"node_id": node_id}

    @staticmethod
    def detect_cycles() -> str:
        """Detect circular dependencies."""
        return """
        MATCH (n)-[r:DEPENDS_ON*]->(n)
        WITH n, collect(DISTINCT relationships(r)) as cycles
        WHERE size(cycles) > 0
        RETURN n, cycles
        """

    @staticmethod
    def create_scored_commit(properties: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Generate ScoredCommit node creation query."""
        props = ", ".join(f"{k}: ${k}" for k in properties.keys())
        query = f"""
        CREATE (sc:ScoredCommit {{{props}}})
        RETURN sc
        """
        return query, properties

    @staticmethod
    def find_scored_commits_by_repo(
        repository_url: str,
        limit: int = 30,
        offset: int = 0,
    ) -> tuple[str, dict[str, Any]]:
        """Find scored commits for a repository ordered by date."""
        query = """
        MATCH (sc:ScoredCommit)
        WHERE sc.repository_url = $repository_url
        RETURN sc
        ORDER BY sc.commit_date ASC
        SKIP $offset
        LIMIT $limit
        """
        return query, {"repository_url": repository_url, "limit": limit, "offset": offset}

    @staticmethod
    def find_scored_commit_by_sha(
        commit_sha: str,
    ) -> tuple[str, dict[str, Any]]:
        """Find scored commit by SHA."""
        query = """
        MATCH (sc:ScoredCommit)
        WHERE sc.commit_sha = $commit_sha
        RETURN sc
        """
        return query, {"commit_sha": commit_sha}

    @staticmethod
    def link_scored_commits(
        from_sha: str,
        to_sha: str,
    ) -> tuple[str, dict[str, Any]]:
        """Link two scored commits in chronological order."""
        query = """
        MATCH (sc1:ScoredCommit), (sc2:ScoredCommit)
        WHERE sc1.commit_sha = $from_sha AND sc2.commit_sha = $to_sha
        CREATE (sc1)-[:NEXT_COMMIT]->(sc2)
        RETURN sc1, sc2
        """
        return query, {"from_sha": from_sha, "to_sha": to_sha}


class ScoredCommitRepository:
    """Repository for ScoredCommit operations."""

    def __init__(self, connection: Neo4jConnection) -> None:
        """Initialize repository with connection."""
        self.connection = connection
        self.queries = GraphQueries()

    async def save(self, scored_commit: dict[str, Any]) -> dict[str, Any]:
        """Save a scored commit to Neo4j."""
        query, params = self.queries.create_scored_commit(scored_commit)
        result = await self.connection.execute_query(query, params)
        logger.info(f"Saved scored commit: {scored_commit.get('commit_sha', 'unknown')[:7]}")
        return result[0] if result else {}

    async def find_by_repository(
        self,
        repository_url: str,
        limit: int = 30,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Find all scored commits for a repository."""
        query, params = self.queries.find_scored_commits_by_repo(repository_url, limit, offset)
        result = await self.connection.execute_query(query, params)
        return [record.get("sc", {}) for record in result]

    async def find_by_sha(self, commit_sha: str) -> dict[str, Any] | None:
        """Find a scored commit by SHA."""
        query, params = self.queries.find_scored_commit_by_sha(commit_sha)
        result = await self.connection.execute_query(query, params)
        return result[0].get("sc") if result else None

    async def link_commits(
        self,
        from_sha: str,
        to_sha: str,
    ) -> None:
        """Link two commits in chronological order."""
        query, params = self.queries.link_scored_commits(from_sha, to_sha)
        await self.connection.execute_query(query, params)
        logger.debug(f"Linked commits: {from_sha[:7]} -> {to_sha[:7]}")

    async def setup_indexes(self) -> None:
        """Create indexes for ScoredCommit nodes."""
        await self.connection.execute_query("""
            CREATE INDEX scored_commit_repo_date IF NOT EXISTS
            FOR (sc:ScoredCommit) ON (sc.repository_url, sc.commit_date)
        """)
        await self.connection.execute_query("""
            CREATE INDEX scored_commit_sha IF NOT EXISTS
            FOR (sc:ScoredCommit) ON (sc.commit_sha)
        """)
        logger.info("Created indexes for ScoredCommit nodes")
