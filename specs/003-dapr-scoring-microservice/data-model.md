# Data Model: Dapr Scoring Microservice

## Entities

### ScoringRequest
| Field | Type | Validation |
|-------|------|------------|
| commit | string | Required, SHA format |
| include_recommendations | boolean | Default: true |

### ScoringResponse
| Field | Type |
|-------|------|
| commit | string |
| composite_score | float |
| system_scores | SystemScore[] |
| container_scores | ContainerScore[] |
| component_scores | ComponentScore[] |
| recommendations | Recommendation[] |
| scored_at | datetime |

### Dapr State (Cached Results)
| Field | Type | Purpose |
|-------|------|---------|
| key | string | `{commit}:score` |
| value | ScoringResponse | Cached response |
| expiry | int | TTL in seconds |

## API Endpoints

### POST /api/v1/score
Score architecture at commit.

**Request**: ScoringRequest  
**Response**: ScoringResponse (200)  
**Dapr**: State store for caching results

### GET /api/v1/model/{commit}
Retrieve C4 model from Neo4j.

**Response**: ModelResponse (200)

### GET /api/v1/history
Get import history.

**Query**: limit (default: 10)  
**Response**: HistoryResponse (200)

### GET /health
Liveness probe.

**Response**: `{"status": "healthy"}`

### GET /dapr/health
Dapr readiness probe.

**Response**: `{"status": "dapr-ready"}`
