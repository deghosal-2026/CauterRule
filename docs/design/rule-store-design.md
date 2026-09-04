# Rule Store Design

## Location

```
rules/
  index.yaml           # Rule index (all rules, current status, tags, taxonomy)
  R-001.yaml           # Individual rule files
  R-002.yaml
  ...
  archived/            # Retired or superseded rules
    R-003.yaml
  packs/               # Installed rule packs
    pack-git/
      manifest.yaml    # Pack metadata (name, version, author, description)
      R-101.yaml       # Pack rules
      R-102.yaml
```

## Index File

```yaml
rules:
  - id: "R-001"
    status: "active"
    promoted_at: "2026-09-01T10:00:00Z"
    summary: "When git push fails with non-fast-forward, run pull --rebase first"
    tags: ["git", "git/push"]
    taxonomy: "git/push/non-fast-forward"
    hit_count: 12
    last_match: "2026-09-10T14:00:00Z"
    pack: null

  - id: "R-002"
    status: "retired"
    promoted_at: "2026-09-02T14:00:00Z"
    retired_at: "2026-09-15T09:00:00Z"
    retirement_reason: "Superseded by R-007 which covers this case more precisely"
    pack: null

  - id: "R-101"
    status: "active"
    promoted_at: "2026-09-01T00:00:00Z"
    summary: "Before git push, verify local branch is up to date"
    tags: ["git", "git/push"]
    taxonomy: "git/push"
    pack: "pack-git"
```

## Versioning

Git provides versioning:
- Every promotion = a git commit with message `promote: R-018`
- Every retirement = a git commit with message `retire: R-003 (superseded by R-007)`
- Every consolidation = a git commit with message `consolidate: R-005, R-008 → R-012`
- Rollback = `git revert <commit>`
- Diff = `cauterule diff <rule-id>` or `git diff` between any two versions

## Provenance Chain

Each rule file contains a `provenance` section:
```yaml
provenance:
  source_trajectory: "trajectories/2026-09-03/failure-003.jsonl"
  extracted_by: "gpt-4o"
  extract_timestamp: "2026-09-03T18:30:00Z"
  extraction_pass: 2
  draft_tournament_rank: 1
  replay_evidence:
    failures_prevented: ["F-001", "F-007"]
    successes_broken: []
    precision: 1.0
    recall: 0.28
  promotion_commit: "abc123def"
  promotion_mode: "hybrid-auto"
```

## Rule Lifecycle

```
Candidate → [Linter] → [Replay Test] → [Conflict Check] → Promoted (active)
    → [Hit tracking] → [Coverage gap analysis]
    → Retired (if stale/unused) or Superseded (if replaced by better rule)
    → Consolidated (if merged with similar rules)
```

## Validation

`cauterule validate` checks rule store integrity:
- No orphaned provenance references (source trajectory exists)
- No missing provenance fields (source, evidence, timestamps)
- No broken pack references
- No duplicate rule IDs
- No rules with invalid status values
- All active rules have valid YAML

## Health Report

`cauterule health` produces a rule store health report:
- Total active rules
- Coverage by domain and failure class
- Stale rules (no hits in N days)
- Conflict count
- Average effectiveness score
- Coverage gaps (recurring failures with no matching rules)
- Rule coverage score (weighted blend of coverage, precision, and stale ratio)

## Consolidation

When the conflict detector or linter finds overlapping rules:
1. Rules with similar triggers are grouped
2. The most specific rule is kept
3. Less specific rules are archived with `superseded_by` pointing to the winner
4. If two rules are equally specific but not contradictory, they are merged into one
5. Consolidation is a git commit with the merge reasoning

## Pack Integration

Bundled packs (e.g. `pack-git`) are stored in `rules/packs/`:
- Pack rules have `pack: "pack-git"` in their metadata
- Pack rules are read-only (cannot be retired or modified locally)
- Pack versioning follows semantic versioning
- `cauterule pack list` shows installed packs
- `cauterule pack info <name>` shows pack contents and metadata