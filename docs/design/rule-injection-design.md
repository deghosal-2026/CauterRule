# Rule Injection Design

## Purpose

Before a task starts, inject matching standing rules into the agent's context so it benefits from accumulated wisdom.

## Interface

```
Input:  Task description + agent state
Output: Injected instructions (list of matching rules)
```

## Matching Algorithm

1. Parse the task description and initial agent state
2. Extract key signals: tool names, command patterns, error patterns, environment state
3. Match against active rules' `when.trigger` and `when.context` clauses
4. Return matched rules ordered by specificity (most specific first)

## Injection Format

```
## Standing Rules (Automatically Applied)

The following rules apply to this task based on your current context:

### R-018: When git push fails with non-fast-forward
- If you encounter a "non-fast-forward" error during git push:
  Run `git pull --rebase` first, then retry the push.
- Source: Learned from previous failure on shared branch work.
```

## Specificity Ordering

Rules are injected in order of specificity:
1. Rules with more context clauses first
2. Rules with exact trigger match before pattern match
3. Newer rules before older (if specificity is equal)

## Edge Cases

### No Matching Rules
If no rules match, injection produces an empty set. The agent runs without standing-rule context.

### Rule Conflict at Match Time
If two matched rules have contradictory directives, both are injected with a conflict note. The agent is expected to resolve — or the system flags it for rule store cleanup.