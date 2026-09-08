# Corpus Contribution Guide

Thank you for contributing trajectories to the CauterRule benchmark corpus!

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/deghosal-2026/CauterRule.git
cd CauterRule

# 2. Create a trajectory JSONL
cat > my-trajectory.jsonl << 'EOF'
{"trajectory_id": "contrib-001", "timestamp": "2026-09-07T00:00:00Z", "task": "Git push fails due to non-fast-forward", "steps": [{"step_number": 1, "tool": "bash", "input": "git push origin main", "error": "! [rejected] non-fast-forward"}], "success": false, "domain": "git", "quality_label": "clear", "tags": ["git", "push"], "failure_point": "step1", "failure_class": "git/push/non-fast-forward", "expected_outcome": "should_extract", "expected_outcome_rationale": "Clear failure pattern with resolution"}
EOF

# 3. Validate
pip install -e .
cauterule validate  # checks rule store integrity
python -m pytest tests/corpus/test_field_test_metadata.py -v
```

## Trajectory Requirements

Every trajectory JSONL record **must** include these fields (see `docs/corpus/format-spec.md` for full schema):

| Field | Type | Example | Required |
|-------|------|---------|----------|
| `trajectory_id` | string | `"contrib-001"` | ✓ |
| `timestamp` | string (ISO 8601) | `"2026-09-07T00:00:00Z"` | ✓ |
| `task` | string | `"Git push fails due to..."` | ✓ |
| `steps` | list of Step objects | `[{"step_number":1, "tool":"bash", ...}]` | ✓ |
| `success` | bool | `false` | ✓ |
| `domain` | string | `"git"`, `"python"`, `"docker"`, etc. | ✓ |
| `quality_label` | string | `"clear"`, `"ambiguous"`, `"multi-causal"`, `"misleading"`, `"open-ended"` | ✓ |
| `tags` | list of strings | `["git", "push", "rebase"]` | ✓ |
| `failure_point` | string or null | `"step_1"` | ✓ (unless `success=true`) |
| `failure_class` | string or null | `"git/push/non-fast-forward"` | ✓ (unless `success=true`) |
| `expected_outcome` | string | `"should_extract"`, `"should_silence"`, `"should_reject"` | ✓ |
| `expected_outcome_rationale` | string | `"Clear failure pattern with resolution"` | ✓ |

## Expected Outcome Semantics

| Value | When to use |
|-------|-------------|
| `should_extract` | Clear failure pattern — a standing rule should be promoted |
| `should_silence` | Clean success or noise — no candidate should be produced |
| `should_reject` | Plausible-but-wrong pattern — extraction might produce a candidate, but it should be rejected by the gate or human review |

## Quality Labels

| Label | Meaning |
|-------|---------|
| `clear` | Single cause, unambiguous failure signal |
| `ambiguous` | Multiple possible causes or unclear failure signal |
| `multi-causal` | Failure resulted from interacting causes |
| `misleading` | Looks like one failure class but is actually another |
| `open-ended` | No clear right/wrong outcome |

## Naming Conventions

- **Gold scenarios:** `G-NNN-name.jsonl` (and `G-NNN-name-{a,b,...}.yaml` rule sidecars)
- **Counterexamples:** `counterex-NNN.jsonl`
- **Near-miss:** `nearmiss-NNN.jsonl`
- **Staleness:** `stale-NNN.jsonl`
- **Synthetic:** `synth-NNN.jsonl`
- **Raw CI:** `<tool>-<ci-run-id>.jsonl`
- **Raw sibling-repos:** `<agent>-NNN-description.jsonl`

## Private Data

- **Never** include real API keys, passwords, or personal data.
- Set `redacted: true` if you have scrubbed sensitive information.
- The `PrivateCorpus` class (`src/cauterule/corpus/private.py`) provides a local-only mode that never uploads data.

## Testing

After adding your trajectory:

```bash
# Validate metadata completeness
python -m pytest tests/corpus/test_field_test_metadata.py -v

# Run all corpus tests
python -m pytest tests/corpus -v

# Run full regression (no LLM)
python -m pytest tests/ -k "not slow and not docker" -v
```

Submit a PR to `corpus/public/` or `field-test/corpus/curated/` depending on whether the trajectory is benchmark-grade (curated) or exploratory (field-test).