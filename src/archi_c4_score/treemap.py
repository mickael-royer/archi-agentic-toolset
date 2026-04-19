"""Treemap generation for visualization."""

import logging
from typing import TYPE_CHECKING

from archi_c4_score.models import TreemapCell

if TYPE_CHECKING:
    from archi_c4_score.models import ContainerScore

logger = logging.getLogger(__name__)


def generate_treemap(
    containers: list["ContainerScore"],
    system_id: str | None = None,
) -> list[TreemapCell]:
    """Generate treemap data for visualization.

    Args:
        containers: List of container scores
        system_id: System node ID

    Returns:
        List of TreemapCell objects
    """
    cells: list[TreemapCell] = []

    if system_id:
        # Calculate system score from container scores
        system_score = 100.0
        if containers:
            system_score = sum(c.composite for c in containers) / len(containers)

        cells.append(
            TreemapCell(
                id=system_id,
                name="System",
                level="SYSTEM",
                score=system_score,
                size=len(containers),
            )
        )

    # Add containers with their scores (skip duplicate components)
    seen: set[str] = set()
    for container in containers:
        if container.node_id in seen:
            continue
        seen.add(container.node_id)

        # Use coupling score (higher coupling = more red/worse)
        cells.append(
            TreemapCell(
                id=container.node_id,
                name=container.node_name,
                level="CONTAINER",
                score=container.coupling,  # Use coupling instead of composite
                size=container.component_count,
                parent_id=system_id,
                stereotype=getattr(container, "stereotype", ""),
            )
        )

    return cells


def calculate_cell_size(score: float, component_count: int) -> int:
    """Calculate cell size for treemap visualization.

    Args:
        score: Container score (0-100)
        component_count: Number of components

    Returns:
        Cell size value
    """
    base_size = component_count
    score_factor = max(1.0, score / 20.0)
    return int(base_size * score_factor)
