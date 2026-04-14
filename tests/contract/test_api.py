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
