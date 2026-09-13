#!/usr/bin/env bash
# Docker field test runner for CauterRule.
#
# v0.3.1 (default): builds the hardened image and runs the automated Docker
# test suite (`tests/field/test_docker_v030.py`, `tests/field/test_docker_v031.py`,
# plus `tests/mcp/test_docker_http_transport.py`).
# Raw results are written to `field-test/results/0.3.1/docker/`:
#   - docker-results.jsonl   (per-test outcome + duration)
#   - docker-test-report.md   (markdown summary table)
#   - docker-junit.xml        (JUnit for CI)
#   - docker-test.log         (full pytest output)
#
# `--legacy` runs the v0.2.0-era 15 shell stages (kept for parity).
# `--v030` runs the v0.3.1 suite but writes to the v0.3.0 results dir for parity.
#
# Usage:
#   scripts/docker_field_test.sh                  # v0.3.1 suite
#   scripts/docker_field_test.sh --skip-build      # reuse existing image
#   scripts/docker_field_test.sh --verbose
#   scripts/docker_field_test.sh --legacy           # 15 shell stages
#   scripts/docker_field_test.sh --legacy --stage 6
set -euo pipefail

DOCKER_TAG="cauterule:field-test"
RESULTS_DIR="field-test/results/0.3.1/docker"
MODE="v031"
SKIP_BUILD=false
VERBOSE=false
SETUP_ONLY=false
SINGLE_STAGE=""
COMPOSE_PROJECT="cauterule-field-test"

usage() {
    cat <<EOF
Usage: $0 [--legacy] [--v030] [--skip-build] [--setup-only] [--verbose] [--stage N] [--help]

  --legacy        Run the v0.2.0-era 15 shell stages instead of the pytest suite.
  --v030          Run the pytest suite but write results to 0.3.0/docker/ (parity).
  --skip-build    Reuse the existing ${DOCKER_TAG} image.
  --setup-only    Build, bring up all compose services, verify they are up, then stop.
                  Do NOT run the test suite. Exits 1 with service logs if any
                  service fails to come up.
  --verbose       Stream pytest/stage output.
  --stage N       (legacy only) run a single stage N (1-15).
  --help          Show this message.

v0.3.1 results are written to ${RESULTS_DIR}/.
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help) usage ;;
        --legacy) MODE="legacy"; shift ;;
        --v030) RESULTS_DIR="field-test/results/0.3.0/docker"; shift ;;
        --skip-build) SKIP_BUILD=true; shift ;;
        --setup-only) SETUP_ONLY=true; shift ;;
        --verbose) VERBOSE=true; shift ;;
        --stage) SINGLE_STAGE="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p "$RESULTS_DIR"
# Fresh live-status files for this run.
rm -f "${RESULTS_DIR}/docker-results.jsonl" "${RESULTS_DIR}/docker-progress.log"

echo "============================================================"
echo " CauterRule Docker field test — v0.3.1"
echo " started:       $(date '+%Y-%m-%d %H:%M:%S')"
echo " image:         ${DOCKER_TAG}"
echo " results dir:   ${RESULTS_DIR}"
echo " suites:"
echo "   - tests/field/test_docker_v031.py   (new v0.3.1 fixes)"
echo "   - tests/field/test_docker_v030.py   (v0.3.0 surface, re-run)"
echo "   - tests/field/test_docker_*.py      (v0.1.0/v0.2.0 inherited)"
echo "   - tests/mcp/test_docker_http_transport.py (bearer auth)"
echo " watch live:    tail -f ${RESULTS_DIR}/docker-progress.log"
echo "============================================================"

# ── Build ──────────────────────────────────────────────────────────────────
if ! $SKIP_BUILD; then
    echo "--- [$(date +%H:%M:%S)] building ${DOCKER_TAG} (log: ${RESULTS_DIR}/docker-build.log)"
    docker build -t "$DOCKER_TAG" . 2>&1 | tee "${RESULTS_DIR}/docker-build.log" | tail -3
    echo "--- [$(date +%H:%M:%S)] build done"
fi

# ── Setup: bring up all runtime services and verify they are up ────────────
# Brings up the compose stack, waits for it to settle, checks every service's
# state (and exit code for one-shots), and dumps that service's logs if it did
# not come up. The MCP HTTP daemon is the service the suite drives, so it must
# also ANSWER an MCP request. If anything is down, we stop (no tests) and
# surface the logs. The `test` profile (in-container unit-suite job) is a CI
# job and is intentionally excluded from the runtime stack.
COMPOSE_ARGS=(-f docker-compose.yaml -p "$COMPOSE_PROJECT"
    --profile demo --profile mcp --profile mcp-http)
export CAUTERULE_MCP_TOKEN="${CAUTERULE_MCP_TOKEN:-ft-token}"
MCP_PORT=8025   # cauterule-mcp-http maps 8025:8025

