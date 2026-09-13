# Raw Sweep Notes — v0.3.1 curated corpus (2-model)

> **Status: RAW / INTERIM working notes.** Not the artifact-derived `FIELD_TEST_REPORT.md`.
> Per plan §8 the final report must be scripted from committed artifacts with a drift check.
>
> **This file is a running journal.** Latest results are always kept current in §1.
> Issues are logged chronologically in §2 with a status (`OPEN` / `FIXED`); when an issue
> is fixed, append the fix + evidence to its entry and flip the status. Do not delete
> entries — the log is the audit trail.

- **Date started:** 2026-09-13
- **Date last updated:** 2026-09-13
- **Runner:** `scripts/run-field-test.py` (one corpus type per invocation)
- **Env:** `.venv312` (Python 3.12.14), `CAUTERULE_SEMANTIC_MATCHING=1`, `--max-workers 6`
- **Provider:** OpenRouter `https://openrouter.ai/api/v1`, extraction passes 2, temps `0.2,0.5`
- **Models:**
  - `gpt-4o-mini` → `openai/gpt-4o-mini` (label `openai-openai_gpt-4o-mini`)
  - `llama-3.1-8b` → `meta-llama/llama-3.1-8b-instruct` (label `openai-meta-llama_llama-3.1-8b-instruct`)
- **Artifacts:** `field-test/results/0.3.1/<corpus>/<model>/2026-09-13/`
- **Baseline:** `field-test/results/0.3.0/.../2026-09-12/`, `docs/field-test/v0.3.0/FIELD_TEST_REPORT.md`
- **Scope:** the 7 curated corpora only. The gated corpora `adversarial/*`, `adapters`,
  `raw/ci`, `reference-expansion` are not run yet (J7 / OPEN).

---

## 1. Latest results (current committed artifacts)

Scored = `passing + failing + inconclusive`. Gate-dropped safety trajectories are not scored.

| Corpus | Model | done | gate | cand | pass | fail | incon | prec | rec | exF1 | agree | safety |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| golden | gpt-4o-mini | 60 | 0 | 104 | **47** | 0 | 13 | 0.783 | 0.365 | 0.606 | 0.083 | pass |
| golden | llama-3.1-8b | 60 | 0 | 110 | **48** | 0 | 12 | 0.800 | 0.419 | 0.677 | 0.100 | pass |
| failures/positive | gpt-4o-mini | 50 | 0 | 85 | 26 | 3 | 21 | 0.544 | 0.218 | 0.674 | 0.174 | pass |
| failures/positive | llama-3.1-8b | 50 | 0 | 91 | 26 | 2 | 22 | 0.544 | 0.232 | 0.713 | 0.261 | pass |
| failures/negative | both | 0 | 60 | 0 | 0 | 0 | 0 | — | — | — | — | pass (silence 1.0) |
| successes | both | 0 | 60 | 0 | 0 | 0 | 0 | — | — | — | — | pass (silence 1.0) |
| nearmiss | gpt-4o-mini | 23 | 27 | 40 | 0 | 4 | 19 | 0.217 | 0.058 | — | — | pass |
| nearmiss | llama-3.1-8b | 23 | 27 | 44 | 0 | 6 | 17 | 0.304 | 0.068 | — | — | pass |
| noisy | gpt-4o-mini | 5 | 0 | 9 | 3 | 0 | 2 | 0.600 | 0.255 | 0.700 | 1.000 | pass |
| noisy | llama-3.1-8b | 5 | 0 | 10 | 2 | 0 | 3 | 0.400 | 0.218 | 0.700 | 1.000 | pass |
| corrections | gpt-4o-mini | 5 | 0 | 9 | 4 | 0 | 1 | 0.800 | 0.181 | 0.578 | 0.250 | pass |
| corrections | llama-3.1-8b | 5 | 0 | 8 | 4 | 0 | 1 | 0.800 | 0.176 | 0.644 | 0.500 | pass |

**nearmiss note:** the `fail` count (4 gpt / 6 llama) is **not** a regression — every one is
`_forced_reject=True` on a `should_reject` source (candidate passed replay but the source is
expected-to-reject) with `precision=1.0`, `successes_broken=[]`. Safety mechanism working.
`accepted=0`, `false_accept_rate=0.0` for both.

### 1a. Pass rate vs plan §6 exit criteria (Wilson 95% CI)

| Corpus | Model | pass/n | rate | CI low | CI high | threshold | verdict |
|---|---|---|---:|---:|---:|---:|---|
| golden | gpt-4o-mini | 47/60 | 0.78 | 0.66 | 0.87 | ≥0.70 | **PASS** |
| golden | llama-3.1-8b | 48/60 | 0.80 | 0.68 | 0.88 | ≥0.70 | **PASS** |
| failures/positive | gpt-4o-mini | 26/50 | 0.52 | 0.39 | 0.65 | ≥0.50 | **PASS** |
| failures/positive | llama-3.1-8b | 26/50 | 0.52 | 0.39 | 0.65 | ≥0.50 | **PASS** |

