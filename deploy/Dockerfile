# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

COPY ../src/pyproject.toml ../src/uv.lock ./
RUN pip install --target=/app/lib uv && \
    uv sync --frozen --no-dev --target /app/lib

COPY ../src/ ./src/

# Production stage - distroless
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /app/lib /app/lib
COPY --from=builder /app/src /app/src

# Add uv to path for runtime
ENV PYTHONPATH=/app/lib:/app/src
ENV PATH=/app/lib/bin:$PATH

# Non-root user for security
USER nonroot

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["archi_c4_score.api:app", "--host", "0.0.0.0", "--port", "8000"]