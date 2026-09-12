# v0.3.1 — Work Breakdown Structure

**Goal:** Accuracy & Trust — fix the correctness defects found by the v0.3.0 code review, close the evaluation/measurement gaps that made the v0.3.0 quality numbers hard to interpret, re-verify the pipeline with a full field test, then release and launch the patch.

**Milestones:** M1-M4 (GitHub milestones 66-69) — M1 (Critical Code Fixes, 10 issues) · M2 (Evaluation & Measurement, 4) · M3 (Field Test, 13) · M4 (Release Readiness & Launch, 16).

**Branch:** `feat-v0.3.1` (branched from `main` @ `76dcf21`).

---

## Release Tagline

**From shipped to trustworthy.** v0.3.0 proved the loop end-to-end. v0.3.1 makes the *verdict* trustworthy — the matcher can carry a paraphrase, the scorer stops punishing net-positive rules, extraction quality is measured directly, the adversarial gate exists in production, and every field-test number is reproducible from a committed artifact.

---

## Parts

| Part | Title | Milestone | Tasks |
|------|-------|-----------|-------|
| [1](wbs-v0.3.1-part1-fixes.md) | Phase 1 — Critical Code Fixes | M1 ([#66](https://github.com/deghosal-2026/CauterRule/milestone/66)) | 10 |
| [2](wbs-v0.3.1-part2-evaluation.md) | Phase 2 — Evaluation & Measurement | M2 ([#67](https://github.com/deghosal-2026/CauterRule/milestone/67)) | 4 |
| [3](wbs-v0.3.1-part3-field-test.md) | Phase 3 — Field Test | M3 ([#68](https://github.com/deghosal-2026/CauterRule/milestone/68)) | 13 |
| [4](wbs-v0.3.1-part4-release.md) | Phase 4 — Release Readiness & Launch | M4 ([#69](https://github.com/deghosal-2026/CauterRule/milestone/69)) | 16 |
| **Total** | | **M1-M4** | **43** |

---

## Milestone Map

```
M1 (Critical Code Fixes)  ──>  M2 (Evaluation & Measurement)
        10 issues                      4 issues
             │                             │
             └──────────────┬──────────────┘
                            ▼
                   M3 (Field Test)
                        13 issues
                            │
                            ▼
              M4 (Release Readiness & Launch)
                        16 issues
```

---

## Dependencies

```
M1 (code correctness) ──> M2 (measurement must run on correct code)
M1 + M2               ──> M3 (field test validates fixes + new metrics)
M3 (results/report)   ──> M4 (release notes, docs, launch)
```

**Internal dependencies:**
- M1: #720 (umbrella) frames #721-#724; matcher fixes (#721, #722) precede scorer fixes (#723, #724); selection fixes (#731, #732) and extraction (#725) are independent; #727 (trust) is independent; #681 (coverage) spans the milestone.
- M2: #730 (extraction metric) and #726 (corpus) precede #729 (measurements); #728 (report reproducibility) consumes all three.
- M3: strictly sequential — plan (#733) → runner (#734) → corpus (#735) → calibration (#736) → sweep (#737) → Docker/multi-env (#738, #739) → measurements (#740-#742) → report (#743) → known issues (#744) → exit gate (#745).
- M4: bump (#746) → validation (#747) → security (#748) → packaging (#749-#751) → docs (#752-#756) → pre-release gate (#757) → tag (#758) → launch (#759) → post-release (#760) → merge (#761).

---

## Standard Milestone Exit Gate

Every milestone (M1-M4) must pass its exit gate before the next milestone begins:

- [ ] **All tests pass:** `pytest` — all pass (deterministic subset; field/scale/docker excluded)
- [ ] **Lint strict clean:** `ruff check .` — zero errors
- [ ] **Types strict clean:** `mypy src/ tests/` (strict) — zero errors
- [ ] **Test coverage > 92%** (deterministic subset):
      `pytest --cov=src/cauterule --cov-report=term-missing --ignore=tests/field --ignore=tests/scale -k "not docker"`
- [ ] **All necessary and affected docs are updated**
- [ ] **Code is committed and pushed** to `feat-v0.3.1`
- [ ] **WBS updated:** `docs/wbs/v0.3.1/` reflects the milestone state (tasks checked, statuses current)
- [ ] **All issues in the milestone are closed**

---

## Final Release Gate (v0.3.1)

Before tagging v0.3.1, ALL of the following must be true:

- [ ] M1-M4 complete and exit gates passed
- [ ] M3 field test report published; every headline number reproducible from a committed artifact (#728, #743)
- [ ] Release thresholds met or explicitly documented with CIs (golden ≥70%, failures/positive ≥50%, nearmiss precision ≥90%, adversarial 0 promoted, generic <10%, inconclusive <15%)
- [ ] Cross-session repeat-failure reduction measured (#729, #741)
- [ ] Human-vs-replay agreement measured (#729, #742)
- [ ] Cost table published ($/1k per model) (#729, #740)
- [ ] Security scan clean; adversarial source-trust gate enforced in production (#727, #748)
- [ ] Coverage >92%, `ruff` + `mypy` strict clean (#681)
- [ ] PyPI + Docker (GHCR) + Homebrew 0.3.1 published (#749-#751)
- [ ] Tag `v0.3.1`, GitHub release published, milestones closed (#758)
- [ ] Launch announcement published (#759)

---

## Current status

`feat-v0.3.1` created from `main` @ `76dcf21`. M1-M4 open, all 43 issues open. No milestone exit gate passed yet.
