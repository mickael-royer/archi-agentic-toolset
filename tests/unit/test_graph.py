"""Unit tests for Neo4j graph operations."""

import pytest
from unittest.mock import AsyncMock, patch
from archi_c4_score.graph import Neo4jConnection, GraphQueries


class TestNeo4jConnection:
    """Tests for Neo4j connection manager."""

    def test_connection_initialization(self):
        """Connection initializes with URI and auth."""
        conn = Neo4jConnection(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )
        assert conn.uri == "bolt://localhost:7687"
        assert conn.user == "neo4j"

    def test_connection_with_database(self):
        """Connection can specify database."""
        conn = Neo4jConnection(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
            database="neo4j",
        )
        assert conn.database == "neo4j"

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Connection establishes successfully."""
        conn = Neo4jConnection(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )
        with patch("neo4j.AsyncGraphDatabase.driver") as mock_driver:
            mock_driver.return_value.verify_authentication = AsyncMock()
            mock_driver.return_value.close = AsyncMock()
            await conn.connect()
            assert conn._driver is not None

    @pytest.mark.asyncio
    async def test_close_connection(self):
        """Connection closes properly."""
        conn = Neo4jConnection(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )
        with patch("neo4j.AsyncGraphDatabase.driver") as mock_driver:
            mock_driver.return_value.verify_authentication = AsyncMock()
            mock_driver.return_value.close = AsyncMock()
            await conn.connect()
            await conn.close()
            mock_driver.return_value.close.assert_called_once()


class TestGraphQueries:
    """Tests for Cypher query operations."""

    @pytest.mark.asyncio
    async def test_create_node_cypher(self):
        """Node creation query is correct."""
        query, params = GraphQueries.create_node("Component", {"id": "test-1", "name": "Test"})
        assert "CREATE (n:Component" in query
        assert "$id" in query
        assert "$name" in query
        assert params == {"id": "test-1", "name": "Test"}

    @pytest.mark.asyncio
    async def test_create_relationship_cypher(self):
        """Relationship creation query is correct."""
        query, params = GraphQueries.create_relationship(
            "node-1", "node-2", "DEPENDS_ON", {"weight": 3.0}
        )
        assert "MATCH (a), (b)" in query
        assert "CREATE (a)-[r:DEPENDS_ON" in query
        assert "weight" in params
        assert params["weight"] == 3.0

    @pytest.mark.asyncio
    async def test_match_by_commit_query(self):
        """Query by git commit is correct."""
        query, params = GraphQueries.match_by_commit("abc123")
        assert "MATCH (n)" in query
        assert "$commit" in query
        assert "WHERE" in query
        assert params == {"commit": "abc123"}

    @pytest.mark.asyncio
    async def test_get_hierarchy_query(self):
        """Hierarchy retrieval query is correct."""
        query = GraphQueries.get_hierarchy()
        assert "MATCH (s:System)" in query
        assert "OPTIONAL MATCH (s)-" in query
        assert "RETURN s, collect(" in query

    @pytest.mark.asyncio
    async def test_get_dependencies_query(self):
        """Dependency query for a node is correct."""
        query, params = GraphQueries.get_dependencies("node-123")
        assert "MATCH (n {id:" in query
        assert "$node_id" in query
        assert params == {"node_id": "node-123"}

    @pytest.mark.asyncio
    async def test_detect_cycles_query(self):
        """Cycle detection query is correct."""
        query = GraphQueries.detect_cycles()
        assert "MATCH" in query
        assert "[r:" in query
        assert "*" in query
        assert "cycles" in query

    @pytest.mark.asyncio
    async def test_queries_use_parameters(self):
        """All queries use $parameter syntax for injection safety."""
        query, params = GraphQueries.get_dependencies("'; DROP DATABASE; --")
        assert "DROP" not in query
        assert "'; DROP DATABASE; --" in params.values()
        assert "$node_id" in query

    @pytest.mark.asyncio
    async def test_match_by_commit_parameterized(self):
        """Commit query uses parameters to prevent injection."""
        malicious_commit = "'; MATCH (n) DETACH DELETE n; RETURN '"
        query, params = GraphQueries.match_by_commit(malicious_commit)
        assert "DETACH" not in query
        assert malicious_commit in params.values()
        assert "$commit" in query
