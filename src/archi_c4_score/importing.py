"""Neo4j import operations for C4 models."""

import json
import logging
from datetime import datetime, timezone

from archi_c4_score.graph import Neo4jConnection, GraphQueries
from archi_c4_score.models import C4Node, C4Relationship

logger = logging.getLogger(__name__)


class Neo4jImporter:
    """Handles importing C4 model elements into Neo4j."""

    def __init__(self, connection: Neo4jConnection) -> None:
        """Initialize importer with a Neo4j connection."""
        self._conn = connection

    async def import_node(self, node: C4Node, commit: str | None = None) -> None:
        """Import a single C4 node into Neo4j."""
        label = node.c4_level.value
        props = {
            "id": node.id,
            "name": node.name,
            "c4_level": node.c4_level.value,
        }
        if node.parent_id:
            props["parent_id"] = node.parent_id
        if commit:
            props["git_commit"] = commit
        props["imported_at"] = datetime.now(timezone.utc).isoformat()
        if node.properties:
            props["properties_json"] = json.dumps(node.properties)

        query, params = GraphQueries.create_node(label, props)
        await self._conn.execute_query(query, params)
        logger.debug(f"Imported node: {node.id} ({label})")

    async def import_relationship(self, rel: C4Relationship) -> None:
        """Import a single relationship into Neo4j."""
        rel_type = rel.relationship_type.upper().replace("-", "_")
        props = {
            "relationship_type": rel.relationship_type,
            "weight": rel.weight,
            "is_circular": rel.is_circular,
        }
        query, params = GraphQueries.create_relationship(
            rel.source_id, rel.target_id, rel_type, props
        )
        await self._conn.execute_query(query, params)
        logger.debug(f"Imported relationship: {rel.source_id} -> {rel.target_id}")

    async def import_model(
        self,
        nodes: list[C4Node],
        rels: list[C4Relationship],
        commit: str | None = None,
    ) -> dict[str, int]:
        """Import complete C4 model into Neo4j."""
        nodes_imported = 0
        for node in nodes:
            await self.import_node(node, commit)
            nodes_imported += 1

        rels_imported = 0
        for rel in rels:
            await self.import_relationship(rel)
            rels_imported += 1

        logger.info(f"Imported model: {nodes_imported} nodes, {rels_imported} relationships")
        return {
            "nodes_imported": nodes_imported,
            "relationships_imported": rels_imported,
        }
