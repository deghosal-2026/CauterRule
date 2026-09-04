# Rule Injection Design

## Purpose

Before a task starts, inject matching standing rules into the agent's context so it benefits from accumulated wisdom. Include explanations, templates, and context budget optimization.

## Interface

```
Input:  Task description + agent state + context budget (optional)
Output: InjectedRuleSet {
    rules: list[InjectedRule],
    explanations: list[string],
    total_tokens: int
}
```

## Matching Algorithm

1. Parse the task description and initial agent state
2. Extract key signals: tool names, command patterns, error patterns, environment state, tags
3. Match against active rules' `when.trigger`, `when.context`, `taxonomy`, and `tags` clauses
4. Return matched rules ordered by specificity (most specific first)
5. If a context budget is specified, prioritize and compress to fit

## Injection Format

```
## Standing Rules (Automatically Applied)

The following rules apply to this task based on your current context:

### R-018: When git push fails with non-fast-forward
- If you encounter a "non-fast-forward" error during git push:
  Run `git pull --rebase` first, then retry the push.
- Why: Non-fast-forward rejection means the remote has commits your local doesn't.
- Source: Learned from previous failure on shared branch work (2026-09-03).
- Confidence: 85% (replay-tested: prevented 2 past failures, broke 0 successes)

### R-005: Before git push, verify local is up to date
- Before running git push, check if your local branch is behind the remote.
- Why: Pushing to an out-of-date branch causes non-fast-forward rejection.
- Source: Bundled pack-git (v1.0.0).
```

## Rule Explanations

`cauterule explain <rule-id>` generates a human-readable explanation:
- Why the rule fires (trigger conditions in plain English)
- When it applies (context and taxonomy)
- What it does (directive in plain English)
- Why it exists (provenance: source failure, replay evidence)
- How confident we are (calibrated confidence)

Explanations are also included in the injection block when `explain: true` is set in config.

## Rule Templates

Rules can reference templates for consistent behavior patterns:

| Template | Injection Behavior |
|----------|-------------------|
| `retry` | Inject as "if X fails, retry with Y" |
| `verify-then-act` | Inject as "before doing X, verify Y" |
| `check-preconditions` | Inject as "before doing X, check that Y exists/passes" |

## Context Budget Optimizer

When the agent has a limited context budget:
1. Rules are ranked by: specificity > hit_count > last_match > confidence
2. Rules are injected in rank order until the token budget is exhausted
3. Lower-ranked rules are compressed (trigger + directive only, no explanation)
4. If the budget is very tight, only the top N rules are injected as one-liners

## Specificity Ordering

Rules are injected in order of specificity:
1. Rules with more context clauses first
2. Rules with exact trigger match before pattern match
3. Rules with more specific taxonomy before broader taxonomy
4. Newer rules before older (if specificity is equal)

## Preflight Mode

`cauterule inject <task> --preflight` predicts:
- Which rules would fire
- Which failure classes are most likely for this task
- Which rules are recommended to load

## Edge Cases

### No Matching Rules
If no rules match, injection produces an empty set. The agent runs without standing-rule context.

### Rule Conflict at Match Time
If two matched rules have contradictory directives, both are injected with a conflict note. The system also flags the conflict for rule store cleanup via `cauterule conflicts`.

### Pack Rules
Pack rules are injected alongside locally learned rules. If a pack rule and a local rule have the same trigger, the more specific one takes precedence.