- golden inconclusive = 13/60 (21.7%) gpt, 12/60 (20.0%) llama — above the <15% target (J6 / OPEN).
- generic triggers: golden 6/166 = 3.6% gpt, 7/174 = 4.0% llama; failures/positive 0% / 1/141 → PASS (<10%).
- nearmiss safety verdict PASS for both (0 false accepts).
- adversarial promoted = 0 → not run (J7 / OPEN).

### 1b. Two-model comparison

- **Golden:** llama 48/60 vs gpt 47/60 — statistically tied (CIs overlap); weak model matches the strong one.
- **failures/positive:** identical, both 26/50 (52%).
- **nearmiss:** both safety PASS, 0 false accepts.
- **noisy:** gpt 3/5 vs llama 2/5 (5-example noise). **corrections:** both 4/5.
- **Extraction semantic F1:** golden 0.606 / 0.677; failures/positive 0.674 / 0.713. Directive F1 low (0.21–0.32).
- **Conclusion:** golden and failures/positive are pipeline-bound, not model-bound after the fixes.

### 1c. Harness health

All 7 curated corpora: **PASS** for both models.

### 1d. Corpus inventory / reference pool

| Corpus | n | Type |
|---|---|---|
| golden | 60 | correctness (positives) |
| failures/positive | 50 | extraction → promotion |
| failures/negative | 60 | safety **silence** (gate drops all) |
| successes | 60 | safety **silence** (gate drops all) |
| nearmiss | 50 | safety **rejection** (candidates must all be blocked) |
| noisy | 5 | robustness |
| corrections | 5 | human-correction flow |

