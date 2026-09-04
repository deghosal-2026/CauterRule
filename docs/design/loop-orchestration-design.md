# Loop Orchestration Design

## Purpose

Orchestrate the full extract → test → promote → inject cycle.

## Trigger

The loop triggers on agent task completion:
- **Failure:** Full cycle: capture → extract → test → promote (conditional)
- **Success:** Capture only (adds to historical success set for future replay)

## Orchestration Flow

```
1. Task completes
2. Trajectory Capture writes JSONL
3. Is failure?
   └─ No → store as success scenario → done
   └─ Yes → proceed to extraction
4. Rule Extractor reads trajectory → produces candidate
5. Candidate valid?
   └─ No → flag for human review → done
   └─ Yes → proceed to replay
6. Historical Replay Engine tests candidate
7. Verdict?
   └─ Pass → Promotion Gate promotes → git commit → done
   └─ Fail → archive candidate with evidence → done
   └─ Inconclusive → hold for human review → done
8. (Background) Rule Injection on next task start
```

## Concurrency

- Extraction and replay are synchronous (one at a time per agent)
- Conflict detection runs asynchronously after promotion
- Rule injection is pre-task, synchronous

## Configuration

```yaml
loop:
  mode: "auto" | "human-review"
  replay_threshold: "balanced" | "conservative" | "aggressive"
  conflict_check: "on-promotion" | "weekly" | "manual"
  injection_enabled: true
```

## Error Handling

- **Extraction failure:** Retry once with different temperature. If still fails, flag for human.
- **Replay engine failure:** Candidate is held. Previous candidate is not blocked.
- **Promotion git failure:** Rule is saved locally. Git push retried on next cycle.