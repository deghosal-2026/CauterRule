# Human-vs-Replay Agreement — CauterRule v0.3.0

**Issue:** #493 · **Plan:** §5.5/§15.9 · **Runner:** `scripts/human_agreement.py`
**Human gate:** agreement <0.8 requires human approval · **Status:** 🟡 Sample generated; reviewer scoring pending.

---

## 1. Method (§5.5)

After each sweep, sample up to N candidates per replay-verdict bucket
(`pass` / `fail` / `inconclusive`). A reviewer independently scores each on
trigger specificity, directive actionability, safety, and replay agreement.

```
replay_vs_human_agreement = matches / total_reviewed
```

If agreement < `HUMAN_GATE_THRESHOLD` (0.80), the promotion gate requires human
approval.

## 2. Run

```bash
# 1. Generate the review sample
python scripts/run-field-test.py --human-review --output-dir field-test/results/0.3.0
#    -> field-test/results/0.3.0/human-agreement-reviews.jsonl

# 2. After a reviewer fills human_verdict/reviewer, score it
python scripts/human_agreement.py --reviews field-test/results/0.3.0/human-agreement-reviews.jsonl
```

## 3. Agreement result (pending)

| Bucket | Sampled | Matches | Agreement |
|--------|---------|---------|-----------|
| pass | _pending_ | | |
| fail | _pending_ | | |
| inconclusive | _pending_ | | |
| **Total** | _pending_ | _pending_ | **_pending_** |

**Decision:** _pending_ — replay-only gate if agreement ≥0.80, else human gate.

**Status:** sampler + scorer are implemented and unit-tested
(`tests/measurement/test_human_agreement.py`); scoring awaits the reviewer-filled
sample from the v0.3.0 re-run.
