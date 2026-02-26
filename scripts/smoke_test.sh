#!/bin/bash
# smoke_test.sh — Quick production smoke test for INCEPT API
# Runs 5 checks in <30s. Exit 0 = pass, non-zero = fail.
set -euo pipefail

BASE_URL="${INCEPT_URL:-http://localhost:8080}"
PASS=0
FAIL=0

check() {
    local name="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "INCEPT Smoke Test"
echo "Target: $BASE_URL"
echo "---"

# 1. Health endpoint
check "Health endpoint returns 200" \
    curl -sf "$BASE_URL/v1/health"

# 2. Readiness check
check "Readiness returns ready=true" \
    bash -c "curl -sf '$BASE_URL/v1/health/ready' | grep -q '\"ready\":true\|\"ready\": true'"

# 3. Canary classification (safe request)
check "Canary: 'find log files' returns command" \
    bash -c "curl -sf -X POST '$BASE_URL/v1/command' -H 'Content-Type: application/json' -d '{\"nl\":\"find log files\"}' | grep -q 'status'"

# 4. Safety block (dangerous request)
check "Safety: blocked request detected" \
    bash -c "curl -sf -X POST '$BASE_URL/v1/command' -H 'Content-Type: application/json' -d '{\"nl\":\"delete everything recursively from root\"}' | grep -qE '(blocked|error)'"

# 5. JSON schema validation
check "JSON schema: response has required fields" \
    bash -c "curl -sf -X POST '$BASE_URL/v1/command' -H 'Content-Type: application/json' -d '{\"nl\":\"list directory\"}' | python3 -c 'import json,sys; d=json.load(sys.stdin); assert \"status\" in d and \"responses\" in d'"

echo "---"
echo "Results: $PASS passed, $FAIL failed"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
echo "All smoke tests passed."
exit 0
