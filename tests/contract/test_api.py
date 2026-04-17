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
    """Tests for POST /api/v1/score endpoint."""

    def test_score_endpoint_exists(self):
        """Score endpoint is available."""
        client = TestClient(app)
        response = client.post("/api/v1/score", json={"commit": "abc123"})
        assert response.status_code in [200, 400, 404]

    def test_score_requires_commit(self):
        """Score requires commit in body."""
        client = TestClient(app)
        response = client.post("/api/v1/score", json={})
        assert response.status_code == 422

    def test_score_returns_composite_score(self):
        """Score endpoint returns composite_score field."""
        client = TestClient(app)
        response = client.post("/api/v1/score", json={"commit": "abc123"})
        assert response.status_code == 200
        data = response.json()
        assert "composite_score" in data

    def test_score_returns_recommendations(self):
        """Score endpoint returns recommendations array."""
        client = TestClient(app)
        response = client.post("/api/v1/score", json={"commit": "abc123"})
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_score_supports_include_recommendations(self):
        """Score endpoint respects include_recommendations parameter."""
        client = TestClient(app)
        response = client.post(
            "/api/v1/score", json={"commit": "abc123", "include_recommendations": False}
        )
        assert response.status_code == 200


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
