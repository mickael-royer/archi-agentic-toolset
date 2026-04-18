# API Contracts: C4 Architecture Scoring

## Endpoints

### GET /scores/container
Get architecture scores for all containers in a system.

**Query Parameters**:
- `repository_url` (required): Git repository URL
- `commit_sha` (optional): Specific commit, defaults to HEAD

**Response**:
```json
{
  "containers": [
    {
      "node_id": "container-api",
      "node_name": "API Service",
      "composite": 75.5,
      "coupling": 82.0,
      "component_count": 5,
      "efferent_coupling": 3,
      "afferent_coupling": 2
    }
  ],
  "system_score": 72.3,
  "commit_sha": "abc123",
  "scored_at": "2026-04-18T10:00:00Z"
}
```

### GET /scores/system
Get consolidated system-level score.

**Query Parameters**:
- `repository_url` (required): Git repository URL
- `commit_sha` (optional): Specific commit, defaults to HEAD

**Response**:
```json
{
  "system_score": 72.3,
  "container_count": 3,
  "component_count": 12,
  "score_range": {"min": 65.0, "max": 82.0},
  "commit_sha": "abc123",
  "scored_at": "2026-04-18T10:00:00Z"
}
```

### GET /scores/timeline
Get score history over commit timeline.

**Query Parameters**:
- `repository_url` (required): Git repository URL
- `limit` (optional): Number of commits, default 50

**Response**:
```json
{
  "repository_url": "https://github.com/example/repo",
  "commits": [
    {
      "commit_sha": "abc123",
      "commit_date": "2026-04-18T10:00:00Z",
      "composite_score": 72.3,
      "system_score": 72.3
    }
  ]
}
```

### GET /scores/export
Export dashboard data for download.

**Query Parameters**:
- `repository_url` (required): Git repository URL
- `format` (optional): timeline, trends, recommendations (comma-separated)

**Response**: JSON file download

### GET /scores/treemap
Get treemap data for visualization.

**Query Parameters**:
- `repository_url` (required): Git repository URL

**Response**:
```json
{
  "cells": [
    {
      "id": "container-api",
      "name": "API Service",
      "level": "CONTAINER",
      "score": 75.5,
      "size": 5,
      "parent_id": "system-main"
    }
  ]
}
```

### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```