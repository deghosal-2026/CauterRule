# Promotion Gate Design

## Purpose

Decide whether a candidate rule is safe to promote based on replay evidence, linter validation, and conflict status.

## Interface

```
Input:  EvidenceReport + LinterResult + ConflictReport + config (mode/thresholds)
Output: PromotionDecision { verdict, evidence_summary, approver, linter_warnings, conflicts }
```

## Modes

### Auto-Promote
- Verdict = "pass" + linter clean + no conflicts → promoted automatically
- Verdict = "fail" → archived with reasoning
- Verdict = "inconclusive" → held for human review
- Linter warnings → blocked regardless of replay verdict

### Human-Review (Default for Production)
- All verdicts generate an evidence summary
- Human must approve or reject via CLI/TUI
- Auto-promote threshold can be configured (confidence >= X, failures_prevented >= Y)

### Hybrid (Default)
- High-confidence candidates (>=0.8) with clean replay + linter + no conflicts → auto-promoted
- Low-confidence or borderline candidates → held for human review
- Threshold is configurable and calibrates over time based on historical accuracy

## Evidence Report Format

```
Rule: R-018 (Draft Tournament Winner, Pass 2/3)
Source: trajectory T-003 (git push non-fast-forward)
When: tool call to git push fails with 'non-fast-forward' error
Do: Run git pull --rebase before git push

Replay Results:
  ✓ Would have prevented: F-001, F-007 (2 failures)
  ✗ Would have broken: (none)
  ~ Near misses: F-003, F-012 (partial match, not counted)

  Precision: 100% (broke 0 successes)
  Recall: 28% (prevented 2 of 7 similar failures)

Linter: ✓ No issues (not vague, not duplicate, not contradictory, testable)
Conflicts: ✓ No conflicts detected

Verdict: PASS

Proposed by: gpt-4o | Confidence: 0.85 (calibrated: 0.82)
Mode: hybrid → auto-promoted (confidence >= 0.8, clean replay + linter)
```

## Evidence Thresholds

| Setting | Auto-Promote When |
|---------|-------------------|
| `conservative` | precision=100%, recall>=1, history>=5, confidence>=0.85 |
| `balanced` (default) | precision=100%, recall>=1, history>=3, confidence>=0.7 |
| `aggressive` | precision=100%, recall>=0, history>=1, confidence>=0.5 |

## Linter Integration

The rule linter runs before the promotion gate makes a decision:
- **Vague** → blocked, sent back for re-extraction or human review
- **Tautological** → blocked
- **Duplicate** → blocked, existing rule referenced
- **Contradictory** → blocked, conflict report generated
- **Untestable** → blocked
- **Unsafe directive** → blocked, logged as security event

## Conflict Integration

The conflict detector runs before the promotion gate:
- **Direct contradiction** → blocked for human review
- **Specificity overlap** → auto-resolved by precedence if non-contradictory, or held for review
- **No conflicts** → proceed to promotion

## Batch Promotion

`cauterule review` TUI supports batch promotion:
- Review 10 candidates in one session
- Evidence cards show precision, recall, linter status, conflicts
- Approve/reject with annotations
- All approvals are committed in a single git commit