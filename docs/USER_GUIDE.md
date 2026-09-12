# CauterRule User Guide

## Overview

CauterRule extracts actionable standing rules from agent execution failures. The system captures a failure trajectory, extracts a candidate rule, replay-tests it against historical data, and stores it for future injection.

This guide covers:

- Running CauterRule with local or cloud LLMs
- Understanding the corpus structure
- Running field tests against any corpus
- Interpreting results
- Generating synthetic trajectories for testing

### Contents

- [Quick Start](#quick-start)
- [Extracting Rules from a Trajectory](#extracting-rules-from-a-trajectory)
- [Running Field Tests](#running-field-tests)
- [Output Structure](#output-structure)
- [Options](#options)
- [Generating Synthetic Trajectories](#generating-synthetic-trajectories)
- [Interpreting Results](#interpreting-results)
- [Examples](#examples)
- [Advanced: Multi-Pass Extraction](#advanced-multi-pass-extraction)
- [Corpus Structure Reference](#corpus-structure-reference)
- [File Format](#file-format)
- [Troubleshooting](#troubleshooting)
- [v0.2.0 Features](#v020-features)
- [v0.3.0 M4 — Rule Lifecycle & Framework Adapters](#v030-m4--rule-lifecycle--framework-adapters)
- [Rule Pack Ecosystem](#rule-pack-ecosystem)
- [Corpus Management](#corpus-management-cauterule-corpus)
- [Benchmarking](#benchmarking-cauterule-benchmark-cauterule-leaderboard)
- [Observability](#observability-cauterule-observe)
- [Configuration](#configuration-cauteruletoml)
- [Cost / Latency Tiering](#cost--latency-tiering)

---

## Quick Start

### Prerequisites

- Python 3.12+
- For local LLM: OMLX running at `http://localhost:8000/v1`
- For cloud LLM: OpenRouter or OpenAI API key

### Installation

```bash
git clone https://github.com/deghosal-2026/CauterRule.git
cd CauterRule
pip install -e .
```

### Run the Demo

```bash
cauterule demo --failures 1
```

---

## Extracting Rules from a Trajectory

### Single trajectory extraction

```bash
# With local OMLX
CAUTERULE_LLM_API_KEY=dummy \
cauterule extract field-test/corpus/golden/G-001-git-push-non-ff.jsonl \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1

# With cloud LLM via OpenRouter
CAUTERULE_LLM_API_KEY=sk-or-... \
cauterule extract field-test/corpus/golden/G-001-git-push-non-ff.jsonl \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1
```

### Dry-run extraction (no LLM call)

```bash
cauterule extract field-test/corpus/golden/G-001-git-push-non-ff.jsonl --dry-run
```

### Pre-extraction gate (silence on clean trajectories)

Before calling the LLM, `cauterule extract` runs a deterministic gate that checks the trajectory for failure evidence (exit codes, assertion failures, schema violations, step errors). If a successful trajectory has no failure signal, extraction is skipped — no LLM call, no candidate. This is reported as `silence` with reason `no_failure_signal`, which counts as a win on safety corpora.

Configure the gate in `cauterule.toml`:

```toml
[extraction]
gate_mode = "strict"  # strict (default) | relaxed
```

Use `relaxed` on positive corpora where extraction is always the goal.

---

## Running Field Tests

The field-test runner (`scripts/run-field-test.py`) runs extraction across entire corpora, replay-tests candidates against the full reference set, and produces incremental results.

### Corpus Types

| Type | Path | Trajectories | Purpose |
|---|---|---|---|
| `golden` | `field-test/corpus/golden/` | 10 | Regression anchor — expected rules known |
| `failures/positive` | `field-test/corpus/curated/failures/positive/` | 30 | Real failure trajectories that should produce rules |
| `failures/negative` | `field-test/corpus/curated/failures/negative/` | 10 | Failure traces that should NOT produce rules |
| `successes` | `field-test/corpus/curated/successes/` | 20 | Success trajectories — rules must not break them |
| `nearmiss` | `field-test/corpus/curated/nearmiss/` | 14 | Looks like a failure but should not trigger |
| `noisy` | `field-test/corpus/curated/noisy/` | 5 | Misleading/ambiguous traces — robustness test |
| `corrections` | `field-test/corpus/curated/corrections/` | 5 | Human-correction-to-rule flow |
| `raw/opencode` | `field-test/corpus/raw/opencode/` | 25 | Real OpenCode session trajectories |
| `raw/synthetic` | `field-test/corpus/raw/synthetic/` | 145 | Generated synthetic scenarios |
| `raw/ci` | `field-test/corpus/raw/ci/` | 110 | GitHub Actions CI failure logs |
| `raw/sibling-repos` | `field-test/corpus/raw/sibling-repos/` | 10 | Agent runs on sibling repos |
| `raw/corrections` | `field-test/corpus/raw/corrections/` | 5 | Manual correction transcripts |
| `raw/cross-session` | `field-test/corpus/raw/cross-session/` | 5 | Cross-session repeat failures |

### v0.2.0 Public Corpus

New in v0.2.0: a shareable public corpus under `corpus/public/` with trajectory metadata annotations, gold rule families, and adversarial/staleness test data.

| Type | Path | Trajectories | Purpose |
|------|------|-------------|---------|
| `golden` | `corpus/public/golden/` | 10 | Gold families — 10 scenarios × ≥2 acceptable rule abstractions each |
| `domain/coding` | `corpus/public/domains/coding.jsonl` | 10 | Coding-domain trajectories with known expected outcomes |
| `domain/devops` | `corpus/public/domains/devops.jsonl` | 10 | DevOps/K8s-domain trajectories |
| `domain/research` | `corpus/public/domains/research.jsonl` | 10 | Research/web-scrape-domain trajectories |
| `domain/support` | `corpus/public/domains/support.jsonl` | 10 | Support/triage-domain trajectories |
| `domain/browser` | `corpus/public/domains/browser_automation.jsonl` | 10 | Browser-automation-domain trajectories |
| `counterexample` | `corpus/public/counterexample/counterexample.jsonl` | 20 | Expected rejection — plausible but wrong |
| `nearmiss` | `corpus/public/nearmiss/nearmiss.jsonl` | 20 | Near-miss — looks like failure but isn't |
| `staleness` | `corpus/public/staleness/staleness.jsonl` | 10 | Historical failures no longer relevant |
| `synthetic` | `corpus/public/synthetic/synthetic.jsonl` | 50 | Shareable synthetic trajectories, no secrets |
| **Total** | | **160** | |

All public corpus trajectories include `expected_outcome` (`should_extract`, `should_silence`, `should_reject`) and `expected_outcome_rationale` metadata for automated ground-truth verification.

### With Local OMLX (Apple Silicon)

```bash
# Single corpus type
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0

# All curated corpus types
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py --all \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0
```

### With Cloud LLM (OpenRouter)

```bash
# Single corpus type
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0

# All 13 corpus types
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py --all \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0
```

### With Ollama (Local)

```bash
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider ollama --llm-model llama3 \
  --output-dir field-test/results/0.1.0
```

---

## Output Structure

Results are written to `{output-dir}/{corpus_type}/{llm_label}/{date}/`:

```
field-test/results/0.1.0/
  golden/
    omlx-openai-Llama-3.2-3B-Instruct-4bit/
      2026-09-06/
        meta.json         # run configuration
        results.jsonl     # per-trajectory results (appended live)
        summary.json      # aggregate metrics (rewritten live)
    openai-openai_gpt-4o-mini/
      2026-09-06/
        ...
  failures_positive/
    ...
```

### Results Format

Each line in `results.jsonl` is a JSON object with:

```json
{
  "trajectory_id": "G-001-git-push-non-ff",
  "status": "done",
  "candidate_count": 1,
  "candidates": [
    {
      "when": "when git push fails with non-fast-forward",
      "do": "pull latest changes before pushing",
      "confidence": 0.85,
      "extraction_pass": 1,
      "temperature": 0.2,
      "llm_response": "{\"when\": {\"trigger\": \"...\"}}"
    }
  ],
  "best": {
    "precision": 1.0,
    "recall": 0.05,
    "verdict": "pass"
  }
}
```

---

## Options

| Flag | Default | Description |
|---|---|---|
| `corpus_type` | — | `golden`, `failures/positive`, `failures/negative`, `successes`, `nearmiss`, `noisy`, `corrections`, `raw/opencode`, `raw/synthetic`, `raw/ci`, `raw/sibling-repos`, `raw/corrections`, `raw/cross-session` |
| `--all` | off | Run all corpus types |
| `--llm-provider` | `openai` | `openai`, `anthropic`, `ollama`, `litellm` |
| `--llm-model` | `gpt-4o-mini` | Model name |
| `--llm-base-url` | `""` | Base URL (OMLX: `http://localhost:8000/v1`, OpenRouter: `https://openrouter.ai/api/v1`) |
| `--output-dir` | `field-test/results/0.1.0` | Output directory |
| `--max-workers` | `4` | Parallel trajectories |
| `--temperatures` | `0.2,0.5` | Comma-separated temperatures |
| `CAUTERULE_LLM_API_KEY` | env var | API key for cloud LLMs |

---

## Generating Synthetic Trajectories

CauterRule includes a generator for creating synthetic trajectory corpora:

```bash
# Generate full corpus (200-250 trajectories)
python scripts/generate-corpus.py

# Dry-run: show counts without writing
python scripts/generate-corpus.py --dry-run

# Validate existing corpus
python scripts/generate-corpus.py --validate
```

The generator produces trajectories across domains:

- **git** — push, merge, rebase, detached HEAD, auth failures
- **python** — import errors, syntax errors, type errors, venv issues
- **docker** — build failures, port conflicts, OOM, missing dockerfiles
- **test** — assertion failures, timeouts, flaky tests
- **deploy** — health checks, image pull failures, configmap issues
- **env** — missing variables, wrong paths, permission denied
- **shell** — command not found, disk full, process killed
- **workflow** — wrong file targeting, stale assumptions, misleading errors
- **browser automation** — element not found, stale elements, timeouts
- **research** — API rate limits, timeouts, missing data

---

## Interpreting Results

### Verdict Meanings

| Verdict | Meaning |
|---|---|
| **pass** | Candidate would have prevented failures without breaking successes |
| **inconclusive** | No clear evidence either way — usually means the candidate is plausible but too broad |
| **fail** | Candidate would break successes or is too weak to prevent failures |

### Metrics

| Metric | Description |
|---|---|
| `candidates` | Number of extracted candidates from a trajectory |
| `precision` | Ratio of prevented failures to total triggered outcomes |
| `recall` | Ratio of prevented failures to total historical failures |
| `failures_prevented` | Trajectories where the candidate would have prevented a failure |
| `successes_broken` | Trajectories where the candidate would have broken a success |

---

## Examples

### Example 1: Basic Golden Set Evaluation

```bash
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0
```

### Example 2: Cloud Model Bake-off

```bash
# Run all 3 models on the same corpus
for MODEL in "openai/gpt-4o-mini" "meta-llama/llama-3.1-8b-instruct" "anthropic/claude-3.5-sonnet"; do
  CAUTERULE_LLM_API_KEY=sk-or-... \
  python scripts/run-field-test.py golden \
    --llm-provider openai --llm-model "$MODEL" \
    --llm-base-url https://openrouter.ai/api/v1 \
    --output-dir field-test/results/0.1.0
done
```

### Example 3: Safety-Corpus Focus

```bash
CAUTERULE_LLM_API_KEY=sk-or-... \
python scripts/run-field-test.py successes \
  --llm-provider openai --llm-model openai/gpt-4o-mini \
  --llm-base-url https://openrouter.ai/api/v1 \
  --output-dir field-test/results/0.1.0
```

### Example 4: Raw Corpus Breadth

```bash
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py raw/synthetic \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --output-dir field-test/results/0.1.0
```

### Example 5: Watch Progress Mid-Run

```bash
tail -f field-test/results/0.1.0/golden/omlx-openai-Llama-3.2-3B-Instruct-4bit/2026-09-06/summary.json
tail -f field-test/results/0.1.0/golden/omlx-openai-Llama-3.2-3B-Instruct-4bit/2026-09-06/results.jsonl
```

---

## Advanced: Multi-Pass Extraction

The runner supports multiple extraction passes at different temperatures:

```bash
CAUTERULE_LLM_API_KEY=dummy \
python scripts/run-field-test.py golden \
  --llm-provider openai --llm-model llama-3.2-3b-instruct \
  --llm-base-url http://localhost:8000/v1 \
  --temperatures 0.2,0.5,0.8 \
  --output-dir field-test/results/0.1.0
```

---

## Corpus Structure Reference

```
field-test/corpus/
├── README.md
├── catalog.yaml
├── golden/                    # 10 regression-anchor trajectories
├── curated/
│   ├── failures/positive/     # 30 failure trajectories
│   ├── failures/negative/     # 10 negative/control cases
│   ├── successes/             # 20 success trajectories
│   ├── nearmiss/              # 14 near-miss scenarios
│   ├── noisy/                 # 5 noisy/misleading trajectories
│   └── corrections/           # 5 human-correction examples
└── raw/
    ├── opencode/              # 25 real OpenCode sessions
    ├── synthetic/             # 145 generated scenarios
    ├── ci/                    # 110 CI failure logs
    ├── sibling-repos/         # 10 Cursor/Claude harness runs
    ├── corrections/           # 5 manual correction transcripts
    └── cross-session/         # 5 cross-session repeats
```

---

## File Format

### Trajectory JSONL (one JSON object per line)

```json
{
  "trajectory_id": "G-001-git-push-non-ff",
  "timestamp": "2026-09-06T00:00:00Z",
  "task": "Push local feature branch commits to remote main",
  "domain": "git",
  "failure_class": "git/push/non-fast-forward",
  "quality_label": "clear",
  "severity": "high",
  "success": false,
  "failure_point": "! [rejected] non-fast-forward",
  "steps": [
    {
      "step_number": 1,
      "tool": "git",
      "input": "git add . && git commit -m 'update'",
      "output": "1 file changed",
      "error": null
    },
    {
      "step_number": 2,
      "tool": "git",
      "input": "git push origin main",
      "output": null,
      "error": "! [rejected] non-fast-forward"
    }
  ],
  "tags": ["git", "push"],
  "source": "opencode",
  "source_repo": "CauterRule",
  "redacted": false
}
```

---

## Troubleshooting

### "Missing Authentication header" (401)

Your `CAUTERULE_LLM_API_KEY` is not set or is invalid. For OMLX, set it to any dummy value:

```bash
export CAUTERULE_LLM_API_KEY=dummy
```

### No endpoints found (404)

The model is not available on your OpenRouter tier. Try a different model:

```bash
# Try these instead
--llm-model openai/gpt-4o-mini
--llm-model meta-llama/llama-3.1-8b-instruct
```

### "No balanced JSON object found"

The LLM returned non-JSON output. This is a model quality issue. Try:
- Using a stronger model
- Adding `--temperatures 0.2` (lower temperature)
- Checking the `llm_response` field in results for debugging

### Results file is empty after rerun

The runner now clears `results.jsonl` at the start of each run. If you rerun on the same day, the previous results are cleared. Use a different output directory or rename the old results.

### Slow extraction

- Reduce `--max-workers` if your LLM provider rate-limits you
- Use a smaller corpus type
- Use a local model instead of cloud
- Set `--temperatures 0.2` (single pass instead of multiple)

---

## v0.2.0 Features

### TUI Review Interface (`cauterule review`)

Review candidate rules before promotion using a terminal UI:

```bash
cauterule review
```

The TUI presents a confidence-ordered queue — highest-impact candidates first. You can:

- Filter by severity, origin, or status
- Approve or reject rules with keyboard shortcuts
- View rule details, trigger specificity, and replay evidence inline
- Navigate with card-based pagination

### Observability (`cauterule observe`)

Track rule health and coverage over time:

```bash
cauterule observe          # show hit counters and coverage scores
cauterule metrics          # detailed metrics report
```

Metrics include:

- **Hit counters** — how often each rule fires during injection
- **Coverage scoring** — which failure classes are covered by active rules
- **Learning journal** — narrative view of rule evolution over time

### Safety-Adjusted Ranking (`cauterule report`)

Generate safety-adjusted model rankings from field-test results:

```bash
cauterule report --safety-adjusted
```

Produces a markdown table ranking models by safety-adjusted pass rate, with:

- Broad-trigger penalty — rules that break successes are penalized
- Violation rate — percentage of rules that violate safety constraints
- Decision economics — pairwise model comparison with wrong-decision rate

### Pre-Extraction Gate

The pre-extraction gate prevents extraction from clean (no-failure) trajectories:

```bash
cauterule preflight --corpus corpus/public/golden/
```

Validates:

- Corpus annotations (`expected_outcome`, `expected_outcome_rationale`)
- Corpus sizes and schema (`CORPUS_SCHEMA_VERSION`)
- Output-directory writability/space
- Provider reachability (unless `--no-probe`)
- Trajectory structure before extraction runs

Check harness health after a run with the parse-rate / completion-ratio gate:

```bash
cauterule harness-health --parsed 38 --total 40 --candidates 41 --threshold 0.7
```

`--parsed` and `--total` are required; the command warns when the parse rate
falls below `--threshold` or the candidate/trajectory completion ratio is
unhealthy.

### Adversarial Testing

Six adversarial corpora test rule robustness:

| Corpus | What It Tests |
|--------|---------------|
| `adversarial/staleness` | Rules that become outdated as codebases evolve |
| `adversarial/counterexample` | Cases where a correct rule produces wrong prevention |
| `adversarial/noise` | Rule resilience to noisy/irrelevant trajectory content |
| `adversarial/prompt-injection` | Rules that prevent vs. are exploited by injection attacks |
| `adversarial/redaction-bypass` | Whether rules leak or circumvent secret redaction |
| `adversarial/nearmiss-escalation` | Edge cases where near-misses should escalate |

Run against any adversarial corpus:

```bash
cauterule extract field-test/corpus/adversarial/prompt-injection/*.jsonl
cauterule test --corpus adversarial
```

### Distribution

- **Docker:** `docker compose up cauterule-demo`
- **Standalone binary:** `scripts/build_binary.sh`
- **GitHub Action:** run `cauterule test --ci` in any CI workflow
- **Webhook:** configure promotion webhook in `cauterule.toml`
- **OpenTelemetry:** emit traces and metrics to any OTEL collector

---

## v0.3.0 M4 — Rule Lifecycle & Framework Adapters

The rule store is now a self-maintaining asset.  See
[`docs/ADAPTERS.md`](ADAPTERS.md) for the full adapter + conformance
reference; the lifecycle policies are summarized below.

### Rule lifecycle configuration (`cauterule.toml`)

```toml
[retirement]          # #543 — auto-retirement policy
harmful_window = 20   # trailing outcomes examined
harmful_ratio = 0.5   # broke/(broke+prevented) above this → candidate
stale_days = 90       # idle for this long → stale candidate
stale_specificity = 0.3  # + specificity below this → stale candidate
min_evidence = 5      # never retire on fewer than N outcomes
dry_run = true        # default: `audit` reports, does not mutate

[promotion]           # #545 — auto-promotion tuning guardrails
min_evidence = 30     # outcomes before learned cutoffs activate
target_prevented_rate = 0.8
floor_min_quality = 0.4
ceiling_min_quality = 0.95
floor_min_specificity = 0.1
ceiling_min_specificity = 0.9
```

### Per-rule lifecycle CLI

```bash
cauterule metrics --rule R-001         # outcome counts + trend sparkline
cauterule show R-001 --outcomes        # same, per rule
cauterule list --sort spec             # include/sort by specificity
cauterule metrics --lowest-spec        # lowest-specificity rules (broad < 0.3)
cauterule audit                        # retirement candidates (dry-run)
cauterule audit --apply --yes          # retire them
cauterule retire R-001 --reason "superseded by R-042"
cauterule show R-001 --history         # supersession chain v1→v2→v3
cauterule health                       # store health incl. supersession
cauterule promote --show-cutoffs       # learned vs default cutoffs
```

Outcome tracking stores `prevented` / `broke` / `neutral` counts per rule in an
append-only log, so replay-cache hits do not double-count.  Malformed rule files
are automatically moved to `<rules>/.quarantine/` (with an index of the failure
reason) instead of aborting the store load.

### Framework adapters

Four adapters capture failures (as trajectories) and inject matching standing
rules using the real matcher + budget.  Every adapter passes the shared
conformance suite in `tests/adapter_conformance/`.

| Adapter | Capture | Injection |
|---|---|---|
| Generic (`@watch`) | per call (sync/async/gen) | `inject()` / `ainject()` |
| LangGraph | per failed node | `inject_rules(state)` |
| CrewAI | per task (wrapper or callbacks) | `inject_crew_rules(...)` |
| PydanticAI | per `Agent.run()` | `inject_system_rules(...)` |

```bash
cauterule init --dir proj --adapter langgraph   # | crewai | pydanticai | custom
```

Generic custom loop:

```python
from cauterule.adapter import watch, inject
from cauterule.store.manager import StoreManager

@watch(base_dir="trajectories", redact_keys={"api_key", "token"})
def my_agent(prompt: str) -> str: ...

with inject(task, rules=StoreManager().list_rules(status="active"), tool="git", error="...") as matched:
    prompt = base + render(matched)
```

LangGraph, CrewAI, and PydanticAI follow the same capture/inject contract with
framework-native entry points.  See [`docs/ADAPTERS.md`](ADAPTERS.md) for the
full hookup examples, capture/injection semantics, redaction behavior, and the
conformance contract.

---

## Rule Pack Ecosystem

Turn the rule store into a library: install community packs, scaffold your
own, publish releases, or share a single rule as a gist.  To author and submit
an official pack, see [`docs/packs/CONTRIBUTING-PACKS.md`](packs/CONTRIBUTING-PACKS.md).

### Official packs

| Pack | Covers | Install |
|---|---|---|
| `pack-git` | push/merge/rebase/conflicts/hooks | bundled |
| `pack-docker` | builds, compose, networking, volumes, registries | `cauterule pack install <repo>@<version>` |
| `pack-deploy` | k8s, rollout/rollback, CI/CD, secrets (deps: `pack-docker`) | same (pulls `pack-docker`) |
| `pack-testing` | flaky tests, coverage, mocks, snapshots, async | same |
| `pack-python` | imports, venvs, pip resolver, installs | same |

### Install / create / publish / share

```bash
cauterule pack install acme/pack-docker@v1.2.0   # GitHub release asset
cauterule pack install pack-docker@1.2.0         # shorthand via registry
cauterule pack install ./local-pack              # local dir or .tar.gz (air-gapped)
cauterule pack install <gist-url>                # single shared rule
cauterule pack install acme/pack-docker --offline --store ./rules
cauterule pack install acme/pack-docker --skip-cert   # CI escape hatch only

cauterule pack create pack-acme --from-tag docker/ --description "..." --author "You"
cauterule pack publish --dry-run                 # validate + cert + asset preview
cauterule pack publish --bump minor              # tag pack-<name>-vX.Y.Z + release
cauterule share R-001                            # secret gist + PROVENANCE.json
cauterule share R-001 --public --yes

cauterule pack list                              # installed packs
cauterule pack info pack-docker                  # version, deps, cert, safety score
cauterule pack info pack-docker --json           # machine-readable
cauterule pack tree pack-deploy                  # resolved dep tree from lockfile
cauterule test --pack pack-docker                # replay every rule in the pack
```

### Semver policy for packs

- `major`: rule removals, trigger narrowing, manifest format change.
- `minor`: new rules, new optional deps.
- `patch`: rule text / metadata fixes.
- `publish --bump` suggests the kind from the rule-list diff (warn-only).

### Dependency syntax (`pack.yaml` deps)

```yaml
deps:
  - pack-docker >=1.0.0,<2.0.0
  - pack-testing ^0.4.0
```

Resolution is recorded in `packs.lock.yaml`. Cycles and conflicts fail with
an actionable error naming both requirers. Prereleases (`-rc.N`) never
satisfy unpinned installs — pin them exactly.

### Certification and safety scores

Every install and publish runs `certify_pack()` (manifest, replay evidence,
provenance) plus a 0–100 safety score (unsafe-directive scan,
broad-trigger penalty). Below the threshold the operation is blocked:

```toml
[packs]
min_safety_score = 70
```

Precedence: `--min-safety-score` flag > `cauterule.toml` > 70.
`pack info` prints the cert status, score, and which rules drag it.

### Share vs publish: which one?

| Situation | Command |
|---|---|
| One rule to a teammate for review | `cauterule share R-001` (secret gist) |
| Versioned pack for the world | `cauterule pack publish` (GitHub release) |
| Air-gapped / local testing | `pack install ./path` + `pack create` |

### Failure taxonomy, observability, badges, webhooks

```bash
cauterule list --taxonomy git/push           # filter by category
cauterule health --by-taxonomy               # precision per category
cauterule taxonomy backfill --dry-run        # classify untagged store rules

cauterule observe                            # summary: learned, verdicts, gaps
cauterule observe --since 7d --json          # period filter, machine output
cauterule observe journal|metrics|frontier|gaps

cauterule badge --svg                        # cauterule-badge.svg
cauterule badge --json                       # shields.io endpoint schema
cauterule badge --url                        # embed URL for README
```

```toml
[webhook]
enabled = true
provider = "slack"   # slack | discord | github | custom
url = "https://hooks.slack.com/..."
on_events = ["promote"]
```

Promotion fires the webhook with retry + backoff (no retry on 4xx),
secret redaction, and the SSRF guard. `cauterule webhook test` dry-runs
delivery against a mock endpoint.

---

## Corpus Management (`cauterule corpus`)

Manage the trajectory corpus as a first-class asset — add, validate, lint,
consolidate, list, and export.

```bash
cauterule corpus list                                  # files + trajectory counts
cauterule corpus add path/to/trajs.jsonl --domain coding --tags "ci,deploy"
cauterule corpus validate corpus/public/golden/        # schema-check (Trajectory parsing)
cauterule corpus lint corpus/public/                    # required annotation fields + provenance
cauterule corpus build --output corpus/index.jsonl     # consolidate into one indexed store
cauterule corpus export --format csv --output out.csv  # export (jsonl|csv), optional --domain
```

`lint` enforces the required annotation fields (`expected_outcome`,
`expected_outcome_rationale`) and style/provenance rules; `build` produces a
single indexed file that downstream runners can load directly.

---

## Benchmarking (`cauterule benchmark`, `cauterule leaderboard`)

Run the extraction/replay/injection hot-path benchmarks and track regressions.

```bash
cauterule benchmark list                       # available benchmarks
cauterule benchmark run extraction             # one hot path
cauterule benchmark run --all                  # full suite
cauterule benchmark run extraction --compare baseline.json   # delta vs baseline
```

Available benchmarks: `extraction`, `replay_matcher`, `injection_budget`,
`conflict_consolidation`, `observe_coverage`.  These back the pytest-benchmark
performance-regression CI gate.

`leaderboard` surfaces which failure patterns rules actually prevent, and the
biggest uncovered gaps:

```bash
cauterule leaderboard --top 20
cauterule leaderboard --store-dir ./rules --top 10
```

---

## Observability (`cauterule observe`)

`observe` gives a single summary plus drill-downs over the learning journal and
rule-health metrics.

```bash
cauterule observe                     # summary: learned, verdicts, gaps
cauterule observe --since 7d --json   # period filter, machine output
cauterule observe journal             # failure → rule → replay → promotion narrative
cauterule observe metrics             # rules, precision, repeat-failure rate, store size
cauterule observe frontier            # next most valuable domain/failure family to learn
cauterule observe gaps                # uncovered failure classes
```

The learning **journal** renders each candidate's trajectory:
failure → extracted rule → replay evidence → promotion decision.  **metrics**
tracks hit counters, coverage scoring, and repeat-failure rate.  See
[`docs/observability.md`](observability.md) for the metric definitions.

---

## Configuration (`cauterule.toml`)

View or edit configuration from the CLI:

```bash
cauterule config --show
cauterule config --set llm.model=openai/gpt-4o-mini
```

Environment variables override file values:

| Variable | Purpose |
|---|---|
| `CAUTERULE_LLM_PROVIDER` | `openai`, `anthropic`, `ollama`, `litellm` |
| `CAUTERULE_MODEL` | Model name (alias: `CAUTERULE_LLM_MODEL`) |
| `CAUTERULE_LLM_API_KEY` | API key for cloud LLMs |
| `CAUTERULE_LLM_BASE_URL` | Provider base URL (OMLX / OpenRouter) |
| `CAUTERULE_SEMANTIC_MATCHING` | `1` enables optional embedding-based paraphrase matching |

### Custom redaction patterns

Add project-specific secret patterns under `[redaction]`; they are applied by
`redact_trajectory` in addition to the built-in Slack / Stripe / private-key /
high-entropy / generic-API-key patterns:

```toml
[redaction]
patterns = [
  "ACME-[A-Za-z0-9]{32}",
  "internal://[^\\s]+",
]
```

### Semantic matching (optional)

The default matcher is lexical (substring + token overlap).  To enable local
sentence-embedding similarity for paraphrase matching:

```bash
pip install "cauterule[matching]"
export CAUTERULE_SEMANTIC_MATCHING=1
```

This loads a small CPU-friendly model (`all-MiniLM-L6-v2`) on first match.  When
disabled or unavailable, matching silently falls back to the lexical score.

---

## Cost / Latency Tiering

Cauterule's extraction economics are explicit. Use the right tier for the job.

### Tier strategy

| Tier | Models | When to use | Approx $/1k trajs |
|------|--------|-------------|---------------------|
| **Local** | Llama-3.2-3B, Qwen3-4B (OMLX) | Iteration, regression sweeps, pre-commit | ~$0 (infra-only) |
| **Cheap cloud** | gpt-4o-mini, Claude-3-Haiku | PR/release gate, nightly CI | $0.40 – $0.50 |
| **Flagship** | gpt-4o, Claude-3-Opus | Calibration, disputed cases, monthly bake-off | $5.00 – $15.00 |

Decision rule: **use local unless** you need cloud quality for a release gate
or the extractor is over-triggering on a new corpus (flagship calibration).

### Preflight cost estimate

```bash
cauterule preflight --corpus corpus/public/golden/ --max-cost 5.00
cauterule preflight --cost-table          # print the full $/1k model table
```

`--max-cost` fails the preflight when the estimate exceeds the cap. The table
covers all known models with $/1k trajectories, p95 latency, and tier.

### Plan thresholds

| Metric | Target |
|--------|--------|
| CLI latency | < 500ms |
| Preflight | < 30s |
| Demo (full loop) | < 60s |

These are asserted in preflight when a probe is available; otherwise they are
re-baselined with justification in the field-test report.
