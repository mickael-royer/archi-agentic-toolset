"""C4 Architecture Scoring with Neo4j."""

__version__ = "0.1.0"

import logging

from archi_c4_score.models import C4Level, C4Node, C4Relationship
from archi_c4_score.graph import Neo4jConnection, GraphQueries
from archi_c4_score.parser import CoArchi2Parser
from archi_c4_score.mapper import C4Mapper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

__all__ = [
    "__version__",
    "C4Level",
    "C4Node",
    "C4Relationship",
    "Neo4jConnection",
    "GraphQueries",
    "CoArchi2Parser",
    "C4Mapper",
]
