# Historical Replay Engine Design

## Purpose

Test a candidate rule against all historical trajectories to determine:
1. Would it have prevented past failures?
2. Would it have broken past successes?

## Interface

```
Input:  CandidateRule + historical trajectories (failures + successes)
Output: EvidenceReport {
    failures_prevented: string[],
    successes_broken: string[],
    failures_missed: string[],
    precision: float,
    recall: float,
    verdict: "pass" | "fail" | "inconclusive"
}
```

## Algorithm

1. **Load** all historical trajectories from the scenarios directory
2. **Match** the candidate rule's `when` clause against each trajectory's conditions
3. **Simulate** whether applying the rule would have changed the outcome:
   - For failures: Would applying the `do` directive have prevented the failure?
   - For successes: Would applying the `do` directive have caused a failure?
4. **Score**: 
   - Precision = successes_broken == 0 (must not break anything)
   - Recall = failures_prevented >= 1 (must help on at least one)
   - Verdict = pass if precision AND recall

## Evidence Criteria

| Condition | Verdict |
|-----------|---------|
| Helps ≥1 failure, breaks 0 successes | Pass |
| Helps ≥1 failure, breaks ≥1 success | Fail |
| Helps 0 failures, breaks 0 successes | Inconclusive (insufficient data) |
| Helps 0 failures, breaks ≥1 success | Fail |

## Edge Cases

### Insufficient History
If there are <3 historical trajectories, the replay returns "inconclusive" rather than "pass" — the evidence base is too thin.

### Partial Match
If the rule's `when` clause partially matches a trajectory, it's logged as a "near miss" but not counted as prevented or broken.

### Conflicting Rules
If a candidate contradicts an existing promoted rule, the replay engine flags it. The existing rule's evidence is compared against the candidate's evidence to determine which is more specific.