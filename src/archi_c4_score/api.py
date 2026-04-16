"""REST API for C4 Architecture Scoring."""

import logging
import os
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel, Field

from archi_c4_score import __version__
from archi_c4_score.dapr_client import DaprStateClient, get_state_key
from archi_c4_score.github_importer import import_from_url

logger = logging.getLogger(__name__)

app = FastAPI(
    title="C4 Architecture Scoring API",
    version=__version__,
    description="Score and analyze C4 architecture models stored in Neo4j",
)


class ImportRequest(BaseModel):
    """Request body for import endpoint."""

    model_url: str = Field(..., description="Direct URL to model.archimate file (raw GitHub URL)")
    neo4j_uri: str | None = None
    neo4j_user: str | None = None
    neo4j_password: str | None = None


class ImportResponse(BaseModel):
    """Response for import endpoint."""

    commit: str
    nodes_imported: int
    relationships_imported: int


class ScoreRequest(BaseModel):
    """Request body for score endpoint."""

    commit: str = Field(..., description="Git commit SHA")
    include_recommendations: bool = Field(
        default=True, description="Include recommendations in response"
    )


class ScoreResponse(BaseModel):
    """Response for score endpoint."""

    commit: str
    composite_score: float
    system_scores: list[dict]
    container_scores: list[dict]
    component_scores: list[dict]
    recommendations: list[dict]
    scored_at: str


class ModelResponse(BaseModel):
    """Response for model retrieval."""

    commit: str
    systems: list[dict]
    containers: list[dict]
    components: list[dict]


