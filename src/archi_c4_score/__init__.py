"""C4 Architecture Scoring with Neo4j."""

__version__ = "0.1.0"

import logging
import json
import sys
from datetime import datetime, timezone


class DaprJsonFormatter(logging.Formatter):
    """JSON formatter for Dapr observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "time": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)
for handler in logging.root.handlers:
    handler.setFormatter(DaprJsonFormatter())

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
