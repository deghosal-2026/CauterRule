# Promotion Gate Design

## Purpose

Decide whether a candidate rule is safe to promote based on replay evidence.

## Interface

```
Input:  EvidenceReport + config (auto/human mode)
Output: PromotionDecision { verdict, evidence_summary, approver }
```

## Modes

### Auto-Promote
- Verdict = "pass" → promoted automatically
- Verdict = "fail" → archived with reasoning
- Verdict = "inconclusive" → held for human review

### Human-Review (Default for Production)
- All verdicts generate an evidence summary
- Human must approve or reject via CLI/UI
- Auto-promote threshold can be configured (confidence ≥ X, failures_prevented ≥ Y)

## Evidence Report Format

```
Rule: R-018
Source: trajectory T-003 (git push non-fast-forward)
When: tool call to git push fails with 'non-fast-forward' error
Do: Run git pull --rebase before git push

Replay Results:
  ✓ Would have prevented: F-001, F-007 (2 failures)
  ✗ Would have broken: (none)
  
  Precision: 100% (broke 0 successes)
  Recall: 28% (prevented 2 of 7 similar failures)
  
Verdict: PASS

Proposed by: gpt-4o | Confidence: 0.85
```

## Evidence Thresholds

| Setting | Auto-Promote When |
|---------|-------------------|
| `conservative` | precision=100%, recall≥1, history≥5 |
| `balanced` (default) | precision=100%, recall≥1, history≥3 |
| `aggressive` | precision=100%, recall≥0, history≥1 |