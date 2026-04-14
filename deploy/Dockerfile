# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY src/ ./src/

# Production stage - distroless
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

COPY --from=builder /app/src /app/src

USER nonroot

EXPOSE 8000

ENV PYTHONPATH=/app/src

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["archi_c4_score.api:app", "--host", "0.0.0.0", "--port", "8000"]