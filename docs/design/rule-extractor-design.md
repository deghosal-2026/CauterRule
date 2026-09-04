# Rule Extractor Design

## Purpose

Take a failure trajectory and produce candidate standing rules in *when X, do Y* form. Multi-pass extraction produces N candidates; draft tournaments rank them by replay evidence.

## Interface

```
Input:  Trajectory (JSONL) + failure_point + config
Output: list[CandidateRule] {
    when: { trigger: string, context: string[] },
    do: { directive: string, because: string },
    confidence: float,
    reasoning: string,
    extraction_pass: int,
    template: string | null
}
```

## Modes

### Normal Extraction
Multi-pass: run extraction 3x with temperature variation (0.2, 0.5, 0.8). Collect all valid candidates. Deduplicate by semantic similarity. Pass all to the draft tournament.

### Dry-Run Extraction
`cauterule extract --dry-run` — shows what would be extracted without making an LLM call. Uses cached results or pattern matching only. Saves cost.

### Human Correction Capture
User types "next time, do X" after a failure. The system:
1. Parses the correction into *when X, do Y* form using the trajectory context
2. Produces a candidate rule from the human input
3. Replay-tests it like any other candidate
4. Promotes if it survives

## Prompt Structure

```
You are analyzing an agent failure trajectory.
Extract a standing rule that would prevent this failure.

Trajectory: {trajectory_json}

Failure point: {failure_point}
Failure class: {failure_class}

Produce a rule in this form:
- WHEN: the condition that triggers the rule (specific, actionable)
- DO: the directive to follow
- BECAUSE: why this rule works
- CONFIDENCE: 0.0 to 1.0
- TEMPLATE: retry | verify-then-act | check-preconditions | null

The rule must be:
- Falsifiable (can be tested against historical scenarios)
- Actionable (the agent can follow it)
- Specific (not "be more careful")
```

## Extraction Strategies

### Strategy 1: Error-Pattern Match
Match the failure error to known error classes and extract the correction pattern.

### Strategy 2: Tool-Call Sequence Analysis
Analyze the sequence of tool calls leading to failure. Identify the missing step or wrong ordering.

### Strategy 3: State-Transition Analysis
Compare the agent's state at failure to the expected state. Extract rule from the delta.

### Strategy 4: Cross-Failure Pattern Detection
If this is the Nth failure of the same class, extract a stronger rule that addresses the pattern, not just the individual instance.

## Failure Clustering

Before extraction, failures are clustered by:
- Failure class (taxonomy)
- Tool sequence similarity
- Error message similarity

One extraction per cluster, not one per failure. This avoids producing 10 near-identical rules for 10 similar failures.

## Draft Tournament

1. Multi-pass extraction produces N candidates (typically 3-5)
2. All candidates are replay-tested against historical trajectories
3. Candidates are ranked by: precision > recall > confidence > specificity
4. The winner is promoted; others are archived with reasoning
5. If the top 2 are within 5% of each other, both are held for human review

## Quality Checks

- Rule must be in *when X, do Y* form (parsed successfully)
- Rule must reference a condition present in the trajectory
- Rule must not be tautological ("when failing, don't fail")
- Rule must pass the linter (not vague, not duplicate, not contradictory)
- Confidence threshold: >=0.6 for automatic processing
- Unsafe directives are blocked by the linter before replay

## Confidence Calibration

Extractor confidence scores are tracked against replay outcomes over time:
- If confidence 0.9 rules only pass replay 50% of the time, the system adjusts
- Calibration data feeds back into the promotion gate's hybrid mode thresholds
- `cauterule explain` shows calibrated confidence alongside raw confidence

## Fallback

If the LLM cannot produce a valid structured rule after all passes:
- The trajectory is flagged for human review
- The failure is logged for the coverage gap detector
- No low-quality candidate is generated