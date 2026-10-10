# Contract: POST /api/v1/score

Request:

```json
{"source": "icepanel", "version": "latest", "include_future": false, "include_recommendations": false}
```

- `source`: `icepanel` (default) or `archimate`. `archimate` needs `model_path` (local `.archimate` file).
- `version`: IcePanel version id, default `latest`.
- `commit`: kept for backward compatibility, used as `version` when `version` is missing.

Response (200):

```json
{
  "commit": "latest",
  "source": "icepanel",
  "composite_score": 61.2,
  "system_scores": [{"node_id": "...", "node_name": "Unicorn", "composite": 61.2}],
  "container_scores": [{"node_id": "...", "node_name": "Backend", "composite": 50.0, "coupling": 50.0,
                        "afferent_coupling": 2, "efferent_coupling": 3, "instability_index": 0.6,
                        "component_count": 4}],
  "component_scores": [{"node_id": "...", "node_name": "List Files", "parent": "Backend", "...": "..."}],
  "recommendations": [],
  "scored_at": "2026-10-11T10:00:00+00:00"
}
```

Errors: 400 when the source is not configured (missing env), 502 when IcePanel is unreachable.

# Contract: MCP tools (`archi-c4-mcp`, stdio)

| Tool | Args | Returns |
|---|---|---|
| `score_landscape` | `version="latest"`, `include_future=false` | same body as the API response |
| `compare_versions` | `from_version`, `to_version="latest"`, `include_future=false` | `{system_delta, containers: [{name, before, after, delta, status: added/removed/changed/unchanged}]}` |
| `list_versions` | none | `[{id, name, created_at}]` |
