# Contributing to CauterRule

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv` (Python 3.11–3.13)
3. Activate: `source .venv/bin/activate`
4. Install: `pip install -e ".[dev]"` (add `.[all]` for LLM/OTEL/semantic extras)
5. Run tests: `pytest`

## Code Quality

- Format: `ruff check .` then `ruff format .`
- Types: `mypy src/ tests/`
- Tests: `pytest tests/ -v --cov=cauterule`
- Corpus validation: `cauterule corpus validate <dir>` and `cauterule corpus lint <dir>`
- Provider/corpus preflight: `cauterule preflight --corpus <dir>`
- Adversarial tests: `pytest tests/adversarial/ -v`
- Adapter conformance: `pytest tests/adapter_conformance/ -v`
- Pack tests: `pytest tests/packs/ -v`
- Scale tests: `pytest tests/scale/ -v`
- TUI tests: `pytest tests/tui/ -v`
- Docker tests: `pytest tests/field/ -v -m docker`

## Choosing an Issue

Work is organized by milestone (M1–M8) per release, tracked in the GitHub
milestone and the WBS under `docs/wbs/vX.Y.Z/`. To contribute:

1. Pick an open issue in the current milestone (or one tagged `good first issue`).
2. Comment to claim it to avoid duplicate work.
3. Branch from the active feature branch (e.g. `feat-v0.3.0`), not `main`.
4. Keep the change scoped to the issue; reference the issue number in commits.
5. Ensure `ruff`, `mypy`, and the relevant tests pass before opening a PR.

Pack and adapter changes have extra review expectations — see
[Adapter Conformance](#adapter-conformance) and [Contributing a Pack](#contributing-a-pack).

## Contributing Trajectories

### Format Specification

Trajectories are stored as JSONL (one JSON object per line) with the following schema (version `1.0`). `CORPUS_SCHEMA_VERSION` is enforced by `cauterule preflight` and `cauterule corpus validate`: a corpus with `schema_version` absent is treated as `1.0`; any other value is rejected.

```json
{
  "schema_version": "1.0",
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

Required: `trajectory_id` (unique), `timestamp`, `task`, at least one `step`
with an explicit `step_number`, and explicit `success`. Safety/adversarial
corpora additionally require `expected_outcome`
(`pass` | `fail` | `should_reject`) and `expected_outcome_rationale`.

### Submission Process

1. Place your JSONL file in `corpus/public/` with a descriptive name following the pattern `<domain>-<scenario>-<tier>.jsonl`.
2. Each file should contain only trajectories from a single scenario/domain.
3. Validate: `cauterule corpus validate corpus/public/` and `cauterule corpus lint corpus/public/`.
4. Run `ruff check` and `mypy` on any new code.
5. Ensure all existing tests still pass.
6. Submit a pull request with a description of the new trajectories.

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

The consolidated (M3) vocabulary — use exactly one:

| Label | Meaning |
|-------|---------|
| `clear` | Unambiguous failure with obvious root cause |
| `noisy` | Failure present but obscured by irrelevant steps |
| `ambiguous` | Failure cause is debatable |
| `multi-causal` | More than one plausible contributing cause |
| `misleading` | Surface symptom points away from the real cause |
| `operator-induced` | Failure caused by user/operator input, not the agent |
| `open-ended` | No single correct resolution; used for exploration |

### Corpus Types

- **Golden** — curated, hand-labeled failures with clear expected rules.
- **Counterexample** — a correct-looking rule produces a wrong prevention.
- **Near-miss** — recovered/ambiguous trajectories that a rule must not claim.
- **Staleness** — rules that become outdated as the codebase evolves.
- **Adversarial** — injection, poisoning, unsafe directives, leakage.
- **Reference** — success/failure references used by the replay pool; the pool is domain-scoped (#708) so a candidate is scored against references in its own domain.

## Custom Agent Adapter

### `@cauterule.watch` decorator

Wrap any agent function to auto-capture trajectories on failure:

```python
from cauterule.adapter import watch


@watch(domain="coding", severity="medium")
def my_agent(task: str) -> str:
    ...
    return result
```

On failure, the trajectory is captured, redacted, and saved to the corpus directory for extraction.

### `cauterule.inject()` context manager

Prep context with matching rules before task execution:

```python
from cauterule.adapter import inject
from cauterule.store.manager import StoreManager

with inject(
    task="deploy to production",
    rules=StoreManager().list_rules(status="active"),
    tool="bash",
) as ctx:
    rules_text = ctx.rules_prompt
    ...
```

### Framework adapters

`cauterule.adapter.langgraph`, `cauterule.adapter.crewai`, and
`cauterule.adapter.pydanticai` wrap their frameworks' failure/capture points and
use the same capture/inject contract. See [`docs/ADAPTERS.md`](docs/ADAPTERS.md).

## Adapter Conformance

Every adapter must satisfy the conformance kit (`tests/adapter_conformance/`),
which asserts:

- **fail-twice → extract → inject → no-repeat** — a repeated failure is
  prevented by the injected rule.
- **redaction-on-disk** — secrets in tool input/output are redacted in the
  persisted trajectory (both keyword and positional redaction paths).
- **success capture** — the success path writes a schema-valid trajectory.
- **schema validation** — written trajectories are enriched and conform to the
  corpus schema.

### Adding an adapter

1. Implement the adapter under `src/cauterule/adapter/<framework>.py` exposing
   the capture and injection entry points. Do not swallow exceptions silently;
   capture the failure path and surface errors through the configured logger.
2. Add a driver to `tests/adapter_conformance/conftest.py` and register it so
   the kit parametrizes over it.
3. Run `pytest tests/adapter_conformance/ -v`.
4. Add a focused integration test under `tests/adapter/` and document the
   adapter in `docs/ADAPTERS.md`.
5. Route all trajectory I/O through the shared redaction engine — never write
   raw capture output.

## Rule Pack Format

Rule packs are directories containing a `pack.yaml` manifest and rule YAML files:

```
pack-python/
├── pack.yaml          # manifest
├── py-import-error.yaml
└── ...
```

### `pack.yaml` fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | ✅ | Pack identifier (`pack-<topic>`) |
| `version` | ✅ | Semver; must increase monotonically on publish |
| `description` | ✅ | One-line summary |
| `author` | ✅ | Maintainer name |
| `rules` | ✅ | List of rule IDs included |
| `license` | ✅ | SPDX identifier (MIT) |
| `deps` | — | Dependent packs (resolved on install) |
| `cauterule` | — | Compatible Cauterule version |
| `checksum` | — | Content checksum for integrity |
| `created_with` | — | e.g. `cauterule 0.3.0` |
| `marketplace` | — | `categories`, `keywords` |
| `cert` | — | `required` (bool), `min_score` (0–1) |

### Contributing a Pack

1. Scaffold: `cauterule pack create <name>` (or add a directory under
   `rules/packs/`).
2. Author rules (see `rules/` for format examples). Prefer specific,
   non-destructive triggers; broad triggers fail certification.
3. Declare metadata and (if applicable) `deps` in `pack.yaml`.
4. Certify: `cauterule pack certify <pack-dir>`. Certification scores safety,
   replay, and provenance; official packs must meet the pack's `cert.min_score`.
5. Test: `pytest tests/packs/ -v` and `cauterule pack replay <pack-dir>`.
6. Submit a PR. Pack PRs require a passing certification report in the
   description and review of any broad-trigger waivers.

### Publishing and sharing

- `cauterule pack publish` — publishes with semver validation.
- `cauterule share <rule-id>` — shares a single rule as a GitHub gist with
  provenance.

## v0.3.0 Contribution Areas

### Adversarial Corpus Contribution

Adversarial test cases validate rule robustness. To contribute:

1. Create trajectories in `field-test/corpus/adversarial/<type>/` (or
   `corpus/public/adversarial/`).
2. Types: `staleness`, `counterexample`, `noise`, `prompt-injection`,
   `redaction-bypass`, `nearmiss-escalation`, `tool_output_injection`,
   `compounding_multiturn`, `unsafe_realistic`, `misleading_harmbench`,
   `contradiction_harmbench`.
3. Each trajectory must set `expected_outcome` (`should_reject` for attacks) and
   `expected_outcome_rationale`.
4. Run `pytest tests/adversarial/ -v` and `cauterule corpus validate <dir>`.

### Benchmark Contribution

1. Place benchmark corpus in `field-test/corpus/benchmark/`.
2. Add a benchmark under `tests/benchmark/` and register it so
   `cauterule benchmark list` shows it.
3. Benchmark types: determinism, acceptance, rejection, bake-off, mutation,
   calibration, ablation, latency, safety-ranking.

### Observability Plugin Contribution

1. Webhook: implement in `src/cauterule/integrations/webhook.py`.
2. OTEL: implement in `src/cauterule/integrations/otel.py`.
3. Add tests in `tests/observe/` / `tests/integrations/`.
4. Document configuration in `cauterule.toml` and `docs/observability.md`.

### CI

CI (`.github/workflows/ci.yaml`) runs on push/PR to `main`: `ruff check .`,
`mypy src/`, a field-test report drift check, and `pytest` with the coverage
gate. `.github/workflows/security-scan.yml` runs truffleHog, pip-audit, the
secret regex scan, and OpenSSF Scorecard. Run the same locally before pushing.