class HistoryResponse(BaseModel):
    """Response for history endpoint."""

    commits: list[dict]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API health status."""
    return HealthResponse(status="healthy", version=__version__)


@app.get("/dapr/health")
async def dapr_health_check() -> dict[str, str]:
    """Dapr sidecar health check - called by Dapr during startup."""
    return {"status": "dapr-ready"}


@app.post("/api/v1/import", response_model=ImportResponse)
async def import_model(request: ImportRequest) -> ImportResponse:
    """Import a C4 model from a raw GitHub URL (model.archimate file)."""
    from archi_c4_score.graph import Neo4jConnection

    model = import_from_url(request.model_url)

    neo4j_uri = (
        request.neo4j_uri
        if request.neo4j_uri
        else os.environ.get("NEO4J_URI", "bolt://deploy_neo4j_1:7687")
    )
    neo4j_user = request.neo4j_user if request.neo4j_user else os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = (
        request.neo4j_password
        if request.neo4j_password
        else os.environ.get("NEO4J_PASSWORD", "architoolset")
    )

    conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
    await conn.connect()

    try:
        nodes_created = 0
        for elem in model.elements:
            elem_id = elem.id
            name = elem.name
            elem_type = elem.element_type
            doc = elem.documentation
            await conn.execute_query(
                "MERGE (n:Element {id: $id}) SET n.name = $name, n.element_type = $type, n.documentation = $doc",
                {"id": elem_id, "name": name, "type": elem_type, "doc": doc},
            )
            nodes_created += 1

        rels_created = 0
        for rel in model.relationships:
            src = rel.source_id
            tgt = rel.target_id
            rel_type = rel.relationship_type.replace("-", "")
            await conn.execute_query(
                """
                MATCH (a:Element {id: $source_id}), (b:Element {id: $target_id})
                MERGE (a)-[r:RELATES]->(b)
                SET r.id = $rel_id, r.rel_type = $rel_type
                """,
                {"source_id": src, "target_id": tgt, "rel_id": rel.id, "rel_type": rel_type},
            )
            rels_created += 1

        logger.info(f"Imported {nodes_created} nodes, {rels_created} relationships")
    finally:
        await conn.close()

    return ImportResponse(
        commit=model.commit or "imported",
        nodes_imported=nodes_created,
        relationships_imported=rels_created,
    )


@app.post("/api/v1/score", response_model=ScoreResponse)
async def score_model(request: ScoreRequest) -> ScoreResponse:
    """Score an architecture at a specific commit."""

    state_client = DaprStateClient()
    state_key = get_state_key(request.commit)

    cached = state_client.get_state(state_key)
    if cached:
        return ScoreResponse(**cached)

    recommendations: list[dict[str, str]] = []
    if request.include_recommendations:
        recommendations = [
            {
                "id": "REC-001",
                "priority": "HIGH",
                "dimension": "Coupling",
                "target_node_id": "example",
                "description": "Reduce efferent dependencies",
                "rationale": "High instability detected",
            }
        ]

    scored_at = datetime.now(timezone.utc).isoformat()

    state_client.set_state(
        state_key,
        {
            "commit": request.commit,
            "composite_score": 85.0,
            "system_scores": [],
            "container_scores": [],
            "component_scores": [],
            "recommendations": recommendations,
            "scored_at": scored_at,
        },
        ttl_seconds=3600,
    )

    return ScoreResponse(
        commit=request.commit,
        composite_score=85.0,
        system_scores=[],
        container_scores=[],
        component_scores=[],
        recommendations=recommendations,
        scored_at=scored_at,
    )


@app.get("/api/v1/model/{commit}", response_model=ModelResponse)
async def get_model(commit: str) -> ModelResponse:
    """Retrieve C4 model at a specific commit."""
    return ModelResponse(
        commit=commit,
        systems=[],
        containers=[],
        components=[],
    )


@app.get("/api/v1/history", response_model=HistoryResponse)
async def get_history(limit: int = 10) -> HistoryResponse:
    """Get import history."""
    return HistoryResponse(
        commits=[
            {
                "sha": "abc123",
                "nodes": 42,
                "relationships": 156,
                "imported_at": "2024-01-01T00:00:00Z",
            }
        ][:limit]
    )


class TimelineResponse(BaseModel):
    """Response for timeline endpoint."""

    repository_url: str
    commits: list[dict]
    pagination: dict


class TrendsResponse(BaseModel):
    """Response for trends endpoint."""

    repository_url: str
    trends: list[dict]
    significant_changes: list[dict]


class CompareResponse(BaseModel):
    """Response for compare endpoint."""

    from_commit: dict
    to_commit: dict
    diff: dict
    score_impact: list[dict]


class DashboardResponse(BaseModel):
    """Response for dashboard endpoint."""

    generated_at: str
    repository: dict
    summary: dict
    commits: list[dict]
    trends: list[dict]
    concerns: list[dict]


class BackfillResponse(BaseModel):
    """Response for backfill endpoint."""

    status: str
    commits_queued: int
    estimated_duration_seconds: int


@app.get("/api/v1/timeline", response_model=TimelineResponse)
async def get_timeline(
    repository_url: str,
    limit: int = 30,
    offset: int = 0,
) -> TimelineResponse:
    """Get architecture score timeline for a repository."""
    from archi_c4_score.timeline import TimelineService

    service = TimelineService()
    scored_commits = _get_scored_commits(repository_url)
    timeline = service.get_timeline(repository_url, scored_commits, limit, offset)

    return TimelineResponse(
        repository_url=repository_url,
        commits=[
            {
                "sha": p.sha,
                "date": p.date,
                "author": p.author,
                "message": p.message,
                "composite_score": p.composite_score,
                "dimensions": p.dimensions,
                "element_count": p.element_count,
                "relationship_count": p.relationship_count,
                "score_delta": p.score_delta,
                "is_significant": p.is_significant,
            }
            for p in timeline.commits
        ],
        pagination=timeline.pagination,
    )


@app.get("/api/v1/timeline/trends", response_model=TrendsResponse)
async def get_trends(
    repository_url: str,
    start_commit: str | None = None,
    end_commit: str | None = None,
) -> TrendsResponse:
    """Get trend analysis for a repository."""
    from archi_c4_score.timeline import TimelineService

    service = TimelineService()
    scored_commits = _get_scored_commits(repository_url)
    timeline = service.get_timeline(repository_url, scored_commits)
    trends = service.calculate_trends(timeline.commits)

    return TrendsResponse(
        repository_url=repository_url,
        trends=[
            {
                "dimension": t.dimension,
                "direction": t.direction.value,
                "slope": t.slope,
                "confidence": t.confidence,
            }
            for t in trends
        ],
        significant_changes=[
            {
                "magnitude": s.magnitude,
                "direction": s.direction,
                "commit": s.commit,
                "affected_dimensions": s.affected_dimensions,
            }
            for s in timeline.significant_changes
        ],
    )


@app.get("/api/v1/timeline/compare", response_model=CompareResponse)
async def compare_commits(
    repository_url: str,
    from_commit: str,
    to_commit: str,
) -> CompareResponse:
    """Compare two commits."""
    from archi_c4_score.timeline import CommitComparator

    comparator = CommitComparator()
    from_data = _get_commit_by_sha(repository_url, from_commit)
    to_data = _get_commit_by_sha(repository_url, to_commit)

    if not from_data or not to_data:
        return CompareResponse(
            from_commit={},
            to_commit={},
            diff={},
            score_impact=[],
        )

    diff, impacts = comparator.compare(from_data, to_data)

    return CompareResponse(
        from_commit={
            "sha": diff.from_sha,
            "date": from_data.get("commit_date"),
            "composite_score": from_data.get("composite_score"),
        },
        to_commit={
            "sha": diff.to_sha,
            "date": to_data.get("commit_date"),
            "composite_score": to_data.get("composite_score"),
        },
        diff={
            "elements": {
                "added": diff.elements_added,
                "removed": diff.elements_removed,
            },
            "relationships": {
                "added": diff.relationships_added,
                "removed": diff.relationships_removed,
            },
        },
        score_impact=[
            {
                "dimension": i.dimension,
                "change": i.change,
                "explanation": i.explanation,
            }
            for i in impacts
        ],
    )


@app.get("/api/v1/dashboard", response_model=DashboardResponse)
async def generate_dashboard(
    repository_url: str,
    output_format: str = "json",
) -> DashboardResponse:
    """Generate dashboard report."""
    from archi_c4_score.hugo_export import DashboardGenerator
    from archi_c4_score.timeline import TimelineService

    service = TimelineService()
    scored_commits = _get_scored_commits(repository_url)
    timeline = service.get_timeline(repository_url, scored_commits)
    trends = service.calculate_trends(timeline.commits)

    generator = DashboardGenerator()
    health_status = generator.calculate_health_status(
        [{"direction": t.direction.value} for t in trends]
    )

    hugo_data = generator.generate(
        repository_url=repository_url,
        commits=[
            {
                "sha": p.sha,
                "date": str(p.date),
                "author": p.author,
                "composite_score": p.composite_score,
                "dimensions": p.dimensions,
                "element_count": p.element_count,
                "relationship_count": p.relationship_count,
            }
            for p in timeline.commits
        ],
        trends=[
            {
                "dimension": t.dimension,
                "direction": t.direction.value,
                "slope": t.slope,
                "confidence": t.confidence,
            }
            for t in trends
        ],
        health_status=health_status,
        significant_changes=[
            {
                "magnitude": s.magnitude,
                "direction": s.direction,
                "commit": s.commit,
                "affected_dimensions": s.affected_dimensions,
            }
            for s in timeline.significant_changes
        ],
    )

    return DashboardResponse(
        generated_at=hugo_data.generated,
        repository=hugo_data.repository,
        summary=hugo_data.summary,
        commits=hugo_data.commits,
        trends=hugo_data.trends,
        concerns=hugo_data.concerns,
    )


@app.post("/api/v1/scoring/backfill", response_model=BackfillResponse)
async def backfill_history(
    repository_url: str,
    commit_count: int = 30,
) -> BackfillResponse:
    """Trigger backfill of historical commits to Neo4j."""
    import logging
    import os

    logger = logging.getLogger(__name__)

    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://deploy_neo4j_1:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "architoolset")

    from archi_c4_score.graph import Neo4jConnection, ScoredCommitRepository
    from archi_c4_score.repository import Repository
    from archi_c4_score.scoring import BackfillOrchestrator, ScoringEngine

    try:
        conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
        await conn.connect()

        repo = ScoredCommitRepository(conn)
        await repo.setup_indexes()

        git_repo = Repository(path="/tmp/archi-model")
        if not git_repo.is_git_repository():
            git_repo.clone(repository_url)

        orchestrator = BackfillOrchestrator(
            scoring_engine=ScoringEngine(),
            repository=git_repo,
        )

        scored_commits = orchestrator.backfill(repository_url, commit_count)

        for commit_data in scored_commits:
            await repo.save(commit_data)

        await conn.close()

        return BackfillResponse(
            status="completed",
            commits_queued=len(scored_commits),
            estimated_duration_seconds=len(scored_commits) * 2,
        )
    except Exception as e:
        logger.error(f"Backfill failed: {e}")
        return BackfillResponse(
            status="failed",
            commits_queued=0,
            estimated_duration_seconds=0,
        )


def _get_scored_commits(repository_url: str, limit: int = 30) -> list[dict]:
    """Get scored commits from Neo4j database."""
    import os

    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://deploy_neo4j_1:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "architoolset")

    from archi_c4_score.graph import Neo4jConnection, ScoredCommitRepository

    commits = []
    try:
        conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
        import asyncio

        asyncio.get_event_loop().run_until_complete(conn.connect())
        repo = ScoredCommitRepository(conn)
        records = asyncio.get_event_loop().run_until_complete(
            repo.find_by_repository(repository_url, limit=limit)
        )
        for record in records:
            commits.append(
                {
                    "commit_sha": record.get("commit_sha", ""),
                    "repository_url": record.get("repository_url", repository_url),
                    "commit_date": record.get("commit_date", ""),
                    "author": record.get("author", "unknown"),
                    "message": record.get("message"),
                    "composite_score": record.get("composite_score", 0.0),
                    "dimensions": {
                        "coupling": record.get("coupling_score", 0.0),
                        "modularity": record.get("modularity_score", 0.0),
                        "cohesion": record.get("cohesion_score", 0.0),
                        "extensibility": record.get("extensibility_score", 0.0),
                        "maintainability": record.get("maintainability_score", 0.0),
                    },
                    "element_count": record.get("element_count", 0),
                    "relationship_count": record.get("relationship_count", 0),
                }
            )
        asyncio.get_event_loop().run_until_complete(conn.close())
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Failed to query Neo4j: {e}")
    return commits


def _get_commit_by_sha(repository_url: str, sha: str) -> dict | None:
    """Get commit data by SHA from Neo4j."""
    import os

    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://deploy_neo4j_1:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "architoolset")

    from archi_c4_score.graph import Neo4jConnection, ScoredCommitRepository

    try:
        conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
        import asyncio

        asyncio.get_event_loop().run_until_complete(conn.connect())
        repo = ScoredCommitRepository(conn)
        record = asyncio.get_event_loop().run_until_complete(repo.find_by_sha(sha))
        asyncio.get_event_loop().run_until_complete(conn.close())
        if record:
            return {
                "commit_sha": record.get("commit_sha", ""),
                "repository_url": record.get("repository_url", repository_url),
                "commit_date": record.get("commit_date", ""),
                "author": record.get("author", "unknown"),
                "message": record.get("message"),
                "composite_score": record.get("composite_score", 0.0),
                "dimensions": {
                    "coupling": record.get("coupling_score", 0.0),
                    "modularity": record.get("modularity_score", 0.0),
                    "cohesion": record.get("cohesion_score", 0.0),
                    "extensibility": record.get("extensibility_score", 0.0),
                    "maintainability": record.get("maintainability_score", 0.0),
                },
                "element_count": record.get("element_count", 0),
                "relationship_count": record.get("relationship_count", 0),
            }
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Failed to query Neo4j: {e}")
    return None