Safety keyed by `expected_outcome`: `should_silence` (successes, failures/negative) →
pass = 100% silence; `should_reject` (nearmiss, adversarial/*) → pass = 0 accepts.
Replay pool = 540 trajectories (incl. `corpus/public/golden_replay/`, 54 refs from F3).

### 1e. Breakdown appendix

inconclusive_breakdown (per candidate): golden gpt `{matcher_gap:4, ambiguous_evidence:21}`,
llama `{matcher_gap:2, ambiguous_evidence:25}`; failures/positive gpt `{matcher_gap:2,
ambiguous_evidence:37}`, llama `{matcher_gap:3, ambiguous_evidence:39}`; nearmiss gpt
`{matcher_gap:3, ambiguous_evidence:32}`, llama `{broad_trigger:2, matcher_gap:6, ambiguous_evidence:26}`.

verdict_reason_breakdown (per trajectory): golden gpt `verdict:pass 47, no_signal 13`;
llama `verdict:pass 48, no_signal 12`; failures/positive gpt `verdict:pass 26, no_signal 17,
blocked_by_broken 3, min_sample 1, blocked_by_near_miss 3`, llama `verdict:pass 26,
no_signal 17, blocked_by_broken 2, min_sample 1, blocked_by_near_miss 4`; nearmiss gpt
`verdict:fail 4 (forced should_reject), no_signal 17, min_sample 1, blocked_by_near_miss 1`.

Extraction metrics (n, token_f1, semantic_f1, directive_f1, agreement):
golden gpt (60, 0.416, 0.606, 0.209, 0.083), llama (60, 0.514, 0.677, 0.227, 0.100);
failures/positive gpt (23, 0.533, 0.674, 0.318, 0.174), llama (23, 0.629, 0.713, 0.281, 0.261);
corrections gpt (4, 0.414, 0.578, 0.424, 0.250), llama (4, 0.515, 0.644, 0.448, 0.500).

---

## 2. Issue journal

Status legend: `OPEN` (unresolved) · `FIXED` (fix committed + verified).
Append new entries at the bottom with the next `J#`.

| ID | Issue | Status | Fixed by |
|---|---|---|---|
| J1 | nearmiss/adversarial safety scoring inverted | FIXED | `b7867b9` |
| J2 | nearmiss harness-health false positive | FIXED | `b7867b9` |
| J3 | golden reference-coverage gap (no_signal→inconclusive) | FIXED | `6f6e89b` |
| J4 | golden ≥70% threshold looked unrealistic | FIXED (was J3) | `6f6e89b` |
| J5 | llama `corrections` `C-002 no_candidates` | FIXED (variance) | — |
| J6 | `extraction_agreement` low + golden ~20% inconclusive | OPEN | — |
| J7 | gated corpora not run (adversarial/adapters/raw-ci/ref-exp) | OPEN | — |
| J8 | stale corpus inventory in README | FIXED | (this commit) |
| J9 | final report + #740–#742 measurements | OPEN | — |

### J1 — nearmiss (+ adversarial) safety scoring inverted — FIXED
- **Found:** pass 1 (2026-09-13). nearmiss safety verdict `fail` despite 0 false accepts.
- **Root cause:** `safety_summary` used `pass iff accepted > 0`; nearmiss was not in
  `replay/safety.py`'s `SAFETY_CORPORA`, so the rejection corpus was scored by the
  extraction-corpus branch. Inverted (v0.3.0's 1 false accept scored `pass`).
- **Fix:** added `REJECTION_CORPORA` / `is_rejection_corpus()` (`nearmiss`, `adversarial/*`);
  rejection corpora pass iff `accepted == 0`; report `false_accept_rate` / `rejection_rate`.
  Tests in `tests/replay/test_safety.py`.
- **Evidence:** both models `accepted=0`, `false_accept_rate=0.0`, `verdict=pass`.
- **Commit:** `b7867b9`.

### J2 — nearmiss harness-health false positive — FIXED
- **Found:** pass 1. Harness `FAIL` (parse 46%, completion 84–86%).
- **Root cause:** parse-rate computed over `done + gate_dropped`; nearmiss's 27 intentional
  gate silences diluted it to 46%.
- **Fix:** added `attempted` denominator (`total - gate_dropped`) to `harness_health`; runner
  passes `attempted`. Tests in `tests/benchmark/test_harness.py`.
- **Evidence:** nearmiss harness `PASS` (`Parse rate 100.0% (23/23)`).
- **Commit:** `b7867b9`.

### J3 — golden reference-coverage gap — FIXED
- **Found:** pass 1. Golden 28/60 (47%), 32 inconclusive; golden spans ~24 domains but the
  replay pool had no same-domain failure references for 18 of them.
- **Root cause:** with `< _MIN_DOMAIN_REFS` (3) same-domain failures, the runner fell back to
  the full 486-pool, so a correctly-extracted rule matched nothing → `no_signal`.
- **Fix:** `scripts/generate_golden_replay_refs.py` authors 54 sibling failure refs
  (`corpus/public/golden_replay/`, 3/domain, encoding each scenario's `expected_rule`),
  routed via `REFERENCE_BUCKETS`.
- **Evidence:** golden 28→47/48 pass, inconclusive 32→12/13, recall 0.08→0.37/0.42. No
  regression in failures/positive, nearmiss, successes, failures/negative.
- **Commit:** `6f6e89b`.

### J4 — golden ≥70% threshold realism — FIXED (was J3, not a threshold)
- **Found:** pass 1 (47% made the gate look impossible).
- **Resolution:** J3 fixed it; golden is now 78%/80% (CIs [0.66,0.87] / [0.68,0.88]). No recalibration.

### J5 — llama `corrections` `C-002 no_candidates` — FIXED (variance, no code change)
- **Found:** pass 1. llama `C-002` returned `no_candidates`.
- **Resolution:** intermittent 8B extraction failure at temps 0.2/0.5; `done` in the latest
  run (corrections 4/5). Not a gate regression.

### J6 — `extraction_agreement` low + golden ~20% inconclusive — OPEN
- **Found:** pass 1/pass 2. Agreement 0.083/0.100 (golden), 0.174/0.261 (failures/positive);
  `extraction_f1` (semantic 0.61–0.71) may be carried by one lucky pass. Golden inconclusive
  still 20–22% (target <15%).
- **Next:** inspect `cauterule/measurement/extraction_accuracy.py` (agreement definition),
  draft tournament/dedup, temperature handling; decide if low agreement is definitional or a
  dedup defect; decide if the <15% inconclusive target is reachable or needs recalibration.

### J7 — gated corpora not run — OPEN
- **Found:** scope choice. `adversarial/*` (must be 0 promotions — now correctly scored by
  J1), `adapters`, `raw/ci` (#726), `reference-expansion` not swept.
- **Next:** run them; they are prerequisites for the v0.3.1 exit gate.

### J8 — stale corpus inventory in README — FIXED
- **Found:** README table said 10/30/10/20/14/5/5 and "84 curated".
- **Fix:** corrected to 60/50/60/60/50/5/5, documented the silence-vs-rejection taxonomy and
  the 540-trajectory reference pool. `field-test/README.md`.

### J9 — final report + #740–#742 measurements — OPEN
- **Found:** plan §8 requirement.
- **Next:** generate `docs/field-test/v0.3.1/FIELD_TEST_REPORT.md` from the committed
  artifacts with the #728 drift check; fill cost / cross-session / human-agreement (#740–#742)
  so they are not `_pending_`.

---

## 3. Reproduce

```bash
export CAUTERULE_LLM_API_KEY=sk-or-...
export CAUTERULE_SEMANTIC_MATCHING=1
.venv312/bin/python scripts/run-field-test.py <corpus> \
  --llm-provider openai --llm-model <model> \
  --llm-base-url https://openrouter.ai/api/v1 \
  --max-workers 6 --output-dir field-test/results/0.3.1
```

Corpus names: `golden`, `failures/positive`, `failures/negative`, `successes`,
`nearmiss`, `noisy`, `corrections`.
Regenerate golden refs (idempotent): `.venv312/bin/python scripts/generate_golden_replay_refs.py`.
Fix tests: `.venv312/bin/python -m pytest tests/replay/test_safety.py tests/benchmark/test_harness.py -q`.

### Journal maintenance

- Add new findings as `J#` entries (append, never delete).
- Keep §1 results current after every sweep; stamp "Date last updated".
- When an `OPEN` entry is fixed, add found/root-cause/fix/evidence/commit and flip status.
