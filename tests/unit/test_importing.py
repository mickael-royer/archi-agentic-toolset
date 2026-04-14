"""Unit tests for Neo4j import operations."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from archi_c4_score.importing import Neo4jImporter
from archi_c4_score.models import C4Level, C4Node, C4Relationship


class TestNeo4jImporter:
    """Tests for Neo4j import operations."""

    @pytest.fixture
    def importer(self, mock_neo4j_connection):
        """Create importer with mocked connection."""
        return Neo4jImporter(connection=mock_neo4j_connection)

    @pytest.mark.asyncio
    async def test_import_node(self, importer, mock_neo4j_connection):
        """Node import executes correctly."""
        mock_neo4j_connection.execute_query = AsyncMock(return_value=[])

        node = C4Node(
            id="node-1",
            name="User Service",
            c4_level=C4Level.CONTAINER,
        )

        await importer.import_node(node, commit="abc123")

        mock_neo4j_connection.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_relationship(self, importer, mock_neo4j_connection):
        """Relationship import executes correctly."""
        mock_neo4j_connection.execute_query = AsyncMock(return_value=[])

        rel = C4Relationship(
            source_id="node-1",
            target_id="node-2",
            relationship_type="flow-to",
            weight=3.0,
        )

        await importer.import_relationship(rel)

        mock_neo4j_connection.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_model(self, importer, mock_neo4j_connection):
        """Full model import executes."""
        mock_neo4j_connection.execute_query = AsyncMock(return_value=[])

        nodes = [
            C4Node(id="n1", name="S1", c4_level=C4Level.SYSTEM),
            C4Node(id="n2", name="C1", c4_level=C4Level.CONTAINER),
        ]
        rels = [
            C4Relationship(
                source_id="n1",
                target_id="n2",
                relationship_type="flow-to",
                weight=3.0,
            ),
        ]

        result = await importer.import_model(nodes, rels, commit="abc123")

        assert result["nodes_imported"] == 2
        assert result["relationships_imported"] == 1

    @pytest.mark.asyncio
    async def test_commit_tracking(self, importer, mock_neo4j_connection):
        """Import links to git commit."""
        mock_neo4j_connection.execute_query = AsyncMock(return_value=[])

        node = C4Node(
            id="node-1",
            name="Test",
            c4_level=C4Level.COMPONENT,
        )

        await importer.import_node(node, commit="abc123")

        call_args = mock_neo4j_connection.execute_query.call_args
        assert "abc123" in str(call_args)


@pytest.fixture
def mock_neo4j_connection():
    """Create mocked Neo4j connection."""
    conn = MagicMock()
    conn.execute_query = AsyncMock(return_value=[])
    return conn
