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
    domain_scoped: bool,
    reference_pool_size: int,
    replay_trace: ReplayTrace
}
```

## Algorithm

1. **Load** all historical trajectories from the scenarios directory (or tiered corpus)
2. **Match** the candidate rule's `when` clause against each trajectory's conditions
3. **Simulate** whether applying the rule would have changed the outcome:
   - For failures: Would applying the `do` directive have prevented the failure?
   - For successes: Would applying the `do` directive have caused a failure?
4. **Score** against a domain-scoped reference pool (v0.3.0). Pass requires precision >= 0.5 after the broad-trigger and near-miss penalties; see "Scoring Changes in v0.3.0" below for the exact rules.

## Determinism

Same candidate + same corpus = same evidence report, always. No randomness in the replay engine. This is tested by the replay determinism test suite.

## Evidence Criteria

| Condition | Verdict |
|-----------|---------|
| Helps >=1 failure, breaks 0 successes | Pass |
| Helps >=1 failure, breaks >=1 success | Fail |
| Helps 0 failures, breaks 0 successes | Inconclusive (insufficient data) |
| Helps 0 failures, breaks >=1 success | Fail |

## Scoring Changes in v0.3.0

The scorer is safety-first and tuned against the v0.3.0 field test:

- **Domain-scoped reference pool (#708)** — `reference_trajs` is scoped to the source trajectory's domain (git, python, docker, …), falling back to the full pool only when the domain slice has <3 failures. This reduces the recall denominator from ~200 to ~10–30 and lifted recall 2–3× (0.087 → 0.170–0.228).
- **Self-match exclusion** — the source trajectory is removed from its own reference set so a candidate cannot count the failure it was extracted from as "prevented".
- **Near-miss penalty with tolerance band** — near-misses are penalized, but `near_misses <= 2` still passes when `precision >= 0.5`, so one near-miss reference cannot disqualify a rule that prevents real failures.
- **Pass threshold 0.8 → 0.5** — with the broad aliases (#492) removed, honest precision is 0.3–0.7; the 0.8 bar was unreachable and produced inconclusive verdicts for useful candidates.
- **Broad-trigger penalty** — breaking a success marks a candidate inconclusive regardless of failures prevented (see `promotion-gate-design.md`).
- **Recovery gate** — `success=True` trajectories with a recovery pattern are silenced rather than scored as preventions.
- **Semantic matching (optional)** — `CAUTERULE_SEMANTIC_MATCHING=1` adds a MiniLM cosine term to the blend `0.5·token-F1 + 0.3·bigram + 0.2·semantic`. It is off by default; the 0.2 weight is a known ceiling on paraphrase bridging.

Determinism is preserved: the same candidate and same corpus still produce the same evidence report.

## Inconclusive Attribution

Every `inconclusive` verdict carries an `inconclusive_reason` root-cause category so summaries can tell you whether to fix the model, the matcher, or the corpus:

| Reason | Meaning | Fix direction |
|--------|---------|---------------|
| `broad_trigger` | Trigger too generic to verify (≤2 content tokens) | Model — improve extraction specificity |
| `matcher_gap` | Trigger specific but matcher recognized nothing | Engine — improve matcher vocabulary |
| `corpus_mismatch` | Insufficient history (<3 trajectories) | Corpus — add more trajectories |
| `ambiguous_evidence` | Near-misses or borderline precision, no decision | Corpus — clarify trajectories |

`cauterule test` prints the reason for inconclusive verdicts. `summarize_inconclusive()` aggregates counts by reason for field-test summaries (e.g. "189 inconclusive = 72 broad_trigger + 61 matcher_gap + 38 corpus_mismatch + 18 ambiguous_evidence"). Track the rate over time: rising means judgment is degrading, falling means it is improving.

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
If the rule's `when` clause partially matches a trajectory, it's logged as a "near miss" but not counted as prevented or broken. Near-miss precision is tracked (target: >=90% of near-miss scenarios do not trigger the rule). v0.3.0 penalizes near-misses with a tolerance band (`near_misses <= 2 → pass if precision >= 0.5`) and reports 98–100% near-miss precision.

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