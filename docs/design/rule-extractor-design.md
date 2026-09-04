# Rule Extractor Design

## Purpose

Take a failure trajectory and produce a candidate standing rule in *when X, do Y* form.

## Interface

```
Input:  Trajectory (JSONL) + failure_point
Output: CandidateRule {
    when: { trigger: string, context: string[] },
    do: { directive: string, because: string },
    confidence: float,
    reasoning: string
}
```

## Prompt Structure

```
You are analyzing an agent failure trajectory. 
Extract a standing rule that would prevent this failure.

Trajectory: {trajectory_json}

Failure point: {failure_point}

Produce a rule in this form:
- WHEN: the condition that triggers the rule (specific, actionable)
- DO: the directive to follow
- BECAUSE: why this rule works
- CONFIDENCE: 0.0 to 1.0

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

## Quality Checks

- Rule must be in *when X, do Y* form (parsed successfully)
- Rule must reference a condition present in the trajectory
- Rule must not be tautological ("when failing, don't fail")
- Confidence threshold: ≥0.6 for automatic processing

## Fallback

If the LLM cannot produce a valid structured rule, the trajectory is flagged for human review instead of generating a low-quality candidate.