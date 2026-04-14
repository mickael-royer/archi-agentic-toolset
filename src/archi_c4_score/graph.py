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
