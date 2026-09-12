# Cross-Session Repeat-Failure Reduction — CauterRule v0.3.0

**Issue:** #663/#496 · **Plan:** §5.2/§7.3 · **Runner:** `scripts/cross_session.py`
**Target:** reduction ≥50% · **Status:** 🟡 Tooling complete; protocol measurement pending re-run.

---

## 1. Protocol (§4.3)

1. **Baseline:** run 5 sessions against the lifecycle corpus **without** CauterRule
   intervention; record the repeat-failure rate.
2. **Intervention:** run the same 5 sessions **with** extraction + promotion;
   the rule store persists between sessions.
3. Compare the late-session window (sessions 4-5) via
   `scripts/cross_session.py`.

The runner's `--cross-session` block consumes
`field-test/results/0.3.0/cross-session-baseline.jsonl` and
`cross-session-intervention.jsonl` (each record: `session`, `failure_class`,
`success`).

## 2. Formula (§7.3)

```
repeat_failure_rate(sessions) = repeat_failures / total_failures
reduction = 1 - (rate_intervention / rate_baseline)
```

A failure is a *repeat* when its `failure_class` was seen earlier in the ordered
session list.

## 3. Run

```bash
python scripts/run-field-test.py --cross-session --output-dir field-test/results/0.3.0
# or directly:
python scripts/cross_session.py \
  --baseline field-test/results/0.3.0/cross-session-baseline.jsonl \
  --intervention field-test/results/0.3.0/cross-session-intervention.jsonl
```

## 4. Measured result (pending)

| Metric | Baseline | Intervention |
|--------|----------|--------------|
| Failures | _pending_ | _pending_ |
| Repeat failures | _pending_ | _pending_ |
| Repeat-failure rate | _pending_ | _pending_ |
| **Reduction** | | **_pending_ (target ≥0.50)** |

**Status:** measurement is fully automated (`src/cauterule/measurement/cross_session.py`,
unit-tested in `tests/measurement/test_cross_session.py`); the numeric result
lands after the v0.3.0 5-session protocol run.
