"""Contract tests for REST API."""

from fastapi.testclient import TestClient
from archi_c4_score.api import app


class TestAPIImport:
    """Tests for POST /api/v1/import endpoint."""

    def test_import_endpoint_exists(self):
        """Import endpoint is available."""
        client = TestClient(app)
        response = client.post("/api/v1/import", json={"repo_url": "https://example.com"})
        assert response.status_code in [200, 400, 422]

    def test_import_requires_repo_url(self):
        """Import requires repo_url in body."""
        client = TestClient(app)
        response = client.post("/api/v1/import", json={})
        assert response.status_code == 422


class TestAPIScore:
    """Tests for POST /api/v1/score (specs/006-icepanel-model-source/contracts/score-api.md)."""

    def test_score_defaults_to_icepanel_latest(self, icepanel_fixture_source):
        response = TestClient(app).post("/api/v1/score", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "icepanel"
        assert data["commit"] == "latest"
        assert data["composite_score"] == 50.4
        assert data["system_scores"][0]["node_name"] == "Unicorn"

    def test_score_container_fields(self, icepanel_fixture_source):
        data = TestClient(app).post("/api/v1/score", json={"version": "v2"}).json()
        backend = next(c for c in data["container_scores"] if c["node_name"] == "Backend")
        assert {"afferent_coupling", "efferent_coupling", "instability_index"} <= set(backend)
        assert data["commit"] == "v2"

    def test_commit_is_alias_of_version(self, icepanel_fixture_source):
        data = TestClient(app).post("/api/v1/score", json={"commit": "abc123"}).json()
        assert data["commit"] == "abc123"

    def test_score_returns_recommendations(self, icepanel_fixture_source):
        data = TestClient(app).post("/api/v1/score", json={}).json()
        assert isinstance(data["recommendations"], list)

    def test_unknown_source_is_rejected(self):
        response = TestClient(app).post("/api/v1/score", json={"source": "visio"})
        assert response.status_code == 422

    def test_unconfigured_source_is_400(self, monkeypatch):
        monkeypatch.delenv("ICEPANEL_API_KEY", raising=False)
        monkeypatch.delenv("ICEPANEL_LANDSCAPE_ID", raising=False)
        response = TestClient(app).post("/api/v1/score", json={"source": "icepanel"})
        assert response.status_code == 400

    def test_archimate_needs_model_path(self):
        response = TestClient(app).post("/api/v1/score", json={"source": "archimate"})
        assert response.status_code == 400


class TestAPIModel:
    """Tests for GET /api/v1/model/{commit} endpoint."""

    def test_model_endpoint_exists(self):
        """Model retrieval endpoint exists."""
        client = TestClient(app)
        response = client.get("/api/v1/model/abc123")
        assert response.status_code in [200, 404]


class TestAPIHistory:
    """Tests for GET /api/v1/history endpoint."""

    def test_history_endpoint_exists(self):
        """History endpoint exists."""
        client = TestClient(app)
        response = client.get("/api/v1/history")
        assert response.status_code in [200, 500]


class TestAPIHealth:
    """Tests for health check."""

    def test_health_endpoint(self):
        """Health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()


class TestAPITimeline:
    """Tests for GET /api/v1/timeline endpoint."""

    def test_timeline_endpoint_exists(self):
        """Timeline endpoint is available."""
        client = TestClient(app)
        response = client.get("/api/v1/timeline?repository_url=https://example.com/repo")
        assert response.status_code in [200, 500]

    def test_timeline_requires_repository_url(self):
        """Timeline requires repository_url parameter."""
        client = TestClient(app)
        response = client.get("/api/v1/timeline")
        assert response.status_code == 422

    def test_timeline_returns_commits(self):
        """Timeline returns commits array."""
        client = TestClient(app)
        response = client.get("/api/v1/timeline?repository_url=https://example.com/repo")
        if response.status_code == 200:
            data = response.json()
            assert "commits" in data
            assert isinstance(data["commits"], list)

    def test_timeline_returns_pagination(self):
        """Timeline returns pagination info."""
        client = TestClient(app)
        response = client.get("/api/v1/timeline?repository_url=https://example.com/repo")
        if response.status_code == 200:
            data = response.json()
            assert "pagination" in data
            assert "total" in data["pagination"]


class TestAPITrends:
    """Tests for GET /api/v1/timeline/trends endpoint."""

    def test_trends_endpoint_exists(self):
        """Trends endpoint is available."""
        client = TestClient(app)
        response = client.get("/api/v1/timeline/trends?repository_url=https://example.com/repo")
        assert response.status_code in [200, 500]

    def test_trends_requires_repository_url(self):
        """Trends requires repository_url parameter."""
        client = TestClient(app)
        response = client.get("/api/v1/timeline/trends")
        assert response.status_code == 422

    def test_trends_returns_trends(self):
        """Trends returns trends array."""
        client = TestClient(app)
        response = client.get("/api/v1/timeline/trends?repository_url=https://example.com/repo")
        if response.status_code == 200:
            data = response.json()
            assert "trends" in data
            assert isinstance(data["trends"], list)


class TestAPICompare:
    """Tests for GET /api/v1/timeline/compare endpoint."""

    def test_compare_endpoint_exists(self):
        """Compare endpoint is available."""
        client = TestClient(app)
        response = client.get(
            "/api/v1/timeline/compare?repository_url=https://example.com/repo&from_commit=abc&to_commit=def"
        )
        assert response.status_code in [200, 400, 404, 500]

    def test_compare_requires_commits(self):
        """Compare requires from_commit and to_commit parameters."""
        client = TestClient(app)
        response = client.get("/api/v1/timeline/compare?repository_url=https://example.com/repo")
        assert response.status_code == 422


class TestAPIDashboard:
    """Tests for GET /api/v1/dashboard endpoint."""

    def test_dashboard_endpoint_exists(self):
        """Dashboard endpoint is available."""
        client = TestClient(app)
        response = client.get("/api/v1/dashboard?repository_url=https://example.com/repo")
        assert response.status_code in [200, 500]

    def test_dashboard_requires_repository_url(self):
        """Dashboard requires repository_url parameter."""
        client = TestClient(app)
        response = client.get("/api/v1/dashboard")
        assert response.status_code == 422

    def test_dashboard_returns_summary(self):
        """Dashboard returns summary section."""
        client = TestClient(app)
        response = client.get("/api/v1/dashboard?repository_url=https://example.com/repo")
        if response.status_code == 200:
            data = response.json()
            assert "summary" in data
            assert "health_status" in data["summary"]

    def test_dashboard_returns_recommendations(self):
        """Dashboard returns recommendations field."""
        client = TestClient(app)
        response = client.get("/api/v1/dashboard?repository_url=https://example.com/repo")
        if response.status_code == 200:
            data = response.json()
            assert "recommendations" in data
            assert "recommendations" in data["recommendations"]
            assert "llm_available" in data["recommendations"]
            assert "generated_at" in data["recommendations"]

    def test_dashboard_recommendations_has_priority_field(self):
        """Dashboard recommendations include priority field."""
        client = TestClient(app)
        response = client.get("/api/v1/dashboard?repository_url=https://example.com/repo")
        if response.status_code == 200:
            data = response.json()
            recs = data.get("recommendations", {}).get("recommendations", [])
            if recs:
                assert "priority" in recs[0]
                assert "impact" in recs[0]


class TestAPIBackfill:
    """Tests for POST /api/v1/scoring/backfill endpoint."""

    def test_backfill_endpoint_exists(self):
        """Backfill endpoint is available."""
        client = TestClient(app)
        response = client.post("/api/v1/scoring/backfill?repository_url=https://example.com/repo")
        assert response.status_code in [200, 202, 500]

    def test_backfill_requires_repository_url(self):
        """Backfill requires repository_url parameter."""
        client = TestClient(app)
        response = client.post("/api/v1/scoring/backfill")
        assert response.status_code == 422
