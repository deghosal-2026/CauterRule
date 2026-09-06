#!/usr/bin/env bash
set -euo pipefail

DOCKER_TAG="cauterule:field-test"
IMAGE_BUILT=false
PASS=0
FAIL=0
TOTAL=15

usage() {
    cat <<EOF
Usage: $0 [--stage N] [--skip-build] [--verbose]

Docker field test runner for CauterRule.

Options:
  --stage N        Run only stage N (1-$TOTAL)
  --skip-build     Skip Docker image build (use existing image)
  --verbose        Show detailed output for each stage
  --help           Show this help message

Stages:
   1  build          Build Docker image
   2  unit           Run unit tests
   3  scale          Run scale tests
   4  adversarial    Run adversarial tests
   5  corpus         Run corpus tests
   6  CLI            Run CLI tests
   7  TUI            Run TUI tests
   8  MCP            Run MCP tests
   9  pipeline       Run pipeline demo
  10  demo           Run cauterule demo command
  11  redaction      Run redaction tests
  12  export         Run export tests
  13  git            Run git-related tests
  14  loop           Run loop tests
  15  multi-env      Run multi-environment tests
EOF
    exit 0
}

# Parse arguments
SINGLE_STAGE=""
SKIP_BUILD=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help) usage ;;
        --stage) SINGLE_STAGE="$2"; shift 2 ;;
        --skip-build) SKIP_BUILD=true; shift ;;
        --verbose) VERBOSE=true; shift ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

run_stage() {
    local num="$1" name="$2" cmd="$3"
    local label="[$num/$TOTAL] $name"

    if [[ -n "$SINGLE_STAGE" && "$SINGLE_STAGE" != "$num" ]]; then
        return 0
    fi

    if $VERBOSE; then
        echo "=== $label ==="
        echo "Command: $cmd"
        if eval "$cmd"; then
            echo "=== PASS: $label ==="
            PASS=$((PASS + 1))
        else
            echo "=== FAIL: $label ==="
            FAIL=$((FAIL + 1))
        fi
    else
        echo "--- $label"
        if eval "$cmd" > /dev/null 2>&1; then
            echo "  PASS"
            PASS=$((PASS + 1))
        else
            echo "  FAIL"
            FAIL=$((FAIL + 1))
        fi
    fi
}

# Stage 1: Build
if ! $SKIP_BUILD; then
    run_stage 1 "build" "docker build -t $DOCKER_TAG ."
    IMAGE_BUILT=true
else
    if [[ -z "$SINGLE_STAGE" || "$SINGLE_STAGE" == "1" ]]; then
        echo "--- [1/$TOTAL] build (SKIPPED --skip-build)"
    fi
    IMAGE_BUILT=true
fi

DOCKER_RUN="docker run --rm $DOCKER_TAG"
DOCKER_RUN_SH="docker run --rm $DOCKER_TAG sh -c"

# Stage 2: Unit tests
run_stage 2 "unit" "$DOCKER_RUN_SH 'pytest tests/ -m \"not slow and not docker\" --tb=short -q'"

# Stage 3: Scale tests
run_stage 3 "scale" "$DOCKER_RUN_SH 'pytest tests/scale/ -m \"not docker\" --tb=short -q'"

# Stage 4: Adversarial tests
run_stage 4 "adversarial" "$DOCKER_RUN_SH 'pytest tests/adversarial/ -m \"not docker\" --tb=short -q'"

# Stage 5: Corpus tests
run_stage 5 "corpus" "$DOCKER_RUN_SH 'pytest tests/corpus/ -m \"not docker\" --tb=short -q'"

# Stage 6: CLI tests
run_stage 6 "CLI" "$DOCKER_RUN_SH 'pytest tests/cli/ -m \"not docker\" --tb=short -q'"

# Stage 7: TUI tests
run_stage 7 "TUI" "$DOCKER_RUN_SH 'pytest tests/tui/ -m \"not docker\" --tb=short -q'"

# Stage 8: MCP tests
run_stage 8 "MCP" "docker run --rm --entrypoint python $DOCKER_TAG -c 'from cauterule.mcp.server import CauterRuleMCPServer; print(\"MCP import OK\")'"

# Stage 9: Pipeline (demo pipeline)
run_stage 9 "pipeline" "$DOCKER_RUN demo --failures 1"

# Stage 10: Demo command
run_stage 10 "demo" "$DOCKER_RUN demo --failures 1"

# Stage 11: Redaction tests
run_stage 11 "redaction" "$DOCKER_RUN_SH 'pytest tests/redaction/ -m \"not docker\" --tb=short -q'"

# Stage 12: Export tests
run_stage 12 "export" "$DOCKER_RUN_SH 'pytest tests/export/ -m \"not docker\" --tb=short -q'"

# Stage 13: Git (extraction tests)
run_stage 13 "git" "$DOCKER_RUN_SH 'pytest tests/extraction/ -m \"not docker\" --tb=short -q'"

# Stage 14: Loop tests
run_stage 14 "loop" "$DOCKER_RUN_SH 'pytest tests/loop/ -m \"not docker\" --tb=short -q'"

# Stage 15: Multi-env field tests
run_stage 15 "multi-env" "$DOCKER_RUN_SH 'pytest tests/field/ -m docker --tb=short -q'"

# Summary
echo ""
echo "================================="
echo "  Results: $PASS passed, $FAIL failed, $TOTAL total"
echo "================================="

if [[ "$FAIL" -eq 0 ]]; then
    exit 0
else
    exit 1
fi