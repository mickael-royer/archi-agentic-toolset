"""REST API for C4 Architecture Scoring."""

import logging
import os
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from archi_c4_score import __version__
from archi_c4_score.dapr_client import DaprStateClient, get_state_key
from archi_c4_score.github_importer import import_from_url
from archi_c4_score.scoring import ScoringEngine

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="C4 Architecture Scoring API",
    version=__version__,
    description="Score and analyze C4 architecture models stored in Neo4j",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ImportRequest(BaseModel):
    """Request body for import endpoint."""

    repository_url: str = Field(
        ..., description="GitHub repository URL (e.g., https://github.com/owner/repo)"
    )
    clear_first: bool = Field(default=False, description="Clear existing data before import")
    max_commits: int = Field(default=50, description="Maximum number of commits to import")
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
    """Import models from GitHub repository commit history."""
    import logging
    import httpx

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    owner_repo = request.repository_url.rstrip("/").replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{owner_repo}/commits"

    neo4j_uri = request.neo4j_uri or os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = request.neo4j_user or os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = request.neo4j_password or os.environ.get("NEO4J_PASSWORD", "architoolset")

    from archi_c4_score.graph import Neo4jConnection

    if request.clear_first:
        logger.info(f"Clearing existing data for {owner_repo}")

    commits_imported = 0
    commits_skipped = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = await client.get(
            api_url, headers=headers, params={"per_page": request.max_commits}
        )
        response.raise_for_status()
        commit_list = response.json()

        logger.info(f"Found {len(commit_list)} commits, connecting to Neo4j")

        conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
        await conn.connect()

        for commit_info in commit_list[: request.max_commits]:
            commit_sha = commit_info["sha"]
            commit_date = commit_info.get("commit", {}).get("committer", {}).get("date", "")

            model_url = (
                f"https://raw.githubusercontent.com/{owner_repo}/{commit_sha}/model.archimate"
            )

            try:
                model_resp = await client.get(model_url)
                if model_resp.status_code != 200:
                    commits_skipped += 1
                    continue

                if request.clear_first:
                    await conn.execute_query("MATCH (e:Element) DETACH DELETE e", {})

                model = import_from_url(model_url)
                nodes_created = 0
                for elem in model.elements:
                    await conn.execute_query(
                        "MERGE (n:Element {id: $id}) SET n.name = $name, n.element_type = $type, n.stereotype = $stereotype",
                        {
                            "id": elem.id,
                            "name": elem.name,
                            "type": elem.element_type,
                            "stereotype": elem.stereotype or "",
                        },
                    )
                    nodes_created += 1

                rels_created = 0
                for rel in model.relationships:
                    await conn.execute_query(
                        """MATCH (a:Element {id: $source_id}), (b:Element {id: $target_id})
                        MERGE (a)-[r:RELATES]->(b) SET r.rel_type = $rel_type""",
                        {
                            "source_id": rel.source_id,
                            "target_id": rel.target_id,
                            "rel_type": rel.relationship_type.replace("-", ""),
                        },
                    )
                    rels_created += 1

                await conn.execute_query(
                    """MERGE (c:ScoredCommit {commit_sha: $sha})
                    SET c.repository_url = $repo_url, c.commit_date = datetime($date),
                        c.element_count = $elem_count, c.relationship_count = $rel_count""",
                    {
                        "sha": commit_sha,
                        "repo_url": request.repository_url,
                        "date": commit_date,
                        "elem_count": nodes_created,
                        "rel_count": rels_created,
                    },
                )

                commits_imported += 1
                logger.info(
                    f"Imported {commit_sha[:7]}: {nodes_created} elements, {rels_created} relations"
                )

            except Exception as e:
                logger.warning(f"Failed {commit_sha[:7]}: {e}")
                commits_skipped += 1

        await conn.close()

    return ImportResponse(
        commit=f"{commits_imported} imported, {commits_skipped} skipped",
        nodes_imported=commits_imported,
        relationships_imported=commits_skipped,
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
    recommendations: dict
    c4_scoring: dict | None = None


class RecommendationResponse(BaseModel):
    """Single recommendation in API response."""

    id: str
    priority: str
    dimension: str | None = None
    description: str
    impact: str
    trend_refs: list[str] = []


class RecommendationSetResponse(BaseModel):
    """Collection of recommendations in API response."""

    recommendations: list[RecommendationResponse]
    llm_available: bool
    generated_at: str
    model_used: str | None = None
    error_message: str | None = None


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
    scored_commits = await _get_scored_commits(repository_url)
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
    scored_commits = await _get_scored_commits(repository_url)
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
    from_data = await _get_commit_by_sha(repository_url, from_commit)
    to_data = await _get_commit_by_sha(repository_url, to_commit)

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
    include_recommendations: bool = True,
) -> DashboardResponse:
    """Generate dashboard report."""
    from datetime import datetime, timezone

    from archi_c4_score.dashboard_service import get_recommendations_for_dashboard
    from archi_c4_score.hugo_export import DashboardGenerator
    from archi_c4_score.timeline import TimelineService

    service = TimelineService()
    scored_commits = await _get_scored_commits(repository_url)
    timeline = service.get_timeline(repository_url, scored_commits)
    trends = service.calculate_trends(timeline.commits)

    generator = DashboardGenerator()
    health_status = generator.calculate_health_status(
        [{"direction": t.direction.value} for t in trends]
    )

    from archi_c4_score.scoring import BackfillOrchestrator, ScoringEngine
    from archi_c4_score.treemap import generate_treemap

    c4_scoring_data = None
    treemap_cells = []
    if scored_commits:
        commit_sha = scored_commits[-1].get("commit_sha")
        orchestrator = BackfillOrchestrator(scoring_engine=ScoringEngine(), repository=None)
        containers = await orchestrator.get_container_scores(repository_url, commit_sha)
        components = await orchestrator.get_component_scores(repository_url, commit_sha)
        treemap = generate_treemap(containers, system_id="system")

        treemap_cells = [
            {
                "id": c.id,
                "name": c.name,
                "level": c.level,
                "score": c.score,
                "size": c.size,
                "parent_id": c.parent_id,
                "stereotype": c.stereotype,
            }
            for c in treemap
        ]

        component_cells = [
            {
                "id": c.node_id,
                "name": c.node_name,
                "composite": c.composite,
                "coupling": c.coupling,
                "instability_index": c.instability_index,
                "efferent_coupling": c.efferent_coupling,
                "afferent_coupling": c.afferent_coupling,
                "parent": c.parent,
            }
            for c in components
        ]

        # Calculate dimensions from Neo4j data for consistency with treemap/components
        if containers or components:
            all_coupling = [c.coupling for c in containers] + [c.coupling for c in components]
            avg_coupling = sum(all_coupling) / len(all_coupling) if all_coupling else 50.0

            dimensions = {
                "coupling": avg_coupling,
                "modularity": 100.0 - avg_coupling,
                "cohesion": 50.0 + (10 - abs(avg_coupling - 50)) / 2,
                "extensibility": 65.0,
                "maintainability": 70.0 - (avg_coupling - 30) * 0.3,
            }
            composite = 100.0 - avg_coupling
        else:
            dimensions = {}
            avg_coupling = 50.0
            composite = 0

        c4_scoring_data = {
            "composite_score": composite,
            "dimensions": dimensions,
            "element_count": scored_commits[-1].get("element_count", 0),
            "relationship_count": scored_commits[-1].get("relationship_count", 0),
            "commit": commit_sha,
            "treemap": treemap_cells,
            "components": component_cells,
        }

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
        c4_scoring=c4_scoring_data,
    )

    if include_recommendations:
        recommendations_data = get_recommendations_for_dashboard(
            repository_url=repository_url,
            repository_name=hugo_data.repository.get("name", "repository"),
            commits=timeline.commits,
            trends=trends,
            significant_changes=timeline.significant_changes,
        )
    else:
        recommendations_data = {
            "recommendations": [],
            "llm_available": False,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    return DashboardResponse(
        generated_at=hugo_data.generated,
        repository=hugo_data.repository,
        summary=hugo_data.summary,
        commits=hugo_data.commits,
        trends=hugo_data.trends,
        concerns=hugo_data.concerns,
        recommendations=recommendations_data,
        c4_scoring=c4_scoring_data,
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
    logger.info(f"Starting backfill for {repository_url}, count={commit_count}")

    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "architoolset")

    from archi_c4_score.graph import Neo4jConnection, ScoredCommitRepository
    from archi_c4_score.repository import Repository
    from archi_c4_score.scoring import BackfillOrchestrator, ScoringEngine

    try:
        conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
        await conn.connect()
        logger.info(f"Connected to Neo4j at {neo4j_uri}")

        repository = ScoredCommitRepository(conn)
        await repository.setup_indexes()
        logger.info("Neo4j indexes set up")

        git_repo = Repository(path="/tmp/archi-model")
        if not git_repo.is_git_repository():
            logger.info(f"Cloning repository {repository_url}")
            git_repo.clone(repository_url)
        else:
            logger.info("Using existing cloned repository")

        orchestrator = BackfillOrchestrator(
            scoring_engine=ScoringEngine(),
            repository=git_repo,
        )

        scored_commits = orchestrator.backfill(repository_url, commit_count)
        logger.info(f"Generated {len(scored_commits)} scored commits")

        for commit_data in scored_commits:
            await repository.save(commit_data)
            logger.info(f"Saved commit {commit_data.get('commit_sha', '?')[:7]}")

        await conn.close()
        logger.info(f"Backfill completed: {len(scored_commits)} commits")

        return BackfillResponse(
            status="completed",
            commits_queued=len(scored_commits),
            estimated_duration_seconds=len(scored_commits) * 2,
        )
    except Exception as e:
        logger.error(f"Backfill failed: {e}", exc_info=True)
        return BackfillResponse(
            status="failed",
            commits_queued=0,
            estimated_duration_seconds=0,
        )


@app.post("/api/v1/sync/github", response_model=BackfillResponse)
async def sync_github_commits(
    repository_url: str,
    branch: str = "main",
    model_filename: str = "model.archimate",
) -> BackfillResponse:
    """Fetch all commits from GitHub main branch and import models to Neo4j."""
    import logging
    import os
    import httpx

    logger = logging.getLogger(__name__)
    logger.info(f"Starting GitHub sync for {repository_url}, branch={branch}")

    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "architoolset")

    from archi_c4_score.graph import Neo4jConnection

    owner_repo = repository_url.rstrip("/").replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{owner_repo}/commits"

    commits_imported = 0
    commits_failed = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            response = await client.get(api_url, headers=headers, params={"per_page": 100})
            response.raise_for_status()
            commits = response.json()

            logger.info(f"Found {len(commits)} commits on {branch}")

            conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
            await conn.connect()

            for commit_info in commits:
                commit_sha = commit_info["sha"]
                commit_date = commit_info.get("commit", {}).get("committer", {}).get("date", "")

                model_url = (
                    f"https://raw.githubusercontent.com/{owner_repo}/{commit_sha}/{model_filename}"
                )
                logger.info(f"Trying {commit_sha[:7]}: {model_url}")

                try:
                    model_resp = await client.get(model_url)
                    if model_resp.status_code != 200:
                        logger.warning(f"No {model_filename} at {commit_sha[:7]}, skipping")
                        commits_failed += 1
                        continue

                    model = import_from_url(model_url)

                    from archi_c4_score.archimate_scorer import ArchimateScorer as Scorer

                    scorer = Scorer()
                    metrics = scorer.score_model(model)

                    nodes_created = 0
                    for elem in model.elements:
                        await conn.execute_query(
                            "MERGE (n:Element {id: $id, commit_sha: $commit_sha}) SET n.name = $name, n.element_type = $type, n.stereotype = $stereotype",
                            {
                                "id": elem.id,
                                "name": elem.name,
                                "type": elem.element_type,
                                "stereotype": elem.stereotype or "",
                                "commit_sha": commit_sha,
                            },
                        )
                        nodes_created += 1

                    rels_created = 0
                    for rel in model.relationships:
                        await conn.execute_query(
                            """MERGE (a:Element {id: $source_id, commit_sha: $commit_sha})
                            MERGE (b:Element {id: $target_id, commit_sha: $commit_sha})
                            MERGE (a)-[r:RELATES]->(b) SET r.rel_type = $rel_type""",
                            {
                                "source_id": rel.source_id,
                                "target_id": rel.target_id,
                                "rel_type": rel.relationship_type.replace("-", ""),
                                "commit_sha": commit_sha,
                            },
                        )
                        rels_created += 1

                    await conn.execute_query(
                        """MERGE (c:ScoredCommit {commit_sha: $sha})
                        SET c.repository_url = $repo_url,
                            c.commit_date = datetime($date),
                            c.scored_at = datetime($date),
                            c.element_count = $elem_count,
                            c.relationship_count = $rel_count,
                            c.composite_score = $composite_score,
                            c.coupling = $coupling,
                            c.modularity = $modularity,
                            c.cohesion = $cohesion,
                            c.extensibility = $extensibility,
                            c.maintainability = $maintainability""",
                        {
                            "sha": commit_sha,
                            "repo_url": repository_url,
                            "date": commit_date,
                            "elem_count": nodes_created,
                            "rel_count": rels_created,
                            "composite_score": metrics.composite_score,
                            "coupling": metrics.coupling,
                            "modularity": metrics.modularity,
                            "cohesion": metrics.cohesion,
                            "extensibility": metrics.extensibility,
                            "maintainability": metrics.maintainability,
                        },
                    )

                    commits_imported += 1
                    logger.info(
                        f"Imported {commit_sha[:7]}: {nodes_created} elements, {rels_created} relations"
                    )

                except Exception as e:
                    logger.warning(f"Failed to import {commit_sha[:7]}: {e}")
                    commits_failed += 1

            await conn.close()
            logger.info(f"Sync completed: {commits_imported} imported, {commits_failed} failed")

            return BackfillResponse(
                status="completed",
                commits_queued=commits_imported,
                estimated_duration_seconds=commits_imported * 2,
            )

        except Exception as e:
            logger.error(f"GitHub sync failed: {e}", exc_info=True)
            return BackfillResponse(
                status="failed",
                commits_queued=0,
                estimated_duration_seconds=0,
            )


