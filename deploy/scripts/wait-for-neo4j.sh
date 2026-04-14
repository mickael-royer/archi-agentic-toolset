#!/bin/bash
# Wait for Neo4j to be ready before starting the application

set -e

NEO4J_HOST="${NEO4J_HOST:-localhost}"
NEO4J_PORT="${NEO4J_PORT:-7474}"
MAX_RETRIES="${MAX_RETRIES:-30}"
RETRY_INTERVAL="${RETRY_INTERVAL:-2}"

echo "Waiting for Neo4j at $NEO4J_HOST:$NEO4J_PORT..."

for i in $(seq 1 $MAX_RETRIES); do
    if curl -s "http://$NEO4J_HOST:$NEO4J_PORT" > /dev/null 2>&1; then
        echo "Neo4j is ready!"
        exit 0
    fi
    echo "Attempt $i/$MAX_RETRIES - Neo4j not ready, waiting ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
done

echo "ERROR: Neo4j did not become ready within ${MAX_RETRIES} attempts"
exit 1
