# Corpus Contribution Guide

Thank you for contributing trajectories to the CauterRule benchmark corpus!

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/deghosal-2026/CauterRule.git
cd CauterRule

# 2. Create a trajectory JSONL
cat > my-trajectory.jsonl << 'EOF'
{"trajectory_id": "contrib-001", "timestamp": "2026-09-07T00:00:00Z", "task": "Git push fails due to non-fast-forward", "steps": [{"step_number": 1, "tool": "bash", "input": "git push origin main", "error": "! [rejected] non-fast-forward"}], "success": false, "domain": "git", "quality_label": "clear", "tags": ["git", "push"], "failure_point": "step1", "failure_class": "git/push/non-fast-forward", "severity": "medium", "expected_outcome": "should_extract", "expected_outcome_rationale": "Clear failure pattern with resolution"}
EOF

# 3. Validate (schema + annotations + provenance)
pip install -e .
cauterule corpus validate my-trajectory.jsonl
cauterule corpus lint my-trajectory.jsonl
cauterule preflight my-trajectory.jsonl   # full check, incl. schema_version
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
| `severity` | string or null | `"low"`, `"medium"`, `"high"` | ✓ (unless `success=true`) |
| `expected_outcome` | string | `"should_extract"`, `"should_silence"`, `"should_reject"` | ✓ |
| `expected_outcome_rationale` | string | `"Clear failure pattern with resolution"` | ✓ |
| `schema_version` | string | `"1.0"` | no (absent = 1.0) |

## Schema Version

The schema constant is `cauterule.corpus.format.CORPUS_SCHEMA_VERSION = "1.0"`.
`cauterule preflight` enforces it: an absent/empty `schema_version` is accepted
(defaults to `1.0`), and any other value fails with
`Unknown or incompatible schema_version: ... Expected: 1.0`. Bump the constant
and the docs together if the format ever changes.

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

## Corpus CLI

`cauterule corpus` manages `corpus/public/`:

```bash
cauterule corpus add ./trajs --domain git --tags ci,rebase   # ingest a file or directory
cauterule corpus list [--domain git] [--format table|json]   # counts per file
cauterule corpus validate [FILES...]                         # Trajectory parsing
cauterule corpus lint [FILES...]                             # failure_class/quality_label/domain
cauterule corpus build --output corpus/store.jsonl           # consolidate + index
cauterule corpus export --format jsonl|csv [--domain git]    # export entries
```

Use `cauterule preflight <corpus>` for the full gate (required fields, duplicate
IDs, `schema_version`, and `expected_outcome` on raw corpora).

## Domain-Scoped Reference Pool

Replay scoring (v0.3.0, #708) scopes the reference pool to the source
trajectory's `domain` when that slice has at least 3 reference trajectories,
falling back to the full pool otherwise. Land your trajectories under the
correct `domain` so domain-scoped scoring works; the v0.3.0 field test uses a
444-trajectory domain-scoped pool across 40 corpora.

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
