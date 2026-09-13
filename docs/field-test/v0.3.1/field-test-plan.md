# Field Test Plan — CauterRule v0.3.1

> **v0.3.1 is a fix-and-re-verify patch.** This plan re-validates the M1 code fixes and the M2 code-review fixes against the **v0.3.0 baseline**: freeze the corpus, re-run the same sweep, and report per-corpus deltas with confidence intervals. It is a regression release, not a feature release — every number must be reproducible from committed artifacts.

**Issues:** #733 (this plan) · #734 (runner wiring) · #735 (corpus) · #736 (calibration) · #737 (sweep) · #740 (cost) · #741 (cross-session) · #742 (human agreement) · #743 (report) · #745 (exit gate)
**Milestone:** M2 ([v0.3.1-M2: Field Test](https://github.com/deghosal-2026/CauterRule/milestone/67))
**Sweep command:** `.venv312` (Python 3.12) + `CAUTERULE_SEMANTIC_MATCHING=1`, OpenRouter `--max-workers 6`
**Artifacts:** `field-test/results/0.3.1/` (`meta.json`, `results.jsonl`, `summary.json`, `harness_health.json` per run)
**Baseline:** `field-test/results/0.3.0/` and `docs/field-test/v0.3.0/FIELD_TEST_REPORT.md`

---

## 1. Objective

Prove that the v0.3.1 fixes moved the release metrics — and did not regress anything — by re-running the identical 2-model × 40-corpus sweep on corrected code and comparing to v0.3.0.

The three questions this field test answers:

1. **Did the replay/scorer fixes move the pass rate?** (#721–#724, #731, #732) — golden and `failures/positive` pass rates should rise; `inconclusive` should fall.
2. **Is extraction actually good, independent of replay?** (#730) — `extraction_f1` / `extraction_agreement` on `failures/positive` and `reference-expansion` should be high while token-F1 stays lower, showing the gap was the text-similarity proxy, not the model.
3. **Are the two worst corpora fixed?** (#726, #735) — `adapters` and `raw/ci` must produce non-zero `prevented` (they were 0/60 and 0/110 by retrieval miss, not by bad rules).

## 2. Methodology — Regression Release

1. **Freeze the corpus.** No target/reference edits after calibration except the corpus work in #735; record the corpus hash in `meta.json`.
2. **Re-run the full sweep** with the same models, corpora, thresholds, and flags as v0.3.0. Same runner, same `--max-workers`.
3. **Compare to baseline** per corpus: pass rate, precision/recall, `inconclusive_breakdown`, `verdict_reason_breakdown`, `extraction_f1`/`extraction_agreement`, adversarial promotions.
4. **Statistical rigor.**
   - Wilson 95% CIs on every rate (`cauterule.stats.rate_with_ci`).
   - **Paired per-trajectory model deltas** (same trajectory, model A vs model B) — not independent-sample comparisons.
   - Golden expanded to **n≥60** so the headline rate is powered (#735); report CIs, never a bare point estimate on n=10.
5. **Reproducibility.** The report is generated from committed artifacts; a drift check fails if the markdown and `field-test/results/0.3.1/` disagree beyond rounding (#728, #743).

## 3. Models

| Model | Provider (OpenRouter) | Tier |
|-------|-----------------------|------|
| `gpt-4o-mini` | `openai/gpt-4o-mini` | cloud, strong |
| `llama-3.1-8b-instruct` | `openai/meta-llama/llama-3.1-8b-instruct` | cloud, weak |

Local OMLX is dropped (#713). Semantic matching is enabled in the sweep environment; the shipped image and hermetic tests deliberately run lexical-only.

## 4. Corpora

40 corpora per model (the v0.3.0 set), including:

| Corpus | What it gates | v0.3.1 change |
|--------|---------------|---------------|
| `golden` | Overall correctness | **expanded to n≥60**, `expected_rule` backfilled (#735) |
| `failures/positive` | Extraction → promotion | replay/scorer fixes (#721–#724) |
| `failures/negative` | Precision | unchanged |
| `successes` | Safety (0 false positives) | unchanged |
| `nearmiss` | Near-miss precision ≥90% | recovery + domain-gate fixes (#723) |
| `adversarial/*` | 0 promotions | source-trust gate now enforced (#727/#776) |
| `adapters` | Framework coverage | **adapter references with matching domains (#726)** |
| `raw/ci` | Real CI failures | **CI references routed into the slice (#726)** |
| `reference-expansion` (+ paraphrase-diversity) | Extraction accuracy | `expected_rule` used as ground truth (#730) |

Full per-corpus inventory and allocation: see `docs/field-test/v0.3.0/field-test-plan.md` §14 (unchanged for v0.3.1 except the rows above).

## 5. What Changed Since v0.3.0 — Issue → Metric Map

| Issue(s) | Fix | Metric it should move |
|----------|-----|-----------------------|
| #721, #722 | Semantic floor + failure-signature haystack | `avg_match_score`, `blocked_by_near_miss` count |
| #723 | Domain-gated `broken` + match margin | `successes_broken` (down), nearmiss precision |
| #724 | Scorer ordering + near-miss band | `passing`, `blocked_by_broken` |
| #725 | Structured `error_signature` | signature-hit grounded matches |
| #727, #776 | Source-trust gate in production | adversarial promotions (must stay 0) |
| #731, #732 | Recall-weighted ranking + 2-pass dedup | `avg_recall`, duplicate candidates |
| #730 | Extraction-accuracy metric | **new** `extraction_f1`, `extraction_agreement` |
| #726, #735 | Adapter/CI references + golden backfill | `adapters`/`raw/ci` `prevented` > 0; golden n≥60 |
| #736 | Re-calibrated thresholds | `precision`/`recall` at shipped thresholds |
| #728 | Artifact-derived report + drift check | artifact-vs-report agreement |
| #762–#804 | 43 code-review fixes | replay verdicts, promotion gates, cost tokens, injection detection |

## 6. Thresholds / Exit Criteria

| Corpus | Metric | Threshold |
|--------|--------|-----------|
| golden | pass rate | **≥ 70%** (n≥60) |
| failures/positive | pass rate | **≥ 50%** |
| nearmiss | precision | **≥ 90%** |
| adversarial/* | promoted | **0** |
| generic triggers | share | **< 10%** |
| all | inconclusive | **< 15%** |

Every rate is reported with a Wilson 95% CI and evaluated against the threshold with the CI, not the point estimate alone. Cost / cross-session / human-agreement are measured post-sweep (#740–#742) and must not be `_pending_`.

## 7. Runner and Harness

- `scripts/run-field-test.py` now emits, per corpus `summary.json`:
  - `extraction_f1`, `extraction_agreement`, `extraction` (n, token/semantic/directive F1) — #730/#734
  - `verdict_reason_breakdown` (`blocked_by_broken` / `blocked_by_precision` / `blocked_by_near_miss` / …) — #724
  - existing `inconclusive_breakdown`, `successes_broken` distributions, `confidence_intervals`
- Output root: **`field-test/results/0.3.1/`**.
- Harness health (`harness_health.json`) gates parse rate; a corpus with `no .jsonl records` or a parse-rate drop aborts the sweep.

## 8. Reproducibility (#728/#743)

1. Commit the post-fix run artifacts under `field-test/results/0.3.1/`.
2. Generate `docs/field-test/v0.3.1/FIELD_TEST_REPORT.md` **from those artifacts** (scripted), not by hand.
3. A drift check recomputes the headline tables from the committed artifacts and fails if markdown and artifacts disagree beyond rounding.
4. Every headline table states the run it came from (`field-test/results/0.3.1/<corpus>/<model>/<timestamp>/`).

## 9. Acceptance Criteria

- [ ] Plan committed at `docs/field-test/v0.3.1/field-test-plan.md`
- [ ] Models, corpora, thresholds, and exit criteria explicit
- [ ] Every M1/M2 issue mapped to the metric it should move (§5)
- [ ] Full sweep completes with no lost corpora; results committed under `field-test/results/0.3.1/`
- [ ] golden / failures-positive / nearmiss / adversarial reported with Wilson CIs
- [ ] Delta table vs v0.3.0
- [ ] `extraction_f1` / `extraction_agreement` present in every `summary.json`
- [ ] Report regenerated from artifacts; drift check passes

## 10. Dependencies

M1 complete (fixes under test) ✓ · M2 code-review fixes complete ✓ · this plan (#733) → extraction metric (#730) → corpus (#726/#735) → runner wiring (#734) → calibration (#736) → sweep (#737) → measurements (#740–#742) → report (#743) → known issues (#744) → exit gate (#745).

---

### See also

- [v0.3.0 field test plan](../v0.3.0/field-test-plan.md) (baseline methodology)
- [v0.3.1 Docker plan](docker-test-plan.md) · [v0.3.1 Docker results](docker-test-results.md)
- [v0.3.1 threshold calibration](threshold-calibration.md)
- [WBS Part 2 — Evaluation & Field Test](../../wbs/v0.3.1/wbs-v0.3.1-part2-field-test.md)
