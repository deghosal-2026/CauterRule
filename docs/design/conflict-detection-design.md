# Conflict Detection Design

## Purpose

Detect when a new or existing rule contradicts another rule in the store, and establish ordering.

## Types of Conflicts

### Direct Contradiction
Same trigger X, different directives Y and not-Y.
```
R-001: When git push fails → run pull --rebase
R-002: When git push fails → run pull --ff-only
```
**Action:** Flag for human review. Cannot auto-promote either rule.

### Specificity Conflict
Broader rule says one thing, narrower rule says another.
```
R-003: When any tool fails → retry with --verbose
R-007: When git push fails with non-fast-forward → run pull --rebase
```
**Action:** More specific rule takes precedence (R-007 wins when both match).

### Supersession
New rule covers the same ground as an old rule but is more precise.
```
R-005: When git push fails → run pull --rebase
R-012: When git push fails with non-fast-forward on shared branch → run pull --rebase
```
**Action:** R-012 supersedes R-005. R-005 is archived with `superseded_by: R-012`.

## Specificity Scoring

| Factor | Weight |
|--------|--------|
| Number of `context` clauses | +1 each |
| Exact string match in trigger (vs. pattern) | +2 |
| Error class is more specific subtype | +3 |
| Rule has been hit-tested in production | +1 |

## Detection Trigger

Conflict detection runs:
1. After every promotion (check new rule against all existing rules)
2. On demand via CLI (`cauterule check-conflicts`)
3. Weekly scheduled check (idempotent)

## Output

```yaml
conflicts:
  - type: "direct_contradiction"
    rules: ["R-001", "R-002"]
    trigger: "git push fails with non-fast-forward"
    resolution: "requires human review"
  
  - type: "specificity"
    broader: "R-003"
    narrower: "R-007"
    resolution: "R-007 takes precedence when both match"
```