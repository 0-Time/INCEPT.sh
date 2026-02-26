#!/bin/bash
# rollback.sh — Stop current container, start previous version, verify health
set -euo pipefail

CURRENT_TAG="${CURRENT_TAG:-latest}"
PREVIOUS_TAG="${PREVIOUS_TAG:-}"
CONTAINER_NAME="${CONTAINER_NAME:-incept}"
SMOKE_SCRIPT="$(dirname "$0")/smoke_test.sh"

if [ -z "$PREVIOUS_TAG" ]; then
    echo "Error: PREVIOUS_TAG must be set"
    echo "Usage: PREVIOUS_TAG=v0.1.0 ./rollback.sh"
    exit 1
fi

echo "Rolling back from $CURRENT_TAG to $PREVIOUS_TAG"

# Stop current container
echo "Stopping current container..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# Start previous version
echo "Starting $PREVIOUS_TAG..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p 8080:8080 \
    "incept:$PREVIOUS_TAG"

# Wait for startup
echo "Waiting for startup..."
sleep 5

# Run smoke test
echo "Running smoke tests..."
if bash "$SMOKE_SCRIPT"; then
    echo "Rollback successful — $PREVIOUS_TAG is healthy"
    exit 0
else
    echo "Rollback FAILED — $PREVIOUS_TAG smoke tests did not pass"
    exit 1
fi
