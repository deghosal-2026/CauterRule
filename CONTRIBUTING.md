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
- Adversarial tests: `pytest tests/adversarial/ -v`
- Scale tests: `pytest tests/scale/ -v`
- TUI tests: `pytest tests/tui/ -v`
- Docker tests: `pytest tests/field/ -v -m docker`

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
  "redacted": false,
  "expected_outcome": "fail",
  "expected_outcome_rationale": "non-ff push rejected by remote"
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

### Trajectory Quality Labels

| Label | Meaning |
|-------|---------|
| `clear` | Unambiguous failure with obvious root cause |
| `noisy` | Failure present but obscured by irrelevant steps |
| `ambiguous` | Failure cause is debatable |
| `success` | No failure — used for safety/near-miss testing |

## Custom Agent Adapter

### `@cauterule.watch` decorator

Wrap any agent function to auto-capture trajectories on failure:

```python
from cauterule.adapter import watch

@watch(domain="coding", severity="medium")
def my_agent(task: str) -> str:
    # your agent logic
    ...
    return result
```

On failure, the trajectory is captured, redacted, and saved to the corpus directory for extraction.

### `cauterule.inject()` context manager

Prep context with matching rules before task execution:

```python
from cauterule.adapter import inject

with inject(task="deploy to production", domain="devops") as ctx:
    rules_text = ctx.rules_prompt  # formatted rules for your LLM
    # run your agent with rules_text injected
```

## Rule Pack Format

Rule packs are directories containing a `pack.yaml` manifest and rule YAML files:

```
pack-git/
├── pack.yaml          # manifest: name, version, description, rules
├── git-push-non-ff.yaml
├── git-merge-conflict.yaml
└── ...
```

### Pack Certification (v0.2.0)

Official packs must pass certification:

```bash
cauterule pack certify <pack-dir>
```

Certification checks:
- **Safety** — no unsafe directives, no broad triggers
- **Replay** — all rules pass replay against the golden corpus
- **Provenance** — author, version, and license metadata present

### Creating a Pack

1. Create a directory under `packs/` with your pack name
2. Add `pack.yaml` manifest
3. Add rule YAML files (see `rules/` for format examples)
4. Run `cauterule pack certify <pack-dir>`
5. Submit a PR with the certified pack

## v0.2.0 Contribution Areas

### Adversarial Corpus Contribution

Adversarial test cases validate rule robustness. To contribute:

1. Create trajectories in `field-test/corpus/adversarial/<type>/`
2. Types: `staleness`, `counterexample`, `noise`, `prompt-injection`, `redaction-bypass`, `nearmiss-escalation`
3. Each trajectory must have `expected_outcome` set to indicate the adversarial expectation
4. Run: `pytest tests/adversarial/ -v` to verify

### Benchmark Contribution

Add new benchmark scenarios:

1. Place benchmark corpus in `field-test/corpus/benchmark/`
2. Add benchmark test in `tests/benchmark/`
3. Benchmark types: determinism, acceptance, rejection, bake-off, mutation, calibration, ablation

### Observability Plugin Contribution

Contribute webhook or OTEL integrations:

1. Webhook: implement in `src/cauterule/integrations/webhook.py`
2. OTEL: implement in `src/cauterule/integrations/otel.py`
3. Add tests in `tests/observe/`
4. Document configuration in `cauterule.toml`