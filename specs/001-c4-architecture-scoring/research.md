# Research: C4 Graph Scoring

**Date**: 2026-04-13  
**Feature**: 002-c4-architecture-scoring

## Neo4j Graph Database

**Decision**: Use Neo4j as the graph database for storing C4 models

**Rationale**: Neo4j is the industry-standard graph database with:
- Native graph storage optimized for relationship traversals
- Cypher query language for complex graph queries
- Official Python driver (neo4j-driver) with async support
- AuraDB for cloud-hosted option, or self-hosted for local development
- Proven track record in architecture analysis tools

**Key characteristics**:
- Nodes represent C4 elements (Software System, Container, Component)
- Relationships represent dependencies with weight properties
- Properties store metadata (name, git commit, timestamp)
- Cypher queries enable complex traversals for scoring

**Alternatives considered**:
- Amazon Neptune: More complex setup, less mature Python support
- ArangoDB: Multi-model (document + graph), overkill for graph-only use
- NetworkX in-memory: No persistence, limited querying

## Architecture Sketch

```
┌─────────────────────────────────────────────────────────────────┐
│                      archi_c4_score                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  repository  │───▶│   parser    │───▶│   mapper     │     │
│  │  (git clone) │    │  (coArchi2)  │    │  (C4 levels) │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                  │                │
│                                                  ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   scoring    │◀───│   graph      │◀───│   neo4j      │     │
│  │  (metrics)  │    │  (cypher)    │    │  (storage)   │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐                          │
│  │     cli      │    │   fastapi    │                          │
│  │  (click)    │    │  (REST API)  │                          │
│  └──────────────┘    └──────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Technical Decisions

### D1: Neo4j Driver

| Option | Pros | Cons |
|--------|------|------|
| **neo4j-driver** | Official, async support, well-documented | Blocking for sync operations |
| **py2neo** | Mature, Pythonic | Legacy, less active development |
| **neomodel** | Django-like ORM | Extra abstraction layer |

**Decision**: neo4j-driver with async/await for FastAPI integration
**Rationale**: Native async support matches FastAPI's async architecture, official support ensures compatibility

### D2: Neo4j Deployment

| Option | Pros | Cons |
|--------|------|------|
| **Neo4j Aura** | Managed, auto-scaling, no ops | Cost for production, network dependency |
| **Neo4j Desktop** | Free local development | Not production-ready |
| **Docker container** | Portable, matches Podman principle | Manual operations |

**Decision**: Docker container for local development, Aura for production
**Rationale**: Matches Podman principle from constitution, easy local testing

### D3: Cypher Query Strategy

| Option | Pros | Cons |
|--------|------|------|
| **Parameterized queries** | Safe, reusable | More verbose |
| **Query builder** | Fluent, readable | Extra dependency |
| **Raw strings** | Simple | SQL injection risk |

**Decision**: Parameterized Cypher queries in dedicated query module
**Rationale**: Security + reusability balance

## Conclusions

1. Neo4j is the graph database choice
2. neo4j-driver with async for FastAPI integration
3. Docker container for local development
4. Parameterized Cypher queries for safety
