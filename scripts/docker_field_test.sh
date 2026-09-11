#!/usr/bin/env bash
# Docker field test runner for CauterRule.
#
# v0.3.0 (default): builds the hardened image and runs the automated Docker
# test suite (`tests/field/test_docker_v030.py` + `tests/mcp/test_docker_http_transport.py`).
# Results are written to `field-test/0.3.0/docker/`:
#   - docker-results.jsonl   (per-test outcome + duration)
#   - docker-test-report.md   (markdown summary table)
#   - docker-junit.xml        (JUnit for CI)
#
# `--legacy` runs the v0.2.0-era 15 shell stages (kept for parity).
#
# Usage:
#   scripts/docker_field_test.sh                  # v0.3.0 suite
#   scripts/docker_field_test.sh --skip-build      # reuse existing image
#   scripts/docker_field_test.sh --verbose
#   scripts/docker_field_test.sh --legacy           # 15 shell stages
#   scripts/docker_field_test.sh --legacy --stage 6
set -euo pipefail

DOCKER_TAG="cauterule:field-test"
RESULTS_DIR="field-test/0.3.0/docker"
MODE="v030"
SKIP_BUILD=false
VERBOSE=false
SINGLE_STAGE=""

usage() {
    cat <<EOF
Usage: $0 [--legacy] [--skip-build] [--verbose] [--stage N] [--help]

  --legacy        Run the v0.2.0-era 15 shell stages instead of the v0.3.0 pytest suite.
  --skip-build    Reuse the existing ${DOCKER_TAG} image.
  --verbose       Stream pytest/stage output.
  --stage N       (legacy only) run a single stage N (1-15).
  --help          Show this message.

v0.3.0 results are written to ${RESULTS_DIR}/.
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help) usage ;;
        --legacy) MODE="legacy"; shift ;;
        --skip-build) SKIP_BUILD=true; shift ;;
        --verbose) VERBOSE=true; shift ;;
        --stage) SINGLE_STAGE="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p "$RESULTS_DIR"

# ── Build ──────────────────────────────────────────────────────────────────
if ! $SKIP_BUILD; then
    echo "--- building ${DOCKER_TAG}"
    if $VERBOSE; then
        docker build -t "$DOCKER_TAG" .
    else
        docker build -t "$DOCKER_TAG" . > /dev/null
    fi
fi

# ── v0.3.0: automated pytest suite ─────────────────────────────────────────
if [[ "$MODE" == "v030" ]]; then
    PYTEST_FLAGS=(-m docker --junit-xml="${RESULTS_DIR}/docker-junit.xml")
    if $VERBOSE; then
        PYTEST_FLAGS+=(-v)
    else
        PYTEST_FLAGS+=(-q)
    fi
    # The field conftest records per-test outcomes + the markdown report.
    # Run ALL docker-marked tests (inherited v0.1.0/v0.2.0 + new v0.3.0).
    echo "--- running v0.3.0 docker suite -> ${RESULTS_DIR}/"
    set +e
    .venv/bin/python -m pytest \
        tests/field/ tests/mcp/ \
        "${PYTEST_FLAGS[@]}" \
        -p no:cacheprovider \
        2>&1 | tee "${RESULTS_DIR}/docker-test.log"
    STATUS=${PIPESTATUS[0]}
    set -e
    echo ""
    echo "================================="
    echo "  v0.3.0 docker suite exit: ${STATUS}"
    echo "  results: ${RESULTS_DIR}/docker-results.jsonl"
    echo "           ${RESULTS_DIR}/docker-test-report.md"
    echo "           ${RESULTS_DIR}/docker-junit.xml"
    echo "================================="
    exit "$STATUS"
fi

# ── legacy: v0.2.0-era 15 shell stages ─────────────────────────────────────
TOTAL=15
PASS=0
FAIL=0

run_stage() {
    local num="$1" name="$2" cmd="$3"
    local label="[$num/$TOTAL] $name"
    if [[ -n "$SINGLE_STAGE" && "$SINGLE_STAGE" != "$num" ]]; then
        return 0
    fi
    echo "--- $label"
    if eval "$cmd" > /dev/null 2>&1; then
        echo "  PASS"; PASS=$((PASS + 1))
    else
        echo "  FAIL"; FAIL=$((FAIL + 1))
    fi
}

DOCKER_RUN="docker run --rm $DOCKER_TAG"
DOCKER_RUN_SH="docker run --rm $DOCKER_TAG sh -c"

run_stage  1 "build"        "docker build -t $DOCKER_TAG ."
run_stage  2 "unit"         "$DOCKER_RUN_SH 'pytest tests/ -m \"not slow and not docker\" --tb=short -q'"
run_stage  3 "scale"        "$DOCKER_RUN_SH 'pytest tests/scale/ -m \"not docker\" --tb=short -q'"
run_stage  4 "adversarial"  "$DOCKER_RUN_SH 'pytest tests/adversarial/ -m \"not docker\" --tb=short -q'"
run_stage  5 "corpus"       "$DOCKER_RUN_SH 'pytest tests/corpus/ -m \"not docker\" --tb=short -q'"
run_stage  6 "CLI"          "$DOCKER_RUN_SH 'pytest tests/cli/ -m \"not docker\" --tb=short -q'"
run_stage  7 "TUI"          "$DOCKER_RUN_SH 'pytest tests/tui/ -m \"not docker\" --tb=short -q'"
run_stage  8 "MCP"          "docker run --rm --entrypoint python $DOCKER_TAG -c 'from cauterule.mcp.server import CauterRuleMCPServer; print(\"MCP import OK\")'"
run_stage  9 "pipeline"     "$DOCKER_RUN demo --failures 1"
run_stage 10 "demo"         "$DOCKER_RUN demo --failures 1"
run_stage 11 "redaction"    "$DOCKER_RUN_SH 'pytest tests/redaction/ -m \"not docker\" --tb=short -q'"
run_stage 12 "export"       "$DOCKER_RUN_SH 'pytest tests/export/ -m \"not docker\" --tb=short -q'"
run_stage 13 "git"          "$DOCKER_RUN_SH 'pytest tests/extraction/ -m \"not docker\" --tb=short -q'"
run_stage 14 "loop"         "$DOCKER_RUN_SH 'pytest tests/loop/ -m \"not docker\" --tb=short -q'"
run_stage 15 "multi-env"    "$DOCKER_RUN_SH 'pytest tests/field/ -m docker --tb=short -q'"

echo ""
echo "================================="
echo "  Legacy results: $PASS passed, $FAIL failed, $TOTAL total"
echo "================================="
[[ "$FAIL" -eq 0 ]]
