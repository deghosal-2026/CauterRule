# Loop Orchestration Design

## Purpose

Orchestrate the full extract → test → promote → inject cycle, including multi-pass extraction, failure clustering, redaction, dry-run, and human correction capture.

## Trigger

The loop triggers on agent task completion:
- **Failure:** Full cycle: capture → redact → cluster → extract (multi-pass) → lint → replay → tournament → promote (conditional)
- **Success:** Capture only (adds to historical success set for future replay)

## Orchestration Flow

```
 1. Task completes
 2. Trajectory Capture writes JSONL
 3. Redaction strips secrets from trajectory
 4. Is failure?
    └─ No → store as success scenario → done
    └─ Yes → proceed to clustering
 5. Failure Clustering: group with similar failures
    └─ If cluster already has a pending extraction → skip
 6. Rule Extractor (multi-pass, 3x temperature variation)
    └─ Produces N candidates (typically 3-5)
 7. Draft Tournament: all candidates replay-tested, ranked
 8. Best candidate → Rule Linter
    └─ Vague/tautological/duplicate/contradictory/unsafe → blocked → done
 9. Linter-passed candidate → Historical Replay Engine
10. Verdict?
    └─ Pass → Conflict Detection
    └─ Fail → archive candidate with evidence → done
    └─ Inconclusive → hold for human review → done
11. Conflict Detection against existing rules
    └─ Direct contradiction → hold for human review → done
    └─ No conflicts → proceed to promotion
12. Promotion Gate (auto/hybrid/human)
    └─ Auto: promoted → git commit → done
    └─ Hybrid: high-confidence → auto-promote; low-confidence → human review
    └─ Human: held for `cauterule review` → done
13. (Background) Rule Injection on next task start
14. (Background) Metrics, coverage, learning journal updated
```

## Special Modes

### Dry-Run Mode
`cauterule extract --dry-run` — shows what would be extracted without making an LLM call. Uses cached results or pattern matching only. Does not write to the rule store.

### Human Correction Capture
After a failure, the user can type "next time, do X":
1. The correction is parsed into *when X, do Y* form using the trajectory context
2. The candidate is produced from the human input (no LLM extraction needed)
3. The candidate goes through the same replay → lint → conflict → promote pipeline
4. If it survives, it's promoted like any other rule

### Preflight Mode
`cauterule inject <task> --preflight` — before the agent starts, predicts likely failure classes and recommends rules to load. Does not run the full loop.

## Concurrency

- Extraction and replay are synchronous (one at a time per agent)
- Conflict detection runs asynchronously after promotion
- Rule injection is pre-task, synchronous
- Multiple failures arriving simultaneously are queued and deduplicated by cluster

## Configuration

```yaml
loop:
  mode: "auto" | "human-review" | "hybrid"
  replay_threshold: "conservative" | "balanced" | "aggressive"
  conflict_check: "on-promotion" | "weekly" | "manual"
  injection_enabled: true
  extraction:
    passes: 3
    temperatures: [0.2, 0.5, 0.8]
    confidence_threshold: 0.6
  clustering:
    enabled: true
    similarity_threshold: 0.85
  redaction:
    enabled: true
    patterns: ["aws_key", "github_token", "jwt", "custom"]
```

## Error Handling

- **Extraction failure:** Retry once with different temperature. If still fails, flag for human review.
- **Replay engine failure:** Candidate is held. Previous candidate is not blocked.
- **Linter failure:** Candidate is blocked with reasoning. Logged for coverage gap analysis.
- **Promotion git failure:** Rule is saved locally. Git push retried on next cycle.
- **Conflict detection failure:** Promotion proceeds; conflict check retried asynchronously.
- **Redaction failure:** Extraction is blocked. Trajectory is flagged for manual review.