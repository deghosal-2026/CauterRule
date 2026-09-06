# Trajectory Schema Design

## Format

JSONL — one JSON object per step in the execution.

## Schema per Line

```json
{
  "trajectory_id": "T-003",
  "timestamp": "2026-09-03T18:25:00Z",
  "task": "Deploy to staging",
  "steps": [
    {
      "step_number": 1,
      "tool": "bash",
      "input": "git push origin feature-branch",
      "output": "! [rejected] non-fast-forward",
      "error": "non-fast-forward error",
      "state": {
        "branch": "feature-branch",
        "remote": "origin",
        "has_unpushed": true
      }
    }
  ],
  "failure_point": "step_1",
  "failure_class": "git/push/non-fast-forward",
  "success": false,
  "quality_label": "clear",
  "domain": "git",
  "severity": "medium",
  "tags": ["git", "push", "shared-branch"],
  "agent_config": {
    "model": "gpt-4o",
    "tools": ["bash", "read", "write"]
  },
  "environment": {
    "os": "linux",
    "ci": true
  },
  "redacted": true
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `trajectory_id` | string | Unique trajectory identifier |
| `timestamp` | datetime | When the task ran |
| `task` | string | The task description |
| `steps` | array | Array of step objects |
| `failure_point` | string | Which step failed |
| `failure_class` | string | Auto-classified taxonomy (e.g. `git/push`, `python/import`, `docker/network`) |
| `success` | bool | Whether the task completed successfully |
| `quality_label` | enum | `clear`, `ambiguous`, `multi-causal`, `misleading`, `operator-induced` |
| `domain` | string | Domain tag (git, python, docker, shell, ci, env) |
| `severity` | enum | `low`, `medium`, `high` |
| `tags` | list | User-defined or auto-generated tags |
| `agent_config` | object | Agent configuration at time of execution |
| `environment` | object | OS, CI flag, and other environment context |
| `redacted` | bool | Whether secrets have been stripped from this trajectory |

## Step Object

| Field | Type | Description |
|-------|------|-------------|
| `step_number` | int | Sequential step number |
| `tool` | string | Tool invoked |
| `input` | string | Tool input (truncated if large, redacted if secrets detected) |
| `output` | string | Tool output (truncated if large, redacted if secrets detected) |
| `error` | string | Error message if any |
| `state` | object | Agent state at this step |

## Redaction

Before LLM extraction, trajectories are redacted:
- API keys, tokens, passwords, and secrets are replaced with `[REDACTED]`
- Configurable patterns via `cauterule.toml`
- Auto-detection of common secret formats (AWS keys, GitHub tokens, JWTs, etc.)
- `redacted: true` flag is set on the trajectory metadata
- Redaction corpus validates 100% success rate

## File Naming

```
trajectories/YYYY-MM-DD/failure-T-{NNN}.jsonl
trajectories/YYYY-MM-DD/success-T-{NNN}.jsonl
```

Failures and successes are stored separately for efficient replay filtering.

## Corpus Tiers

| Tier | Count | Use |
|------|-------|-----|
| `tiny` | 25 | Local dev, fast iteration |
| `small` | 100 | CI, regression tests |
| `medium` | 1k | Benchmark, model bake-off |
| `large` | 10k+ | Scale testing, performance gates |