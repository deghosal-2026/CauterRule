# Standing Rule Format Design

## The Atomic Unit

Every standing rule is a structured *when X, do Y* pair:

```yaml
rule:
  id: "R-018"
  when:
    trigger: "tool call to git push fails with 'non-fast-forward' error"
    context:
      - "working on shared branch"
      - "multiple contributors"
  do:
    directive: "Run git pull --rebase before git push"
    because: "Non-fast-forward rejection means remote has commits local doesn't"
  tags: ["git", "git/push", "shared-branch"]
  taxonomy: "git/push/non-fast-forward"
  template: "verify-before-irreversible"
  confidence: 0.85
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
    promotion_mode: "auto"
  status: "active"
  promoted_at: "2026-09-03T18:35:00Z"
  hit_count: 3
  last_match: "2026-09-10T14:00:00Z"
  pack: null
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Auto-generated, sequential (R-001, R-002...) |
| `when.trigger` | string | yes | The condition that fires the rule |
| `when.context` | list | no | Additional context for matching (AND semantics) |
| `do.directive` | string | yes | The behavior to follow |
| `do.because` | string | no | Rationale (extracted by LLM) |
| `tags` | list | no | User-defined tags for organization and filtering |
| `taxonomy` | string | no | Auto-classified failure class (e.g. `git/push`, `python/import`) |
| `template` | string | no | Rule template name (retry, verify-then-act, check-preconditions) |
| `confidence` | float | yes | Extractor confidence (0.0-1.0), calibrated against replay outcomes |
| `provenance` | object | yes | Full provenance chain (see below) |
| `status` | enum | yes | active, retired, superseded |
| `promoted_at` | datetime | yes | When it entered the store |
| `hit_count` | int | yes | How many times it matched |
| `last_match` | datetime | no | Last match timestamp |
| `pack` | string | no | Pack name if this rule came from a rule pack |

## Provenance Object

| Field | Type | Description |
|-------|------|-------------|
| `source_trajectory` | string | Path to the JSONL trajectory that spawned this rule |
| `extracted_by` | string | LLM model that extracted the candidate |
| `extract_timestamp` | datetime | When extraction occurred |
| `extraction_pass` | int | Which multi-pass attempt produced this candidate (1-3) |
| `draft_tournament_rank` | int | Rank in the draft tournament (1 = winner) |
| `replay_evidence` | object | Failures prevented, successes broken, precision, recall |
| `promotion_commit` | string | Git commit hash of the promotion |
| `promotion_mode` | enum | auto, human-review, hybrid |

## Matching Semantics

A rule fires when the current task's conditions satisfy the `when` clause:
- **trigger** is a pattern match against the current error, tool call, or state
- **context** is an optional list of additional conditions (AND semantics)
- **tags** are used for filtering and organization, not for matching
- **taxonomy** is used for coverage gap detection and failure class matching
- Match is structural (keyword + pattern), not semantic (embedding) in v0.1.0

## Rule Templates

Common rule patterns are templatized for consistency:

| Template | Pattern | Example |
|----------|---------|---------|
| `retry` | When X fails, retry with Y | When git push fails, retry after pull --rebase |
| `verify-then-act` | Before doing X, verify Y | Before git push, verify local is up to date |
| `check-preconditions` | Before doing X, check Y exists | Before deploy, check tests pass |

## Rule Precedence

More specific rules take priority over less specific ones:
- A rule with `context` outranks one without
- A rule with more `context` items outranks one with fewer
- A rule with a more specific `taxonomy` subtype outranks a broader one
- Direct contradictions are flagged for human review

## Rule Linter Checks

The linter validates rules for:
- **Vagueness** — trigger or directive is too generic ("be careful")
- **Tautology** — "when failing, don't fail"
- **Duplicates** — semantically identical to an existing rule
- **Contradictions** — conflicts with an existing rule
- **Untestable** — directive cannot be verified via replay