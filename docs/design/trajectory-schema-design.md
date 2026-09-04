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
  "failure_class": "git_non_fast_forward",
  "success": false,
  "agent_config": {
    "model": "gpt-4o",
    "tools": ["bash", "read", "write"]
  }
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
| `failure_class` | string | Categorization of failure type |
| `success` | bool | Whether the task completed successfully |
| `agent_config` | object | Agent configuration at time of execution |

## Step Object

| Field | Type | Description |
|-------|------|-------------|
| `step_number` | int | Sequential step number |
| `tool` | string | Tool invoked |
| `input` | string | Tool input (truncated if large) |
| `output` | string | Tool output (truncated if large) |
| `error` | string | Error message if any |
| `state` | object | Agent state at this step |

## File Naming

```
trajectories/YYYY-MM-DD/failure-T-{NNN}.jsonl
trajectories/YYYY-MM-DD/success-T-{NNN}.jsonl
```

Failures and successes are stored separately for efficient replay filtering.