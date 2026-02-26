#!/usr/bin/env bash
# build_offline_bundle.sh -- Build an offline distribution bundle for air-gapped deployment.
#
# Creates a tarball containing:
#   - Docker image (via docker save)
#   - GGUF model file
#   - Documentation
#   - README with deployment instructions
#
# Usage:
#   ./scripts/build_offline_bundle.sh [version]
#
# Examples:
#   ./scripts/build_offline_bundle.sh 0.3.0
#   ./scripts/build_offline_bundle.sh          # uses version from incept/__init__.py
#
# Requirements:
#   - Docker (for building and saving the image)
#   - A GGUF model file at models/v1/model.gguf (or set INCEPT_MODEL_PATH)

set -euo pipefail

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

IMAGE_NAME="incept"
MODEL_PATH="${INCEPT_MODEL_PATH:-$PROJECT_ROOT/models/v1/model.gguf}"
BUNDLE_DIR="$PROJECT_ROOT/dist"

# Determine version
if [[ -n "${1:-}" ]]; then
    VERSION="$1"
else
    VERSION=$(python3 -c "
import re, pathlib
text = pathlib.Path('$PROJECT_ROOT/incept/__init__.py').read_text()
match = re.search(r'__version__\s*=\s*[\"'\''](.*?)[\"'\'']', text)
print(match.group(1) if match else '0.0.0')
")
fi

IMAGE_TAG="${IMAGE_NAME}:${VERSION}"
BUNDLE_NAME="incept-${VERSION}-offline"
BUNDLE_PATH="${BUNDLE_DIR}/${BUNDLE_NAME}"

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
info()  { echo "[INFO]  $*"; }
warn()  { echo "[WARN]  $*" >&2; }
error() { echo "[ERROR] $*" >&2; exit 1; }

check_prereqs() {
    command -v docker >/dev/null 2>&1 || error "Docker is required but not found in PATH."
    command -v tar    >/dev/null 2>&1 || error "tar is required but not found in PATH."
}

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
main() {
    check_prereqs

    info "Building INCEPT offline bundle v${VERSION}"
    info "Project root: $PROJECT_ROOT"
    info "Model path:   $MODEL_PATH"
    info "Bundle path:  ${BUNDLE_PATH}.tar.gz"
    echo "---"

    # -- Step 1: Build Docker image -----------------------------------
    info "Step 1/5: Building Docker image ${IMAGE_TAG} ..."
    docker build -t "$IMAGE_TAG" -t "${IMAGE_NAME}:latest" "$PROJECT_ROOT"
    info "Docker image built successfully."

    # -- Step 2: Create bundle directory ------------------------------
    info "Step 2/5: Creating bundle directory ..."
    rm -rf "$BUNDLE_PATH"
    mkdir -p "$BUNDLE_PATH"/{docker,model,docs,scripts}

    # -- Step 3: Export Docker image ----------------------------------
    info "Step 3/5: Saving Docker image (this may take a few minutes) ..."
    docker save "$IMAGE_TAG" | gzip > "$BUNDLE_PATH/docker/${IMAGE_NAME}-${VERSION}.tar.gz"
    info "Docker image saved: docker/${IMAGE_NAME}-${VERSION}.tar.gz"

    # -- Step 4: Copy model and docs ----------------------------------
    info "Step 4/5: Copying model and documentation ..."

    # Model file
    if [[ -f "$MODEL_PATH" ]]; then
        cp "$MODEL_PATH" "$BUNDLE_PATH/model/"
        info "Model copied: model/$(basename "$MODEL_PATH")"
    else
        warn "Model file not found at $MODEL_PATH -- skipping."
        warn "You can add it manually to ${BUNDLE_PATH}/model/ before distributing."
    fi

    # Documentation
    for doc in README.md LICENSE CHANGELOG.md SECURITY.md; do
        if [[ -f "$PROJECT_ROOT/$doc" ]]; then
            cp "$PROJECT_ROOT/$doc" "$BUNDLE_PATH/docs/"
        fi
    done

    # Copy docs directory if it exists
    if [[ -d "$PROJECT_ROOT/docs" ]]; then
        cp -r "$PROJECT_ROOT/docs/"* "$BUNDLE_PATH/docs/" 2>/dev/null || true
    fi

    # Copy smoke test for post-deployment verification
    if [[ -f "$PROJECT_ROOT/scripts/smoke_test.sh" ]]; then
        cp "$PROJECT_ROOT/scripts/smoke_test.sh" "$BUNDLE_PATH/scripts/"
        chmod +x "$BUNDLE_PATH/scripts/smoke_test.sh"
    fi

    # -- Step 4b: Generate deployment README --------------------------
    cat > "$BUNDLE_PATH/DEPLOY.md" <<'DEPLOY_EOF'
# INCEPT Offline Deployment Guide

This bundle contains everything needed to run INCEPT on an air-gapped machine.

## Contents

```
docker/         Docker image (compressed tar)
model/          GGUF model file
docs/           Documentation
scripts/        Deployment and verification scripts
DEPLOY.md       This file
```

## Prerequisites

- Docker Engine 20.10+ (must be pre-installed on the target machine)
- 2 GB available disk space
- 1 GB available RAM

## Deployment Steps

### 1. Transfer the bundle

Copy the tarball to the target machine via USB, SCP, or any available method:

```bash
scp incept-*-offline.tar.gz user@target:/tmp/
```

### 2. Extract the bundle

```bash
cd /opt
tar xzf /tmp/incept-*-offline.tar.gz
cd incept-*-offline
```

### 3. Load the Docker image

```bash
docker load < docker/incept-*.tar.gz
```

### 4. Copy the model file

If the model was included in the bundle:

```bash
mkdir -p /opt/incept-models
cp model/*.gguf /opt/incept-models/
```

### 5. Run the container

```bash
docker run -d \
    --name incept \
    --restart unless-stopped \
    --network none \
    -p 8080:8080 \
    -v /opt/incept-models:/app/models/v1:ro \
    -e INCEPT_SAFE_MODE=true \
    -e INCEPT_LOG_LEVEL=info \
    --memory 1g \
    --cpus 2.0 \
    incept:latest
```

### 6. Verify the deployment

```bash
# Wait for model to load (usually <10 seconds)
sleep 10

# Run smoke tests
bash scripts/smoke_test.sh

# Or manually check health
curl -s http://localhost:8080/v1/health/ready
```

### 7. (Optional) Set up API key authentication

```bash
docker run -d \
    --name incept \
    -p 8080:8080 \
    -e INCEPT_API_KEY=your-secret-key-here \
    -v /opt/incept-models:/app/models/v1:ro \
    incept:latest
```

## Verification

After deployment, verify offline operation:

```bash
# Confirm no network access
docker inspect incept | grep -i network

# Test a command
curl -s -X POST http://localhost:8080/v1/command \
    -H 'Content-Type: application/json' \
    -d '{"nl": "list files in /tmp"}' | python3 -m json.tool
```

## Troubleshooting

- **Container won't start:** Check `docker logs incept` for errors.
- **Model not found:** Verify the model volume mount path matches `INCEPT_MODEL_PATH`.
- **Port conflict:** Change the host port: `-p 9090:8080`.
- **Out of memory:** Increase the memory limit: `--memory 2g`.

For detailed troubleshooting, see `docs/troubleshooting.md`.
DEPLOY_EOF

    # -- Step 5: Create tarball ---------------------------------------
    info "Step 5/5: Creating tarball ..."
    cd "$BUNDLE_DIR"
    tar czf "${BUNDLE_NAME}.tar.gz" "$(basename "$BUNDLE_PATH")"
    rm -rf "$BUNDLE_PATH"

    # -- Summary ------------------------------------------------------
    echo ""
    echo "=========================================="
    info "Offline bundle created successfully."
    echo "=========================================="
    echo ""
    echo "  File:    ${BUNDLE_DIR}/${BUNDLE_NAME}.tar.gz"
    echo "  Size:    $(du -h "${BUNDLE_DIR}/${BUNDLE_NAME}.tar.gz" | cut -f1)"
    echo "  Version: ${VERSION}"
    echo "  Image:   ${IMAGE_TAG}"
    echo ""
    echo "  To deploy on an air-gapped machine:"
    echo "    1. Copy ${BUNDLE_NAME}.tar.gz to the target"
    echo "    2. tar xzf ${BUNDLE_NAME}.tar.gz"
    echo "    3. cd ${BUNDLE_NAME} && cat DEPLOY.md"
    echo ""
}

main "$@"
