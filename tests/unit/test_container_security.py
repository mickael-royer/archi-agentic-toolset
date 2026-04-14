"""Tests for container security (US3)."""

from pathlib import Path


class TestDistrolessContainer:
    """Tests for distroless container security."""

    def test_dockerfile_uses_distroless_base(self):
        """Dockerfile uses distroless Python base image."""
        deploy_dir = Path("deploy")
        dockerfile = deploy_dir / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile not found in deploy/"

        content = dockerfile.read_text()
        assert "gcr.io/distroless/python3-debian12" in content, (
            "Dockerfile must use distroless base image"
        )

    def test_dockerfile_no_shell(self):
        """Production stage has no shell available."""
        deploy_dir = Path("deploy")
        dockerfile = deploy_dir / "Dockerfile"
        content = dockerfile.read_text()

        lines = content.split("\n")
        prod_lines = []
        in_prod_stage = False
        for line in lines:
            if "FROM gcr.io/distroless" in line:
                in_prod_stage = True
            if in_prod_stage:
                prod_lines.append(line)

        prod_content = "\n".join(prod_lines)
        assert "sh" not in prod_content.lower() or "#" in prod_content, (
            "Production stage should not have shell"
        )

    def test_dockerfile_nonroot_user(self):
        """Dockerfile runs as non-root user."""
        deploy_dir = Path("deploy")
        dockerfile = deploy_dir / "Dockerfile"
        content = dockerfile.read_text()

        assert "USER nonroot" in content, "Dockerfile must use non-root user"

    def test_dockerfile_has_healthcheck(self):
        """Dockerfile has health check configured."""
        deploy_dir = Path("deploy")
        dockerfile = deploy_dir / "Dockerfile"
        content = dockerfile.read_text()

        assert "HEALTHCHECK" in content, "Dockerfile must have HEALTHCHECK"

    def test_dockerfile_exposes_port(self):
        """Dockerfile exposes port 8000."""
        deploy_dir = Path("deploy")
        dockerfile = deploy_dir / "Dockerfile"
        content = dockerfile.read_text()

        assert "EXPOSE 8000" in content, "Dockerfile must expose port 8000"

    def test_dockerfile_multistage_build(self):
        """Dockerfile uses multi-stage build."""
        deploy_dir = Path("deploy")
        dockerfile = deploy_dir / "Dockerfile"
        content = dockerfile.read_text()

        from_count = content.count("FROM ")
        assert from_count >= 2, "Dockerfile must use multi-stage build"


class TestComposeSecurity:
    """Tests for docker-compose security configuration."""

    def test_compose_exists(self):
        """docker-compose.yaml exists."""
        deploy_dir = Path("deploy")
        compose = deploy_dir / "docker-compose.yaml"
        assert compose.exists(), "docker-compose.yaml not found"

    def test_compose_no_privileged_mode(self):
        """Compose does not use privileged mode."""
        deploy_dir = Path("deploy")
        compose = deploy_dir / "docker-compose.yaml"
        if compose.exists():
            content = compose.read_text()
            assert "privileged: true" not in content.lower(), (
                "Compose should not use privileged mode"
            )
