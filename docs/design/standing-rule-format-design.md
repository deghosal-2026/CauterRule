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
  provenance:
    source_trajectory: "trajectories/2026-09-03/failure-003.jsonl"
    extracted_by: "gpt-4o"
    extract_timestamp: "2026-09-03T18:30:00Z"
    replay_evidence:
      failures_prevented: ["F-001", "F-007"]
      successes_broken: []
  status: "active"
  promoted_at: "2026-09-03T18:35:00Z"
  hit_count: 0
  last_match: null
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Auto-generated, sequential (R-001, R-002...) |
| `when.trigger` | string | yes | The condition that fires the rule |
| `when.context` | list | no | Additional context for matching |
| `do.directive` | string | yes | The behavior to follow |
| `do.because` | string | no | Rationale (extracted by LLM) |
| `provenance` | object | yes | Full provenance chain |
| `status` | enum | yes | active, retired, superseded |
| `promoted_at` | datetime | yes | When it entered the store |
| `hit_count` | int | yes | How many times it matched |
| `last_match` | datetime | no | Last match timestamp |

## Matching Semantics

A rule fires when the current task's conditions satisfy the `when` clause:
- **trigger** is a pattern match against the current error, tool call, or state
- **context** is an optional list of additional conditions (AND semantics)
- Match is structural (keyword + pattern), not semantic (embedding) in v0.x

## Rule Precedence

More specific rules take priority over less specific ones:
- A rule with `context` outranks one without
- A rule with more `context` items outranks one with fewer
- Direct contradictions are flagged for human review