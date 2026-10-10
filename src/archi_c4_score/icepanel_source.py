"""IcePanel model source: reads the C4 model from the IcePanel REST API (ADR 0030, 0031)."""

import json
import logging
import os
from collections.abc import Callable
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from archi_c4_score.c4_converter import C4ConversionResult
from archi_c4_score.model_source import ModelVersion
from archi_c4_score.models import C4Level, C4Node, C4Relationship
from archi_c4_score.scoring import ASYNC_WEIGHT, SYNC_WEIGHT

logger = logging.getLogger(__name__)

ICEPANEL_API_URL = "https://api.icepanel.io/v1"
AUTH_HEADER = "X-API-Key"
AUTH_ENV = "ICEPANEL_API_KEY"
INTERACTION_TAG_GROUP = "Interaction"
ASYNC_TAG = "Async"

C4_LEVEL_BY_TYPE = {
    "system": C4Level.SYSTEM,
    "app": C4Level.CONTAINER,
    "store": C4Level.CONTAINER,
    "component": C4Level.COMPONENT,
}

# fetch(path, list_key, params) -> every item across pages
Fetcher = Callable[[str, str, dict[str, str]], list[dict[str, Any]]]


class IcePanelModelSource:
    """Map an IcePanel landscape version to C4 nodes and weighted relationships."""

    def __init__(self, landscape_id: str, fetch: Fetcher, include_future: bool = False) -> None:
        self.landscape_id = landscape_id
        self._fetch = fetch
        self.include_future = include_future

    @classmethod
    def from_env(cls, include_future: bool = False) -> "IcePanelModelSource":
        auth = os.getenv(AUTH_ENV)
        landscape_id = os.getenv("ICEPANEL_LANDSCAPE_ID")
        if not auth or not landscape_id:
            raise ValueError(f"{AUTH_ENV} and ICEPANEL_LANDSCAPE_ID must be set")
        return cls(landscape_id, _http_fetcher(auth), include_future)

    @staticmethod
    def default_version() -> str:
        return os.getenv("ICEPANEL_VERSION_ID", "latest")

    def list_versions(self) -> list[ModelVersion]:
        versions = self._fetch(f"/landscapes/{self.landscape_id}/versions", "versions", {})
        return sorted(
            (
                ModelVersion(id=v["id"], name=v.get("name", ""), created_at=v.get("createdAt", ""))
                for v in versions
            ),
            key=lambda v: v.created_at,
        )

    def load(self, version_id: str = "latest") -> C4ConversionResult:
        base = f"/landscapes/{self.landscape_id}/versions/{version_id}"
        objects = self._fetch(f"{base}/model/objects", "modelObjects", {})
        connections = self._fetch(f"{base}/model/connections", "modelConnections", {})
        return to_c4(objects, connections, self._async_tag_ids(base), self.include_future)

    def _async_tag_ids(self, base: str) -> set[str]:
        groups = self._fetch(f"{base}/tag-groups", "tagGroups", {})
        group_ids = {g["id"] for g in groups if g.get("name") == INTERACTION_TAG_GROUP}
        if not group_ids:
            logger.warning(
                "No '%s' tag group in IcePanel: all connections count as sync",
                INTERACTION_TAG_GROUP,
            )
            return set()
        tags = self._fetch(f"{base}/tags", "tags", {})
        return {t["id"] for t in tags if t.get("groupId") in group_ids and t.get("name") == ASYNC_TAG}


def to_c4(
    objects: list[dict[str, Any]],
    connections: list[dict[str, Any]],
    async_tag_ids: set[str],
    include_future: bool = False,
) -> C4ConversionResult:
    """Pure mapping from IcePanel objects/connections to C4 entities (see spec 006 data-model)."""
    allowed = {"live", "deprecated"} | ({"future"} if include_future else set())
    objects = [o for o in objects if o.get("status", "live") in allowed and o.get("type") != "root"]
    by_id = {o["id"]: o for o in objects}

    nodes: list[C4Node] = []
    system_id: str | None = None
    for obj in objects:
        level = C4_LEVEL_BY_TYPE.get(obj.get("type", ""))
        scored = level is not None and not obj.get("external", False)
        if level == C4Level.SYSTEM and scored and system_id is None:
            system_id = obj["id"]
        parent_id = obj.get("parentId")
        nodes.append(
            C4Node(
                id=obj["id"],
                name=obj.get("name", obj["id"]),
                c4_level=level or C4Level.SYSTEM,
                parent_id=parent_id if parent_id in by_id else None,
                properties={
                    "type": obj.get("type", ""),
                    "external": str(obj.get("external", False)).lower(),
                    "scored": str(scored).lower(),
                    "caption": obj.get("caption") or "",
                },
            )
        )

    relationships: list[C4Relationship] = []
    for conn in connections:
        if conn.get("status", "live") not in allowed:
            continue
        origin, target = str(conn.get("originId")), str(conn.get("targetId"))
        if origin not in by_id or target not in by_id:
            continue
        is_async = bool(async_tag_ids & set(conn.get("tagIds") or []))
        rel_type, weight = ("async", ASYNC_WEIGHT) if is_async else ("sync", SYNC_WEIGHT)
        pairs = [(origin, target)]
        if conn.get("direction") == "bidirectional":
            pairs.append((target, origin))
        for source_id, target_id in pairs:
            relationships.append(
                C4Relationship(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=conn.get("name", ""),
                    rel_type=rel_type,
                    weight=weight,
                )
            )

    return C4ConversionResult(nodes=nodes, relationships=relationships, system_id=system_id)


def _http_fetcher(auth: str) -> Fetcher:
    def fetch(path: str, list_key: str, params: dict[str, str]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        query = dict(params)
        while True:
            url = f"{ICEPANEL_API_URL}{path}"
            if query:
                url += "?" + urlencode(query)
            request = Request(url, headers={AUTH_HEADER: auth, "Accept": "application/json"})
            with urlopen(request, timeout=30) as response:
                body = json.load(response)
            items.extend(body.get(list_key, []))
            if not body.get("nextCursor"):
                return items
            query["cursor"] = body["nextCursor"]

    return fetch
