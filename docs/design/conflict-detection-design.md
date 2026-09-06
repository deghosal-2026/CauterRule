# Conflict Detection Design

## Purpose

Detect when a new or existing rule contradicts another rule in the store, establish ordering, and consolidate overlapping rules.

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

### Overlap (Non-Contradictory)
Two rules cover similar ground but don't contradict.
```
R-005: When git push fails → run pull --rebase
R-008: When git push fails → check if branch is protected first
```
**Action:** Flag for consolidation. Both can coexist, but the user may want to merge.

## Specificity Scoring

| Factor | Weight |
|--------|--------|
| Number of `context` clauses | +1 each |
| Exact string match in trigger (vs. pattern) | +2 |
| Error class is more specific subtype (taxonomy depth) | +3 |
| Rule has been hit-tested in production | +1 |
| Rule has higher replay precision | +1 |

## Consolidation

When overlapping rules are detected:
1. Rules with similar triggers are grouped
2. The most specific rule is identified by specificity score
3. Less specific rules are archived with `superseded_by` pointing to the winner
4. If two rules are equally specific but not contradictory, they are merged into one
5. Merge creates a new rule with combined context and the union of provenance
6. Consolidation is a git commit with merge reasoning

## Rule Linter Integration

The linter runs conflict detection as part of its checks:
- **Duplicates** — semantically identical to an existing rule → blocked
- **Contradictions** — conflicts with an existing rule → blocked, conflict report generated
- The linter and conflict detector share the same specificity scoring

## Detection Trigger

Conflict detection runs:
1. After every promotion (check new rule against all existing rules)
2. On demand via CLI (`cauterule conflicts`)
3. As part of `cauterule validate`
4. As part of `cauterule health`

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

  - type: "overlap"
    rules: ["R-005", "R-008"]
    resolution: "flagged for consolidation"

consolidation_candidates:
  - rules: ["R-005", "R-008", "R-011"]
    suggested_action: "merge into one rule with combined context"
    specificity_winner: "R-011"
```

## Scale

Conflict detection is pairwise by default. At 1k rules, naive pairwise is ~500k comparisons. Performance target: <5s at 1k rules. For larger stores, an index on trigger patterns and taxonomy reduces the comparison set.