async def _get_scored_commits(repository_url: str, limit: int = 30) -> list[dict]:
    """Get scored commits from Neo4j database."""
    import os

    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "architoolset")

    from archi_c4_score.graph import Neo4jConnection, ScoredCommitRepository

    commits = []
    try:
        conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
        await conn.connect()
        repo = ScoredCommitRepository(conn)
        records = await repo.find_by_repository(repository_url, limit=limit)
        for record in records:
            composite_score = record.get("composite_score")
            dims = {}
            if composite_score is not None:
                dims = {
                    "coupling": record.get("coupling"),
                    "modularity": record.get("modularity"),
                    "cohesion": record.get("cohesion"),
                    "extensibility": record.get("extensibility"),
                    "maintainability": record.get("maintainability"),
                }
            commits.append(
                {
                    "commit_sha": record.get("commit_sha", ""),
                    "repository_url": record.get("repository_url", repository_url),
                    "commit_date": record.get("commit_date", ""),
                    "author": record.get("author", "unknown"),
                    "message": record.get("message"),
                    "composite_score": composite_score,
                    "dimensions": dims,
                    "element_count": record.get("element_count", 0),
                    "relationship_count": record.get("relationship_count", 0),
                }
            )
        await conn.close()
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Failed to query Neo4j: {e}")
    return commits


async def _get_commit_by_sha(repository_url: str, sha: str) -> dict | None:
    """Get commit data by SHA from Neo4j."""
    import os

    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "architoolset")

    from archi_c4_score.graph import Neo4jConnection, ScoredCommitRepository

    try:
        conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
        await conn.connect()
        repo = ScoredCommitRepository(conn)
        record = await repo.find_by_sha(sha)
        await conn.close()
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
