FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml src/README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

EXPOSE 8000

ENV PYTHONPATH=/app/src

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["archi_c4_score.api:app", "--host", "0.0.0.0", "--port", "8000"]