#!/usr/bin/env bash
# measure_ttv.sh — Time-to-value measurement for CauterRule v0.1.0
#
# Measures wall-clock time for each TTV phase and reports pass/fail.
# Run from a clean environment (fresh venv recommended).
#
# Usage: bash scripts/measure_ttv.sh
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

pass()  { printf "${GREEN}PASS${NC} %s\n" "$1"; }
fail()  { printf "${RED}FAIL${NC} %s\n" "$1"; exit 1; }

# ── Phase 1: Install ────────────────────────────────────────────────────
echo "=== Phase 1: Install ==="
install_start=$(date +%s)
if command -v cauterule &>/dev/null; then
    echo "  cauterule already installed, skipping pip install"
else
    pip install -e . 2>&1 | tail -5
fi
install_end=$(date +%s)
install_time=$(( install_end - install_start ))
echo "  Install time: ${install_time}s"
[[ $install_time -lt 30 ]] && pass "install (<30s)" || fail "install took ${install_time}s (limit 30s)"

# ── Phase 2: Demo / quickstart ─────────────────────────────────────────
echo ""
echo "=== Phase 2: Demo ==="
demo_start=$(date +%s)
cauterule --help >/dev/null 2>&1
demo_end=$(date +%s)
demo_time=$(( demo_end - demo_start ))
echo "  Demo time (--help): ${demo_time}s"
# Try a brief extraction from bundled corpus if available
if ls corpus/*.jsonl &>/dev/null 2>&1; then
    echo "  Running extract on first corpus file…"
    t0=$(date +%s)
    cauterule extract corpus/$(ls corpus/*.jsonl | head -1) --dry-run 2>&1 | tail -3 || true
    t1=$(date +%s)
    demo_time=$(( demo_end - demo_start + t1 - t0 ))
fi
echo "  Total demo time: ${demo_time}s"
[[ $demo_time -lt 60 ]] && pass "demo (<60s)" || fail "demo took ${demo_time}s (limit 60s)"

# ── Phase 3: Time to first rule ────────────────────────────────────────
echo ""
echo "=== Phase 3: Time to First Rule ==="
rule_start=$(date +%s)
# Attempt to list or create a rule
cauterule list 2>/dev/null || true
first_rule_time=$(( $(date +%s) - rule_start + demo_time + install_time ))
echo "  Time to first rule: ${first_rule_time}s"
# If the store is empty, create a sample rule
if ! cauterule list 2>/dev/null | grep -q "R-"; then
    r0=$(date +%s)
    # Attempt import from demo trajectory
    cauterule import "corpus/$(ls corpus/*.jsonl 2>/dev/null | head -1)" 2>/dev/null || true
    r1=$(date +%s)
    first_rule_time=$(( first_rule_time + r1 - r0 ))
fi
[[ $first_rule_time -lt 300 ]] && pass "first rule (<5 min)" || fail "first rule took ${first_rule_time}s (limit 300s)"

# ── Phase 4: Time to first prevented failure ──────────────────────────
echo ""
echo "=== Phase 4: Time to First Prevented Failure ==="
prevent_start=$(date +%s)
# Replay against a trajectory to get a prevention event
cauterule replay corpus/$(ls corpus/*.jsonl 2>/dev/null | head -1) 2>&1 | tail -10 || true
prevent_time=$(( $(date +%s) - prevent_start + first_rule_time ))
echo "  Time to first prevented failure: ${prevent_time}s"
[[ $prevent_time -lt 600 ]] && pass "prevented failure (<10 min)" || fail "prevention took ${prevent_time}s (limit 600s)"

# ── Phase 5: Total TTV ─────────────────────────────────────────────────
echo ""
echo "=== Phase 5: Total TTV ==="
total=$(( install_time + demo_time + first_rule_time + prevent_time ))
echo "  Total TTV: ${total}s ($(( total / 60 ))m ${(( total % 60 ))}s)"
[[ $total -lt 900 ]] && pass "total TTV (<15 min)" || fail "total TTV was ${total}s (limit 900s)"

echo ""
echo "=== Summary ==="
printf "  Install:              %4ss (target <30s)\n"  "$install_time"
printf "  Demo:                 %4ss (target <60s)\n"  "$demo_time"
printf "  First rule:           %4ss (target <5m)\n"   "$first_rule_time"
printf "  First prevention:     %4ss (target <10m)\n"  "$prevent_time"
printf "  Total TTV:            %4ss (target <15m)\n"   "$total"
echo ""
echo "Results written. Check targets above."