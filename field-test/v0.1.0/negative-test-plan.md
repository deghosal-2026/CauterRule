# Negative Test Plan — CauterRule v0.1.0

**Purpose:** Verify that CauterRule correctly rejects trajectories that describe successful outcomes, opinions, cosmetic complaints, informational messages, normal logs, non-blocking warnings, intermittent self-resolving issues, operator mistakes, feature requests, or flaky tests that pass on retry.

These trajectories should produce **zero rules** in the rule store.

---

## Test Cases

| ID | Scenario | Reason No Rule Should Be Produced |
|----|----------|----------------------------------|
| N-001 | Successful `git push` with clean output | No failure occurred; `success: true` throughout. |
| N-002 | User expresses opinion ("I prefer tabs") | Opinion is subjective preference, not a reproducible failure. |
| N-003 | User calls output "ugly" (cosmetic) | Complaint lacks actionable, repeatable error conditions. |
| N-004 | User reports "Running on macOS" | Pure environment informational, no failure symptom. |
| N-005 | Agent logs "Task completed" | Normal successful completion; no failure signal. |
| N-006 | `npm install` emits deprecation warnings | Warnings did not cause failure or block the task. |
| N-007 | DNS resolution fails then self-resolves on retry | Intermittent transient issue; no systematic cause. |
| N-008 | User deletes wrong branch, then correct branch | Operator error that the user immediately fixed. |
| N-009 | User says "It would be nice if we had X" | Feature request with no current failure to prevent. |
| N-010 | Flaky integration test fails then passes with `--reruns` | Test flakiness resolved by retry; no persistent failure. |

---

## Invariant

For all negative test cases, the extraction pipeline MUST NOT emit any rule. If any rule is produced, the test fails.

---

## File Locations

All trajectories are at `field-test/v0.1.0/corpus/curated/failures/negative/`.

| # | File |
|---|------|
| 1 | `N-001-success-git-push.jsonl` |
| 2 | `N-002-opinion.jsonl` |
| 3 | `N-003-cosmetic.jsonl` |
| 4 | `N-004-env-info.jsonl` |
| 5 | `N-005-normal-log.jsonl` |
| 6 | `N-006-warning-only.jsonl` |
| 7 | `N-007-intermittent.jsonl` |
| 8 | `N-008-operator-error.jsonl` |
| 9 | `N-009-feature-request.jsonl` |
| 10 | `N-010-flaky-pass.jsonl` |

---

**Count:** 10 negative trajectories
**Expected rule count:** 0