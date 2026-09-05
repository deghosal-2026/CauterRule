# Contributing to CauterRule

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate: `source .venv/bin/activate`
4. Install: `pip install -e ".[dev]"`
5. Run tests: `pytest`

## Code Quality

- Format: `ruff check .` then `ruff format .`
- Types: `mypy src/ tests/`
- Tests: `pytest tests/ -v --cov=cauterule`

## Contributing Trajectories

### Format Specification

Trajectories are stored as JSONL (one JSON object per line) with the following schema (version `1.0`):

```json
{
  "trajectory_id": "unique-id",
  "timestamp": "2026-09-03T18:25:00Z",
  "task": "description of the task",
  "steps": [
    {
      "step_number": 1,
      "tool": "bash",
      "input": "command input",
      "output": "command output",
      "error": null,
      "state": {}
    }
  ],
  "success": false,
  "failure_point": "step_1",
  "failure_class": "domain/error-category",
  "quality_label": "clear",
  "domain": "coding",
  "severity": "medium",
  "tags": ["example", "git"],
  "agent_config": {"model": "gpt-4o", "tools": ["bash", "read"]},
  "environment": {"os": "linux", "ci": true},
  "redacted": false
}
```

### Submission Process

1. Place your JSONL file in `corpus/public/` with a descriptive name following the pattern `<domain>-<scenario>-<tier>.jsonl`.
2. Each file should contain only trajectories from a single scenario/domain.
3. Run `ruff check` and `mypy` on any new code.
4. Ensure all existing tests still pass.
5. Submit a pull request with a description of the new trajectories.

### Naming Convention

File names use the format:

```
<domain>-<scenario>-<tier>.jsonl
```

Examples:
- `coding-fix-sort-tiny.jsonl`
- `devops-deploy-medium.jsonl`
- `research-paper-summary-small.jsonl`

Domains: `coding`, `devops`, `research`, `support`, `browser_automation`
Tiers: `tiny` (≤25), `small` (≤100), `medium` (≤1,000), `large` (>1,000)

Each trajectory must have at least one step, a valid timestamp, and a unique ID.