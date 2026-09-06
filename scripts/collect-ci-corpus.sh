#!/usr/bin/env bash
# collect-ci-corpus.sh — Download CI failure logs from GitHub Actions and convert to trajectory JSONL
set -euo pipefail

REPO="deghosal-2026/CauterRule"
LIMIT=15
OUTDIR="field-test/v0.1.0/corpus/raw/ci"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --limit) LIMIT="$2"; shift 2 ;;
        --repo) REPO="$2"; shift 2 ;;
        *) echo "Usage: $0 [--limit N] [--repo user/repo]"; exit 1 ;;
    esac
done

mkdir -p "$OUTDIR"
echo "=== Collecting CI corpus from $REPO ==="
echo "Limit: $LIMIT runs, Output: $OUTDIR"

FAILED_RUNS=$(gh run list --repo "$REPO" --workflow CI --branch main --limit "$LIMIT" --json databaseId,conclusion --jq '.[] | select(.conclusion=="failure") | .databaseId')

COUNT=0
for RUN_ID in $FAILED_RUNS; do
    COUNT=$((COUNT + 1))
    TID=$(printf "ci-fail-%03d" "$COUNT")

    echo "  [$COUNT] Processing run $RUN_ID -> $TID"

    JOBS=$(gh run view "$RUN_ID" --repo "$REPO" --log 2>/dev/null | tail -100 || true)

    FAILURE_CLASS="ci/failure"
    DOMAIN="ci"
    if echo "$JOBS" | grep -qi "ruff\|flake8"; then FAILURE_CLASS="ci/lint"; fi
    if echo "$JOBS" | grep -qi "mypy\|type.*check"; then FAILURE_CLASS="ci/typecheck"; fi
    if echo "$JOBS" | grep -qi "pytest\|test.*fail\|FAILED"; then FAILURE_CLASS="ci/test"; fi
    if echo "$JOBS" | grep -qi "docker\|build.*fail"; then FAILURE_CLASS="ci/build"; DOMAIN="docker"; fi

    ERROR_LINE=$(echo "$JOBS" | grep -i "error:" | head -3 || echo "CI run failed")
    LOG_SNIPPET=$(echo "$JOBS" | tail -30)

    python3 << PYEOF
import json
from datetime import datetime, timezone
traj = {
    "trajectory_id": "$TID",
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "task": "Run CI on $REPO",
    "domain": "$DOMAIN",
    "failure_class": "$FAILURE_CLASS",
    "quality_label": "clear",
    "severity": "medium",
    "success": False,
    "failure_point": """${ERROR_LINE:0:200}""",
    "steps": [{"step_number": 1, "tool": "ci", "input": "CI run $RUN_ID", "output": """${LOG_SNIPPET:0:1000}""", "error": """${ERROR_LINE:0:500}""", "state": None}],
    "tags": ["ci", "$DOMAIN", "$FAILURE_CLASS"],
    "expected_rule": "",
    "human_correction": None,
    "source": "ci",
    "source_repo": "$REPO",
    "redacted": False,
    "notes": "Downloaded from CI run $RUN_ID"
}
with open("$OUTDIR/$TID.jsonl", "w") as f:
    f.write(json.dumps(traj) + "\n")
print(f"      wrote $OUTDIR/$TID.jsonl")
PYEOF
    sleep 0.3
done

echo ""
echo "=== Done: $COUNT CI trajectories collected ==="
ls -la "$OUTDIR"/
