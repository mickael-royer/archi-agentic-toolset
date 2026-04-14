"""REST API for C4 Architecture Scoring."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from archi_c4_score import __version__

app = FastAPI(
    title="C4 Architecture Scoring API",
    version=__version__,
    description="Score and analyze C4 architecture models stored in Neo4j",
)


class ImportRequest(BaseModel):
    """Request body for import endpoint."""

    repo_url: str = Field(..., description="coArchi2 repository URL")
    neo4j_uri: str | None = "bolt://localhost:7687"
    neo4j_user: str | None = "neo4j"
    neo4j_password: str | None = None


class ImportResponse(BaseModel):
    """Response for import endpoint."""

    commit: str
    nodes_imported: int
    relationships_imported: int


class ScoreRequest(BaseModel):
    """Request body for score endpoint."""

    commit: str = Field(..., description="Git commit SHA")


class ScoreResponse(BaseModel):
    """Response for score endpoint."""

    commit: str
    composite_score: float
    system_scores: list[dict]
    container_scores: list[dict]
    component_scores: list[dict]
    recommendations: list[dict]


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


@app.post("/api/v1/import", response_model=ImportResponse)
async def import_model(request: ImportRequest) -> ImportResponse:
    """Import a C4 model from a coArchi2 repository."""
    return ImportResponse(
        commit="abc123def456",
        nodes_imported=0,
        relationships_imported=0,
    )


@app.post("/api/v1/score", response_model=ScoreResponse)
async def score_model(request: ScoreRequest) -> ScoreResponse:
    """Score an architecture at a specific commit."""
    return ScoreResponse(
        commit=request.commit,
        composite_score=85.0,
        system_scores=[],
        container_scores=[],
        component_scores=[],
        recommendations=[],
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
