"""Integration tests for local development with podman-compose."""

from fastapi.testclient import TestClient


class TestLocalDevelopment:
    """Tests for local development setup."""

    def test_health_endpoint(self):
        """Health endpoint returns healthy status."""
        from archi_c4_score.api import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_dapr_health_endpoint(self):
        """Dapr health endpoint returns ready status."""
        from archi_c4_score.api import app

        client = TestClient(app)
        response = client.get("/dapr/health")
        assert response.status_code == 200
        assert response.json()["status"] == "dapr-ready"

    def test_api_version_in_health(self):
        """Health response includes version."""
        from archi_c4_score.api import app
        from archi_c4_score import __version__

        client = TestClient(app)
        response = client.get("/health")
        assert response.json()["version"] == __version__


class TestScoringEndpoints:
    """Tests for scoring API endpoints."""

    def test_score_endpoint_exists(self):
        """Score endpoint is available."""
        from archi_c4_score.api import app

        client = TestClient(app)
        response = client.post("/api/v1/score", json={"commit": "abc123"})
        assert response.status_code == 200

    def test_model_endpoint_exists(self):
        """Model endpoint is available."""
        from archi_c4_score.api import app

        client = TestClient(app)
        response = client.get("/api/v1/model/abc123")
        assert response.status_code == 200

    def test_history_endpoint_exists(self):
        """History endpoint is available."""
        from archi_c4_score.api import app

        client = TestClient(app)
        response = client.get("/api/v1/history")
        assert response.status_code == 200

    def test_history_with_limit(self):
        """History endpoint supports limit parameter."""
        from archi_c4_score.api import app

        client = TestClient(app)
        response = client.get("/api/v1/history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["commits"]) <= 5
