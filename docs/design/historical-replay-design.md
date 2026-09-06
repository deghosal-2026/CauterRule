# Historical Replay Engine Design

## Purpose

Test candidate rules against all historical trajectories to determine:
1. Would they have prevented past failures?
2. Would they have broken past successes?

Produce deterministic, evidence-backed reports. Support visualization, "what if?" simulation, and draft tournaments.

## Interface

```
Input:  CandidateRule + historical trajectories (failures + successes)
Output: EvidenceReport {
    failures_prevented: string[],
    successes_broken: string[],
    failures_missed: string[],
    near_misses: string[],
    precision: float,
    recall: float,
    verdict: "pass" | "fail" | "inconclusive",
    replay_trace: ReplayTrace
}
```

## Algorithm

1. **Load** all historical trajectories from the scenarios directory (or tiered corpus)
2. **Match** the candidate rule's `when` clause against each trajectory's conditions
3. **Simulate** whether applying the rule would have changed the outcome:
   - For failures: Would applying the `do` directive have prevented the failure?
   - For successes: Would applying the `do` directive have caused a failure?
4. **Score**:
   - Precision = successes_broken == 0 (must not break anything)
   - Recall = failures_prevented >= 1 (must help on at least one)
   - Verdict = pass if precision AND recall

## Determinism

Same candidate + same corpus = same evidence report, always. No randomness in the replay engine. This is tested by the replay determinism test suite.

## Evidence Criteria

| Condition | Verdict |
|-----------|---------|
| Helps >=1 failure, breaks 0 successes | Pass |
| Helps >=1 failure, breaks >=1 success | Fail |
| Helps 0 failures, breaks 0 successes | Inconclusive (insufficient data) |
| Helps 0 failures, breaks >=1 success | Fail |

## Visualization

### Replay Visualization
Step-by-step view of how a rule would have changed a past trajectory. Shows each step with the original outcome and the simulated outcome side by side.

### Failure Time Machine (`cauterule rewind`)
1. User selects a failed trajectory
2. The trajectory is replayed step by step
3. User selects a rule to overlay (candidate or promoted)
4. At each step, the system shows whether the rule would have fired and what would have changed
5. The final outcome is compared: original (failed) vs simulated (would the rule have fixed it?)

### "What if?" Mode
Apply a hypothetical rule (not yet a candidate) to a trajectory and see the simulated outcome. No LLM extraction needed — the user writes the rule and the engine simulates it.

### Replay Diff
Before/after comparison of agent behavior with and without a rule. Shows:
- Which steps would have been different
- Which tool calls would have changed
- Whether the final outcome flips

## Draft Tournament

When the extractor produces N candidates:
1. All N are replay-tested in parallel
2. Evidence reports are compared
3. Ranking: precision (must be 100%) > recall (higher is better) > confidence > specificity
4. Winner is promoted; losers are archived with their evidence reports

## Edge Cases

### Insufficient History
If there are <3 historical trajectories, the replay returns "inconclusive" rather than "pass" — the evidence base is too thin.

### Partial Match (Near Miss)
If the rule's `when` clause partially matches a trajectory, it's logged as a "near miss" but not counted as prevented or broken. Near-miss precision is tracked (target: >=90% of near-miss scenarios do not trigger the rule).

### Conflicting Rules
If a candidate contradicts an existing promoted rule, the replay engine flags it. The existing rule's evidence is compared against the candidate's evidence to determine which is more specific.

## Performance

| Corpus Size | Target Latency per Candidate |
|-------------|-------------------------------|
| tiny (25) | <2s |
| small (100) | <10s |
| medium (1k) | <60s |
| large (10k+) | <600s (with caching) |

Replay throughput target: >=6 candidates/minute on `small` corpus.