# Rule Store Design

## Location

```
rules/
  index.yaml           # Rule index (all rules, current status)
  R-001.yaml           # Individual rule files
  R-002.yaml
  ...
  archived/            # Retired or superseded rules
    R-003.yaml
```

## Index File

```yaml
rules:
  - id: "R-001"
    status: "active"
    promoted_at: "2026-09-01T10:00:00Z"
    summary: "When git push fails with non-fast-forward, run pull --rebase first"

  - id: "R-002"
    status: "retired"
    promoted_at: "2026-09-02T14:00:00Z"
    retired_at: "2026-09-15T09:00:00Z"
    retirement_reason: "Superseded by R-007 which covers this case more precisely"
```

## Versioning

Git provides versioning:
- Every promotion = a git commit with message `promote: R-018`
- Every retirement = a git commit with message `retire: R-003 (superseded by R-007)`
- Rollback = `git revert <commit>`
- Diff = `git diff` between any two versions

## Provenance Chain

Each rule file contains a `provenance` section:
```yaml
provenance:
  source_trajectory: "trajectories/2026-09-03/failure-003.jsonl"
  extracted_by: "gpt-4o"
  extract_timestamp: "2026-09-03T18:30:00Z"
  replay_evidence:
    failures_prevented: ["F-001", "F-007"]
    successes_broken: []
  promotion_commit: "abc123def"
```

## Rule Lifecycle

```
Candidate → [Replay Test] → Promoted (active) → [Hit tracking] → 
  → Retired (if stale/unused) or Superseded (if replaced by better rule)
```