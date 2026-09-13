# v0.3.1 — Work Breakdown Structure

**Goal:** Accuracy & Trust — fix the correctness defects found by the v0.3.0 code review, measure the fixes directly and re-verify with a full field test, then release and launch the patch.

**Milestones:** M1-M3 (GitHub milestones 66-68) — M1 ✓ closed (Critical Code Fixes, 10 issues) · M2 (Evaluation & Field Test, 60) · M3 (Release Readiness & Launch, 16).

**Branch:** `feat-v0.3.1`.

---

## Release Tagline

**From shipped to trustworthy.** v0.3.0 proved the loop end-to-end. v0.3.1 makes the *verdict* trustworthy — the matcher can carry a paraphrase, the scorer stops punishing net-positive rules, extraction quality is measured directly, the adversarial gate exists in production, and every field-test number is reproducible from a committed artifact.

---

## Parts

| Part | Title | Milestone | Tasks |
|------|-------|-----------|-------|
| [1](wbs-v0.3.1-part1-fixes.md) | Phase 1 — Critical Code Fixes | M1 ([#66](https://github.com/deghosal-2026/CauterRule/milestone/66)) ✓ closed | 10 |
| [2](wbs-v0.3.1-part2-field-test.md) | Phase 2 — Evaluation & Field Test | M2 ([#67](https://github.com/deghosal-2026/CauterRule/milestone/67)) | 60 |
| [3](wbs-v0.3.1-part3-release.md) | Phase 3 — Release Readiness & Launch | M3 ([#68](https://github.com/deghosal-2026/CauterRule/milestone/68)) | 16 |
| **Total** | | **M1-M3** | **86** |

---

## Milestone Map

```
M1 (Critical Code Fixes) ✓ closed
              │
              ▼
M2 (Evaluation & Field Test)   ──  60 issues
              │
              ▼
M3 (Release Readiness & Launch) ──  16 issues
```

---

## Dependencies

```
M1 (code correctness) ──> M2 (measure on correct code, then re-verify)
M2 (results + report) ──> M3 (release notes, docs, launch)
```

**Internal dependencies within M2:**
- Evaluation implementation (#726 references, #730 metric) precedes the field-test wiring/run.
- Plan (#733) → runner (#734) → corpus (#735) → calibration (#736) → sweep (#737) → Docker/multi-env (#738, #739) → measurements (#740-#742) → report (#743) → known issues (#744) → exit gate (#745).
- **Code review fixes (#762, #763-#804) precede the final measurement run.** Several defects corrupt the measurement itself (cost `$0.00` #802, ungated promotion #775, unwired injection gate #776), so fixing the 11 Criticals before the sweep keeps the M2 numbers honest. Importants may be fixed or explicitly deferred.

**Internal dependencies within M3:**
- bump (#746) → validation (#747) → security (#748) → packaging (#749-#751) → docs (#752-#756) → pre-release gate (#757) → tag (#758) → launch (#759) → post-release (#760) → merge (#761).

> **Note:** the original "M2 — Evaluation & Measurement" tickets (#726, #728, #729, #730) were kept per request and now live in M2 alongside the field-test work. They overlap the field-test tickets (#726↔#735, #730↔#734, #729↔#740-#742, #728↔#743) and should be reconciled/closes as their counterparts land.

---

## Standard Milestone Exit Gate

Every milestone (M1-M3) must pass its exit gate before the next milestone begins:

- [ ] **All tests pass:** `pytest` — all pass (deterministic subset; field/scale/docker excluded)
- [ ] **Lint strict clean:** `ruff check .` — zero errors
- [ ] **Types strict clean:** `mypy src/ tests/` (strict) — zero errors
- [ ] **Test coverage > 92%** (deterministic subset):
      `pytest --cov=src/cauterule --cov-report=term-missing --ignore=tests/field --ignore=tests/scale -k "not docker"`
- [ ] **All necessary and affected docs are updated**
- [ ] **Code is committed and pushed** to `feat-v0.3.1`
- [ ] **WBS updated:** `docs/wbs/v0.3.1/` reflects the milestone state
- [ ] **All issues in the milestone are closed**

---

## Final Release Gate (v0.3.1)

Before tagging v0.3.1, ALL of the following must be true:

- [ ] M1-M3 complete and exit gates passed
- [ ] M2 field test report published; every headline number reproducible from a committed artifact (#728, #743)
- [ ] Release thresholds met or explicitly documented with CIs (golden ≥70%, failures/positive ≥50%, nearmiss precision ≥90%, adversarial 0 promoted, generic <10%, inconclusive <15%)
- [ ] Cross-session repeat-failure reduction measured (#729, #741)
- [ ] Human-vs-replay agreement measured (#729, #742)
- [ ] Cost table published ($/1k per model) (#729, #740)
- [ ] Security scan clean; adversarial source-trust gate enforced in production (#727, #748)
- [ ] Coverage >92%, `ruff` + `mypy` strict clean
- [ ] PyPI + Docker (GHCR) + Homebrew 0.3.1 published (#749-#751)
- [ ] Tag `v0.3.1`, GitHub release published, milestones closed (#758)
- [ ] Launch announcement published (#759)

---

## Current status

`feat-v0.3.1` @ `be960c2`. **M1 closed** (`2b94b19` + `ccae982`). M2 and M3 open.

- **M1 (Critical Code Fixes): ✅ closed.** 9/10 code issues done; #681 coverage reached 88.5% (gate >92%), remainder folded into M3 (#747).
- **M2 (Evaluation & Field Test): open** — **60 issues**: 4 original evaluation tickets + 13 field-test tickets + **43 from the `[0.3.1-M2-CodeReview]` audit** (#762, #763-#804). 11 Critical (10 code-review + #762), 32 Important. **5/11 Criticals fixed** (#763, #764, #769, #770, #775).
- **M3 (Release Readiness & Launch): open** — 16 issues.

> **Code review (2026-09-12).** A full-repo audit (code, tests, field-test infrastructure) at `be960c2` logged 42 defects + #762. See [Part 2 → Code review findings](wbs-v0.3.1-part2-field-test.md#code-review-findings-43-issues). Note: 3 audit areas (store/corpus/capture/observe, full test-suite pass, field-test runner/report integrity) were not completed and remain candidates for a follow-up review.
