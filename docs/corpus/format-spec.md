# CauterRule Corpus Format Specification

**Version:** 1.0
**Schema constant:** `cauterule.corpus.format.CORPUS_SCHEMA_VERSION = "1.0"`

Each record may carry an optional `schema_version` string. It is **enforced by
`cauterule preflight <corpus>`**: an absent or empty value is accepted
(defaults to `1.0`), while any value other than `"1.0"` fails the
`schema_version` check with `Expected: 1.0`. The field is not required by
`cauterule corpus validate` / `lint`, which rely on `Trajectory` parsing.

## 1. File Format

Every corpus is a directory of **JSONL** files (one JSON object per line, newline-delimited). A corpus may optionally include a `catalog.yaml` or sidecar YAML rule files.

## 2. Trajectory Record

Each line is a JSON object describing one agent trajectory. Required and optional fields:

### 2.1 Identity

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trajectory_id` | string | yes | Unique identifier, e.g. `G-001-git-push-non-ff` |
| `timestamp` | string (ISO 8601) | yes | When the trajectory was captured |
| `schema_version` | string | no | Format version; `"1.0"` (enforced by preflight, absent = 1.0) |

### 2.2 Core

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task` | string | yes | Natural-language task description |
| `steps` | list of Step objects | yes | Ordered agent actions (see §2.5) |
| `success` | bool | yes | Whether the task ultimately succeeded |

### 2.3 Metadata

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | yes | Functional domain: `coding`, `devops`, `research`, `support`, `browser_automation` |
| `quality_label` | string | yes | `clear`, `ambiguous`, `multi-causal`, `misleading`, `open-ended`, `unlabeled` |
| `tags` | list of strings | yes | Arbitrary tags for filtering (e.g. `["git", "push"]`) |
| `tier` | string | no | `tiny`, `small`, `medium`, `large` — corpus size tier |
| `severity` | string or null | no | Failure severity: `low`, `medium`, `high`, `critical` |
| `redacted` | bool | no | Whether secrets/identifiers have been removed |
| `expected_rule` | string or null | no | Text of the expected rule for this trajectory |
| `expected_abstractions` | list of strings | no | Multiple acceptable rule abstractions for gold-family testing |
| `source` | string or null | no | Origin of the trajectory (e.g. `ci`, `synthetic`, `human-crafted`) |
| `source_repo` | string or null | no | For CI corpora, the repository slug |
| `human_correction` | string or null | no | Manual correction applied to the trajectory |

### 2.4 Failure Analysis

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `failure_point` | string or null | yes* | Description of where the failure occurred (nullable if `success=true`) |
| `failure_class` | string or null | yes* | Taxonomic failure class (nullable if `success=true`) |
| `notes` | string or null | no | Free-form analysis notes |

*May be `null` when `success` is `true`.

### 2.5 Annotation (for Replay Ground Truth)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `expected_outcome` | string | yes | `should_extract`, `should_silence`, `should_reject` |
| `expected_outcome_rationale` | string or null | yes | Explanation of why this outcome is correct |
| `expected_outcome_confidence` | string or null | no | `high`, `medium`, `low` |

Annotations are mandatory: `cauterule preflight` requires `expected_outcome`
on every raw corpus (`raw/ci`, `raw/opencode`, `raw/synthetic`,
`raw/sibling-repos`, `raw/corrections`, `raw/cross-session`) and
`cauterule corpus lint` flags records missing the required provenance fields
(`failure_class`, `quality_label`, `domain`). `validate_annotations()` in
`cauterule.corpus.validation` reports trajectories missing `expected_outcome`.

### 2.6 Step Object

Each element in `steps` is a JSON object:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `step_number` | int | yes | 1-based step order |
| `tool` | string | yes | Tool invoked (e.g. `bash`, `edit`, `read`, `web_fetch`) |
| `input` | string or null | no | Tool input |
| `output` | string or null | no | Tool output |
| `error` | string or null | no | Error message if step failed |
| `state` | dict or null | no | Agent state snapshot at this step |

### 2.7 Environment (optional)

| Field | Type | Description |
|-------|------|-------------|
| `os` | string | Operating system |
| `ci` | bool | Whether running in CI |
| `shell` | string or null | Shell type |

### 2.8 Agent Config (optional)

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | LLM model identifier |
| `tools` | list of strings | Tools available to the agent |

## 3. Corpus Metadata (Per-Directory)

Each corpus directory may include a `catalog.yaml` or `metadata.json`:

```yaml
id: golden
tier: small
domain: coding
quality_label: clear
trajectory_count: 12
gold_rule_ids:
  - G-001
  - G-002
```

## 4. Gold Rule Families

Gold scenarios live in `golden/` subdirectories. Each scenario has:

- `G-XXX-name.jsonl` — trajectory JSONL
- `G-XXX-name-a.yaml` — first acceptable rule abstraction
- `G-XXX-name-b.yaml` — second acceptable rule abstraction (≥2 required)

The rule YAML files use the standard `StandingRule` format (see `docs/design/standing-rule-format-design.md`).

## 5. Expected Outcome Semantics

| `expected_outcome` | Meaning |
|--------------------|---------|
| `should_extract` | The trajectory contains a clear failure pattern that should produce a promoted rule |
| `should_silence` | The trajectory has no failure signal; extraction should produce no candidate |
| `should_reject` | The trajectory has a plausible-but-wrong pattern; extraction may produce a candidate but it should be rejected by the gate or human review |

## 6. Validation

Use the `cauterule corpus` CLI and `src/cauterule/corpus/validation.py`:

```bash
cauterule corpus validate [FILES...]   # Schema-check files (Trajectory parsing)
cauterule corpus lint [FILES...]       # Required annotation/provenance fields
cauterule preflight <corpus.jsonl>     # Full checks incl. schema_version enforcement
```

- `validate_corpus_sizes()` — minimum trajectory counts per safety corpus
  (`successes`, `failures/negative`, `nearmiss`; default 50 each).
- `validate_annotations()` — 0 missing `expected_outcome` on annotated corpora.

## 7. Domain-Scoped Reference Pool

During replay scoring, candidates are scored against a reference pool. As of
v0.3.0 (#708) the pool is **scoped to the source trajectory's `domain`** when
that domain slice has at least 3 reference trajectories; otherwise it falls
back to the full pool so a tiny slice cannot inflate recall. The scorer also
excludes the source trajectory from its own reference set and records
`domain_scoped` plus `reference_pool_size` in the evidence report. The v0.3.0
field test uses a 444-trajectory domain-scoped pool across 40 corpora, which
lifted golden recall 2–3×.

See `scripts/run-field-test.py` and
[`docs/field-test/v0.3.0/FIELD_TEST_REPORT.md`](../field-test/v0.3.0/FIELD_TEST_REPORT.md).