verify_services() {
    local i svc state exitcode status bad=0 code
    echo "--- [$(date +%H:%M:%S)] setup: docker compose up -d (runtime services)"
    docker compose "${COMPOSE_ARGS[@]}" up -d 2>&1 | tail -6
    # Wait up to ~60s for the stack to settle (one-shots exit, daemons start).
    for i in $(seq 1 30); do sleep 2; done
    echo "--- [$(date +%H:%M:%S)] service states"
    local lines
    lines=$(docker compose "${COMPOSE_ARGS[@]}" ps -a \
        --format '{{.Service}}|{{.State}}|{{.ExitCode}}|{{.Status}}' 2>/dev/null || true)
    while IFS='|' read -r svc state exitcode status; do
        case "$svc" in cauterule-*) ;; *) continue ;; esac
        case "$state" in
            running|healthy|paused)
                echo "  [ok]   $svc: $state ($status)" ;;
            exited)
                if [[ "$exitcode" == "0" ]]; then
                    echo "  [done] $svc: exited 0 ($status)"
                else
                    echo "  [FAIL] $svc: exited ${exitcode} ($status)"
                    echo "  --- logs: $svc ---"
                    docker compose "${COMPOSE_ARGS[@]}" logs --no-color "$svc" 2>&1 | tail -40
                    bad=1
                fi ;;
            *)
                echo "  [FAIL] $svc: $state ($status)"
                echo "  --- logs: $svc ---"
                docker compose "${COMPOSE_ARGS[@]}" logs --no-color "$svc" 2>&1 | tail -40
                bad=1 ;;
        esac
    done <<< "$lines"
    # The MCP HTTP daemon must be running.
    if ! docker compose "${COMPOSE_ARGS[@]}" ps --status running --format '{{.Service}}' | grep -q '^cauterule-mcp-http$'; then
        echo "  [FAIL] cauterule-mcp-http is not running"
        echo "  --- logs: cauterule-mcp-http ---"
        docker compose "${COMPOSE_ARGS[@]}" logs --no-color cauterule-mcp-http 2>&1 | tail -40
        bad=1
    else
        # And it must answer an authenticated MCP initialize request.
        code=$(curl -s -o /dev/null -w '%{http_code}' -X POST \
            "http://127.0.0.1:${MCP_PORT}/mcp" \
            -H 'Content-Type: application/json' \
            -H 'Accept: application/json, text/event-stream' \
            -H "Authorization: Bearer ${CAUTERULE_MCP_TOKEN}" \
            -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}' \
            2>/dev/null || true)
        if [[ -z "$code" || "$code" == "000" ]]; then
            echo "  [FAIL] MCP HTTP endpoint not answering (http_code=${code:-none})"
            docker compose "${COMPOSE_ARGS[@]}" logs --no-color cauterule-mcp-http 2>&1 | tail -40
            bad=1
        else
            echo "  [ok]   MCP HTTP endpoint answered (http_code=${code})"
        fi
    fi
    # Tear down so the test suite drives its own containers.
    docker compose "${COMPOSE_ARGS[@]}" down 2>&1 | tail -2
    if [[ "$bad" -ne 0 ]]; then
        echo "FATAL: one or more services did not come up (logs above). NOT running tests."
        exit 1
    fi
    echo "--- [$(date +%H:%M:%S)] setup OK: all runtime services came up"
}

if [[ "$MODE" == "v031" ]]; then
    verify_services
fi

if $SETUP_ONLY; then
    echo "=== --setup-only: services verified, stopping before tests ==="
    exit 0
fi

# ── v0.3.1: automated pytest suite ─────────────────────────────────────────
if [[ "$MODE" == "v031" ]]; then
    # Verbose so the log shows each test as it starts/finishes; -rA prints a
    # per-test PASS/FAIL/SKIP summary at the end; --tb=short keeps failures
    # readable. python -u keeps the tee stream live.
    PYTEST_FLAGS=(
        -m docker
        -v
        --tb=short
        -rA
        --junit-xml="${RESULTS_DIR}/docker-junit.xml"
    )
    # The field conftest records per-test outcomes + the markdown report.
    # Run ALL docker-marked tests (inherited v0.1.0/v0.2.0/v0.3.0 + new v0.3.1).
    echo "--- [$(date +%H:%M:%S)] running v0.3.1 docker suite -> ${RESULTS_DIR}/"
    echo "    live per-test status: ${RESULTS_DIR}/docker-results.jsonl"
    echo "    full log:             ${RESULTS_DIR}/docker-test.log"
    set +e
    CAUTERULE_FT_RESULTS_DIR="$RESULTS_DIR" .venv/bin/python -u -m pytest \
        tests/field/ tests/mcp/ \
        "${PYTEST_FLAGS[@]}" \
        -p no:cacheprovider \
        2>&1 | tee "${RESULTS_DIR}/docker-test.log"
    STATUS=${PIPESTATUS[0]}
    set -e
    echo ""
    echo "--- progress log (${RESULTS_DIR}/docker-progress.log) ---"
    cat "${RESULTS_DIR}/docker-progress.log" 2>/dev/null || true
    echo "================================="
    echo "  v0.3.1 docker suite exit: ${STATUS}"
    echo "  [$(date +%H:%M:%S)] results: ${RESULTS_DIR}/docker-results.jsonl"
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
