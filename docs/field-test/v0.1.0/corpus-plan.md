# Corpus Acquisition Plan — CauterRule v0.1.0 Field Test

**Date:** 2026-09-05
**Milestone:** M30 — Comprehensive Field Test
**Status:** Living document — update as corpus grows

---

## 1. Why We Need Real Corpus

The existing test fixtures in `tests/fixtures/trajectories/` are synthetic. They are useful for unit tests but not sufficient for field testing. Real field tests require trajectories from actual agent work — real tasks, real failures, real corrections.

This document defines what corpus we need, where to get it, how to collect it, and how to organize it.

---

## 2. Corpus Sources

### 2.1 Source Priority

| Priority | Source | Type | Estimated Yield | Collection Method |
|----------|--------|------|----------------|------------------|
| P1 | OpenCode sessions on CauterRule repo | Failure + success | 20-30 trajectories | Export from session history, extract failures + corrections |
| P2 | GitHub Actions CI logs from CauterRule repo | Failure | 10-20 trajectories | Download CI run logs, extract failure steps |
| P3 | Agent runs on sibling repos (AgentSelfEdit, PlannerCritic, ToolTrust) | Failure + success + correction | 15-25 trajectories | Run toy agent tasks, capture via @cauterule.watch |
| P4 | Manual correction transcripts | Correction | 5-10 examples | Collect instances where user said "next time do X" |
| P5 | Cross-session repeat failures | Failure | 5-10 trajectories | Identify same failure appearing across different days/repos |

### 2.2 What Each Source Contributes

| Source | Failure Types | Why It Matters |
|--------|---------------|----------------|
| OpenCode sessions | Git, Python, Docker, workflow, verification | Matches real usage. These are the actual failures the user encountered while building CauterRule itself |
| GitHub Actions CI | Lint, mypy, pytest, packaging, Docker | High-value for deterministic replay. CI failures are clean, structured, and reproducible |
| Sibling repos | Same categories but different context | Tests rule transferability across repos. Rules learned in one repo should help in another |
| Manual corrections | Any domain | Highest-value for human-correction feature. These are real "why didn't you just X" moments |
| Cross-session repeats | Any recurring type | Most valuable for measuring repeat-failure reduction. If it happened twice, it will happen again |

### 2.3 Real Corpus Spread Target

This is the concrete target spread for the first real field-test corpus. The goal is not just volume, but balanced representation of the failure modes CauterRule is expected to learn from.

| Bucket | Target Count | Primary Source | Secondary Source | Why It Matters |
|--------|--------------|----------------|------------------|----------------|
| Git failures | 8 | OpenCode sessions | Manual corrections | High recurrence, clear reusable lessons |
| Python/runtime failures | 6 | OpenCode sessions | Sibling repo runs | Common coding-agent mistakes |
| Docker/build failures | 4 | CI logs | OpenCode sessions | Strong field relevance for deployment workflows |
| Test/CI failures | 4 | GitHub Actions CI | Sibling repo runs | Deterministic and easy to replay |
| Deploy/env/shell failures | 3 | OpenCode sessions | Corrections | Important operational rules |
| Workflow/agent-process failures | 3 | OpenCode sessions | Corrections | Valuable for OpenCode-specific behavioral rules |
| Success trajectories | 20 | OpenCode sessions | Sibling repo runs | Needed to measure regressions and broken successes |
| Near-miss trajectories | 10 | Derived from failures | Public synthetic corpus | Needed for precision and trigger specificity |
| Noisy/misleading trajectories | 5 | Derived from failures | OpenCode sessions | Tests robustness of extraction |
| Human-correction examples | 5 | Corrections | OpenCode sessions | Tests correction-to-rule flow |
| Golden trajectories | 10 | Best curated failures | N/A | Regression anchor across versions |

### 2.4 Real Corpus Source Map

This is the recommended mapping from real sources to corpus buckets.

| Source | Raw Trajectory Target | Best For | Notes |
|--------|------------------------|---------|-------|
| OpenCode sessions on CauterRule | 25-30 | Git, Python, Docker, workflow, verification failures; success trajectories | Highest-value source because it matches actual user workflow |
| GitHub Actions / CI logs | 10-15 | Test, lint, mypy, packaging, Docker, build failures | Clean and reproducible; ideal for replay and regression |
| Sibling repo agent runs | 15-20 | Python, test, docker, deploy failures in different contexts | Tests transferability of rules across repos |
| Manual corrections | 5-8 | Human-correction examples, workflow rules | Especially useful for 30.3.8 |
| Cross-session repeats | 5-8 | Repeat-failure measurement, persistence testing | Critical for proving memory and reduction claims |

### 2.5 Gap Closure Plan

Instead of treating these as open-ended gaps, this is the concrete acquisition plan to close them.

| Asset To Acquire | Target | Primary Source | Closure Action |
|------------------|--------|----------------|----------------|
| OpenCode failure trajectories | 20 | OpenCode sessions on CauterRule | Mine the last 20-30 sessions, select clear failures, convert to JSONL in `corpus/raw/opencode/` |
| OpenCode success trajectories | 10 | OpenCode sessions on CauterRule | Select matched successful tasks from the same domains, convert to JSONL in `corpus/raw/opencode/` |
| CI-derived JSONL trajectories | 8 | GitHub Actions logs | Download failed run logs, parse with `scripts/parse_ci_log.py`, save to `corpus/raw/ci/` |
| Cross-session repeated failures | 5 | OpenCode + CI + sibling repos | Group by `failure_class`, select repeats appearing in 2+ sessions, save to `corpus/raw/cross-session/` |
| Human-correction examples | 5 | Manual corrections from sessions | Extract correction moments, convert to JSONL in `corpus/raw/corrections/` |
| Noisy/misleading trajectories | 3 | Derived from real failures | Clone 3 clear failures and add retries/irrelevant calls, save to `corpus/curated/noisy/` |
| Golden trajectory set | 10 | Best curated failures | Select strongest curated failures, document expected rules, save to `corpus/golden/` |
| Public-shareable subset | 20-30 | Curated trajectories | Redact and de-identify strong trajectories, publish to `corpus/public/` |

### 2.6 Recommended First Collection Order

To keep momentum high, collect in this order:

1. OpenCode failures from CauterRule development sessions
2. Matching OpenCode successes from the same domains
3. GitHub Actions failures (lint, mypy, pytest, Docker)
4. Manual correction examples already visible in project history
5. Cross-session repeats identified from the above
6. Near-miss and noisy variants derived from the real failures
7. Golden set selected from the strongest curated failures

### 2.7 Closure Milestones For Corpus Acquisition

The corpus acquisition effort is considered materially complete for M30 when all of the following are true:

- [ ] At least 20 real OpenCode failure trajectories are collected
- [ ] At least 10 real OpenCode success trajectories are collected
- [ ] At least 8 CI-derived failure trajectories are collected
- [ ] At least 5 cross-session repeat failures are identified and labeled
- [ ] At least 5 human-correction examples are captured
- [ ] At least 3 noisy/misleading variants are created from real failures
- [ ] A 10-trajectory golden set is created and documented
- [ ] A 20-30 trajectory public-shareable subset is prepared
- [ ] `corpus/catalog.yaml` reflects actual collected counts
- [ ] Validation script passes on the curated corpus

---

## 3. Corpus Structure

### 3.1 Directory Layout

```
field-test/v0.1.0/corpus/
├── README.md                          # This file
├── catalog.yaml                       # Master catalog of all trajectories
│
├── raw/                               # Original captured trajectories (unmodified)
│   ├── opencode/                      # From OpenCode sessions
│   │   ├── session-001.jsonl
│   │   ├── session-002.jsonl
│   │   └── ...
│   ├── ci/                            # From GitHub Actions
│   │   ├── ci-lint-failure.jsonl
│   │   ├── ci-mypy-failure.jsonl
│   │   └── ...
│   ├── sibling-repos/                 # From other repo agent runs
│   │   ├── agentselfedit-test.jsonl
│   │   └── ...
│   ├── corrections/                   # Manual correction transcripts
│   │   ├── correction-git-push.jsonl
│   │   └── ...
│   └── cross-session/                 # Cross-session repeat failures
│       ├── repeat-docker-build.jsonl
│       └── ...
│
├── curated/                           # Cleaned, labeled, validated trajectories
│   ├── failures/                      # 30 failure trajectories
│   │   ├── F-001-git-push-non-ff.jsonl
│   │   ├── F-002-python-import.jsonl
│   │   └── ... (30 files)
│   ├── successes/                     # 20 success trajectories
│   │   ├── S-001-git-push-success.jsonl
│   │   └── ... (20 files)
│   ├── nearmiss/                      # 10 near-miss trajectories
│   │   ├── N-001-auth-vs-ff.jsonl
│   │   └── ... (10 files)
│   ├── noisy/                         # 5 noisy/misleading trajectories
│   │   ├── M-001-retry-noise.jsonl
│   │   └── ... (5 files)
│   └── corrections/                   # 5 human-correction examples
│       ├── C-001-pull-before-push.jsonl
│       └── ... (5 files)
│
└── golden/                            # 10 golden trajectories (regression anchor)
    ├── golden-manifest.json           # Expected rules per trajectory
    ├── G-001-git-push-non-ff.jsonl
    └── ... (10 files)
```

### 3.2 File Naming Convention

```
<type>-<nnn>-<domain>-<scenario>.jsonl

Where:
  type     = F (failure), S (success), N (nearmiss), M (misleading/noisy),
             C (correction), G (golden)
  nnn      = sequential number (001, 002, ...)
  domain   = git, python, docker, deploy, test, ci, shell, workflow, env
  scenario = brief kebab-case description
```

Example: `F-001-git-push-non-ff.jsonl`

### 3.3 Catalog Format

`corpus/catalog.yaml`:
```yaml
version: "1.0"
generated: "2026-09-05"
seed: 42

sources:
  opencode:
    description: "Trajectories extracted from OpenCode sessions on CauterRule repo"
    count: 25
    capture_method: "Manual extraction from session logs + @cauterule.watch"
  ci:
    description: "GitHub Actions CI failures from CauterRule repo"
    count: 12
    capture_method: "Downloaded CI run logs, converted to JSONL format"
  sibling_repos:
    description: "Agent runs on AgentSelfEdit, PlannerCritic, ToolTrust repos"
    count: 18
    capture_method: "Toy agent with @cauterule.watch decorator"
  corrections:
    description: "Manual correction transcripts from development sessions"
    count: 7
    capture_method: "Extracted from conversation history"
  cross_session:
    description: "Same failure type appearing across different days or repos"
    count: 6
    capture_method: "Manual identification from session logs"

total_raw: 68
curated:
  failures: 32
  successes: 20
  nearmiss: 10
  noisy: 6
  corrections: 5
  golden: 10

domains:
  git: 20
  python: 18
  docker: 12
  test: 10
  ci: 8
  deploy: 6
  shell: 4
  env: 4
  workflow: 3
```

### 3.4 Trajectory Metadata Schema

Each JSONL trajectory must include:

```json
{
  "trajectory_id": "F-001-git-push-non-ff",
  "timestamp": "2026-09-05T10:00:00Z",
  "task": "Push local commits to remote branch",
  "domain": "git",
  "failure_class": "git/push",
  "quality_label": "clear",
  "severity": "medium",
  "success": false,
  "failure_point": "Step 2: git push origin main -> rejected (non-fast-forward)",
  "steps": [
    {
      "step_number": 1,
      "tool": "git",
      "input": "git add . && git commit -m 'fix: update config'",
      "output": "1 file changed, 3 insertions(+)",
      "error": null,
      "state": null
    },
    {
      "step_number": 2,
      "tool": "git",
      "input": "git push origin main",
      "output": null,
      "error": "! [rejected] main -> main (non-fast-forward) error: failed to push some refs",
      "state": null
    }
  ],
  "tags": ["git", "push", "non-fast-forward"],
  "expected_rule": "when git push fails with non-fast-forward, pull latest changes before pushing",
  "human_correction": "next time, pull before pushing",
  "source": "opencode",
  "source_repo": "CauterRule",
  "redacted": false,
  "notes": "Classic non-fast-forward push failure. Happens when remote has commits local doesn't. Fix is git pull --rebase before push."
}
```

---

## 4. Collection Process

### 4.1 From OpenCode Sessions (P1)

**Method:** Manual extraction + @cauterule.watch

```
1. Identify 20-30 sessions where the agent failed and was corrected
2. For each session, extract:
   - The task description
   - Each step taken (tool, input, output, error)
   - The failure point
   - The correction that fixed it
3. Format as Trajectory JSONL
4. Label with domain, failure_class, quality_label
5. Save to corpus/raw/opencode/
```

**Session selection criteria:**
- Session had at least one clear failure
- Failure has a clear root cause
- A correction exists (either agent-originated or user-provided)
- Domain matches priority list (git, python, docker, CI, workflow)

### 4.2 From GitHub Actions CI Logs (P2)

**Method:** Download CI run logs, convert to JSONL

```
1. Go to https://github.com/deghosal-2026/CauterRule/actions
2. Find failed runs (lint, mypy, pytest, build)
3. Download the raw log for each failed step
4. Parse the log to extract:
   - What command was run
   - What the error/output was
   - What the expected behavior should have been
5. Format as Trajectory JSONL
6. Save to corpus/raw/ci/
```

**CI sources to mine:**
- `ruff check .` failures
- `mypy src/ tests/` failures
- `pytest --cov` failures
- Docker build failures
- PyPI publish failures

### 4.3 From Sibling Repo Agent Runs (P3)

**Method:** Run @cauterule.watch on toy agent tasks

```
1. Pick 3-5 sibling repos (AgentSelfEdit, PlannerCritic, ToolTrust, etc.)
2. Define 3-5 tasks per repo that are known to fail
3. Wrap the agent function with @cauterule.watch
4. Run the tasks
5. Collect captured trajectories
6. Save to corpus/raw/sibling-repos/
```

**Example tasks per repo:**

| Repo | Task | Expected Failure |
|------|------|------------------|
| AgentSelfEdit | Run pytest without installing deps | ModuleNotFoundError |
| PlannerCritic | Submit plan with invalid JSON | JSON parse error |
| ToolTrust | Build without Dockerfile | docker build fails |
| CauterRule | Run mypy without strict | Type errors |
| Any repo | Git push without committing | Dirty tree rejected |

### 4.4 From Manual Correction Transcripts (P4)

**Method:** Collect instances where user corrected the agent

```
1. Review session history for "next time", "instead", "try this", "remember" patterns
2. For each correction:
   - What was the task?
   - What did the agent do wrong?
   - What should it have done instead?
   - Was the correction effective?
3. Format as Trajectory JSONL
4. Save to corpus/raw/corrections/
```

**Manual correction examples from CauterRule development:**

| # | Situation | Wrong Behavior | Correction | Domain |
|---|-----------|---------------|------------|--------|
| 1 | Updating WBS | Agent edited wrong section | "Check the section header before editing" | workflow |
| 2 | Docker build | Agent forgot to rebuild image | "Always rebuild before testing Docker changes" | docker |
| 3 | Pushing changes | Agent tried to push on detached HEAD | "Check current branch before pushing" | git |
| 4 | Running tests | Agent ran wrong test file | "Check the test file path matches the module" | test |
| 5 | Installing deps | Agent forgot to activate venv | "Activate venv before pip install" | python |

### 4.5 From Cross-Session Repeat Failures (P5)

**Method:** Identify same failure type across different sessions

```
1. Scan all collected trajectories
2. Group by failure_class
3. Identify failure classes that appear in 2+ different source sessions
4. Flag as cross-session repeats
5. Save to corpus/raw/cross-session/
```

**Expected cross-session repeats:**
- `git/push` — likely in multiple sessions
- `python/import` — across different repos
- `docker/build` — environment-specific
- `test/failure` — recurring test patterns
- `workflow/verification` — agent not checking before completing

---

## 5. Collection Targets

### 5.1 Trajectory Count Targets

| Category | Target | Minimum | Source |
|----------|--------|---------|--------|
| Failure — git | 8 | 5 | OpenCode + CI + corrections |
| Failure — python | 6 | 4 | OpenCode + sibling repos |
| Failure — docker | 4 | 3 | OpenCode + CI |
| Failure — test | 4 | 3 | CI + sibling repos |
| Failure — CI/tooling | 4 | 3 | CI logs |
| Failure — shell/env | 2 | 2 | Corrections |
| Failure — workflow | 2 | 2 | Corrections |
| **Total failures** | **30** | **22** | |
| Success — git | 5 | 3 | OpenCode |
| Success — python | 4 | 3 | OpenCode |
| Success — docker | 3 | 2 | OpenCode |
| Success — test | 4 | 2 | OpenCode |
| Success — other | 4 | 2 | OpenCode |
| **Total successes** | **20** | **12** | |
| Near-miss | 10 | 5 | Generated from failures |
| Noisy/misleading | 5 | 3 | Generated from failures |
| Human-correction | 5 | 3 | Corrections |
| **Total curated** | **70** | **45** | |
| Golden (regression) | 10 | 10 | Selected from curated |

### 5.2 Domain Distribution Target

```
git        ████████████████████  28%  (20/70)
python     ████████████████      25%  (18/70)
docker     ████████████          17%  (12/70)
test       ██████████            14%  (10/70)
ci         ███████                8%  (6/70)
deploy     █████                  6%  (4/70)
shell      ████                   4%  (3/70)
env        ████                   4%  (3/70)
workflow   ███                    4%  (3/70)
```

### 5.3 Quality Label Distribution Target

```
clear        ████████████████████  60%  (42/70)
ambiguous    ██████████            20%  (14/70)
multi-causal █████                  8%  (6/70)
misleading   ████                   6%  (4/70)
operator-induced ████               6%  (4/70)
```

---

## 6. Collection Tooling

### 6.1 Manual Trajectory Creator

Use this script to create a trajectory file interactively:

```python
# scripts/create_trajectory.py
"""Interactive tool to create a trajectory JSONL file."""

import json
import uuid
from datetime import datetime, timezone


def create_trajectory():
    tid = input("Trajectory ID (e.g. F-004-docker-build): ").strip()
    task = input("Task description: ").strip()
    domain = input("Domain (git/python/docker/test/ci/deploy/shell/env/workflow): ").strip()
    failure_class = input("Failure class (e.g. git/push, python/import): ").strip()
    quality = input("Quality label (clear/ambiguous/multi-causal/misleading/operator-induced): ").strip()
    severity = input("Severity (low/medium/high): ").strip()
    success = input("Success? (y/n): ").strip().lower() == "n"
    correction = input("Human correction (or leave blank): ").strip()
    source = input("Source (opencode/ci/sibling-repos/corrections): ").strip()

    steps = []
    step_num = 1
    while True:
        print(f"\n--- Step {step_num} ---")
        tool = input("Tool name (or blank to stop): ").strip()
        if not tool:
            break
        inp = input("Input: ").strip()
        out = input("Output: ").strip()
        err = input("Error (or blank): ").strip()
        steps.append({
            "step_number": step_num,
            "tool": tool,
            "input": inp or None,
            "output": out or None,
            "error": err or None,
            "state": None,
        })
        step_num += 1

    trajectory = {
        "trajectory_id": tid,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task": task,
        "domain": domain,
        "failure_class": failure_class,
        "quality_label": quality,
        "severity": severity,
        "success": success,
        "failure_point": steps[-1]["error"] if steps else None,
        "steps": steps,
        "tags": domain.split(",") if "," in domain else [domain],
        "expected_rule": "",
        "human_correction": correction or None,
        "source": source,
        "source_repo": "CauterRule",
        "redacted": False,
        "notes": "",
    }

    outpath = f"field-test/v0.1.0/corpus/raw/{source}/{tid}.jsonl"
    with open(outpath, "w") as f:
        f.write(json.dumps(trajectory) + "\n")
    print(f"\nSaved to {outpath}")
    return trajectory


if __name__ == "__main__":
    create_trajectory()
```

### 6.2 CI Log Parser

For converting GitHub Actions log text to Trajectory JSONL:

```python
# scripts/parse_ci_log.py
"""Parse a GitHub Actions CI log into a trajectory JSONL file."""

import json
import re
import sys
from pathlib import Path


def parse_ci_log(log_path: str) -> dict:
    text = Path(log_path).read_text()
    
    # Extract the command that was run
    cmd_match = re.search(r"Run (.+)", text)
    command = cmd_match.group(1) if cmd_match else "unknown"
    
    # Extract the first error
    error_match = re.search(r"Error: (.+)", text)
    error = error_match.group(1) if error_match else None
    
    # Extract the full error block
    error_block = ""
    if error:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "Error:" in line:
                error_block = "\n".join(lines[i:i+10])
                break
    
    # Determine domain from command
    domain = "ci"
    if "ruff" in command or "flake8" in command:
        domain = "ci"
    elif "mypy" in command:
        domain = "ci"
    elif "pytest" in command:
        domain = "test"
    elif "docker" in command:
        domain = "docker"
    elif "git" in command:
        domain = "git"
    elif "pip" in command:
        domain = "python"
    
    return {
        "trajectory_id": f"ci-{Path(log_path).stem}",
        "timestamp": "2026-09-05T00:00:00Z",
        "task": f"Run CI step: {command[:100]}",
        "domain": domain,
        "failure_class": f"{domain}/failure",
        "quality_label": "clear",
        "severity": "medium",
        "success": error is not None,
        "failure_point": error or "unknown",
        "steps": [
            {
                "step_number": 1,
                "tool": domain,
                "input": command[:500],
                "output": text[:1000],
                "error": error_block[:1000] or None,
                "state": None,
            }
        ],
        "tags": [domain, "ci"],
        "expected_rule": "",
        "human_correction": None,
        "source": "ci",
        "source_repo": "CauterRule",
        "redacted": False,
        "notes": f"Parsed from CI log: {log_path}",
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_ci_log.py <ci-log-file.txt>")
        sys.exit(1)
    traj = parse_ci_log(sys.argv[1])
    outpath = f"field-test/v0.1.0/corpus/raw/ci/{traj['trajectory_id']}.jsonl"
    Path(outpath).parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, "w") as f:
        f.write(json.dumps(traj) + "\n")
    print(f"Saved: {outpath}")
```

---

## 7. Validation Checks

Every curated trajectory must pass these checks before being promoted to `corpus/curated/`:

### 7.1 Required Fields

- [ ] `trajectory_id` — non-empty, follows naming convention
- [ ] `timestamp` — valid ISO 8601
- [ ] `task` — non-empty, describes what the agent was asked to do
- [ ] `domain` — one of: git, python, docker, test, ci, deploy, shell, env, workflow
- [ ] `failure_class` — follows `<domain>/<subtype>` pattern
- [ ] `quality_label` — one of: clear, ambiguous, multi-causal, misleading, operator-induced
- [ ] `severity` — one of: low, medium, high
- [ ] `success` — boolean
- [ ] `steps` — array, at least 1 step
- [ ] Every step has `step_number` (int), `tool` (string), and at least one of `input`, `output`, `error`
- [ ] `source` — one of: opencode, ci, sibling-repos, corrections
- [ ] `redacted` — boolean (must be true if source contains secrets)

### 7.2 Content Checks

- [ ] Trajectory is internally consistent (steps flow logically)
- [ ] Failure point is one of the step errors
- [ ] No secrets in any field (API keys, tokens, passwords)
- [ ] Expected rule (if specified) is a reasonable lesson
- [ ] Human correction (if present) addresses the actual failure

### 7.3 Validation Script

```bash
python -c "
import json
from pathlib import Path

VALID_DOMAINS = {'git','python','docker','test','ci','deploy','shell','env','workflow'}
VALID_LABELS = {'clear','ambiguous','multi-causal','misleading','operator-induced'}
VALID_SOURCES = {'opencode','ci','sibling-repos','corrections'}

errors = []
for f in Path('field-test/v0.1.0/corpus/curated').rglob('*.jsonl'):
    try:
        traj = json.loads(f.read_text())
        tid = traj.get('trajectory_id', 'unknown')
        if traj.get('domain') not in VALID_DOMAINS:
            errors.append(f'{tid}: invalid domain {traj.get(\"domain\")}')
        if traj.get('quality_label') not in VALID_LABELS:
            errors.append(f'{tid}: invalid quality_label {traj.get(\"quality_label\")}')
        if traj.get('source') not in VALID_SOURCES:
            errors.append(f'{tid}: invalid source {traj.get(\"source\")}')
        if not traj.get('steps'):
            errors.append(f'{tid}: no steps')
        if not traj.get('task'):
            errors.append(f'{tid}: no task')
    except Exception as e:
        errors.append(f'{f}: {e}')

if errors:
    for e in errors:
        print(f'ERROR: {e}')
    print(f'{len(errors)} validation errors')
    exit(1)
else:
    print(f'All trajectories valid')
"
```

---

## 8. Corpus Curation Process

### Step 1: Collect Raw Trajectories

Collect from all 5 sources. Save to `corpus/raw/<source>/` as JSONL files.

**Target:** 68+ raw trajectories
**Done when:** All 5 sources have been mined, raw directory is populated

### Step 2: Curate and Clean

For each raw trajectory:
1. Verify metadata is correct
2. Redact any secrets
3. Ensure all required fields are present
4. Add expected rule (if extractable)
5. Classify quality label
6. Save to `corpus/curated/<category>/` with standard naming

**Target:** 70 curated trajectories (30F + 20S + 10N + 5M + 5C)
**Done when:** All 70 trajectories have passed validation

### Step 3: Create Golden Set

From the curated set, select 10 trajectories with the clearest failure-to-rule mapping:
- 3 git failures
- 2 python failures
- 2 docker failures
- 1 test failure
- 1 CI failure
- 1 workflow failure

For each, verify the expected rule is correct by running `cauterule extract --dry-run` with a mock LLM.

**Target:** 10 golden trajectories
**Done when:** `golden-manifest.json` lists all 10 with expected rules

### Step 4: Publish Public Corpus

From the curated set, select trajectories suitable for public sharing:
- No secrets
- No private repo references
- No sensitive project details

Save to `corpus/public/` with README explaining the corpus format.

**Target:** 30 public trajectories
**Done when:** `corpus/public/` is populated with shareable trajectories

---

## 9. Timeline

| Phase | Duration | Target | Done When |
|-------|----------|--------|-----------|
| Collect raw trajectories (all 5 sources) | 2 hours | 68+ raw | Raw directory populated |
| Curate and validate | 1 hour | 70 curated | Validation script passes |
| Create golden set | 30 min | 10 golden | golden-manifest.json complete |
| Publish public set | 30 min | 30 public | corpus/public/ populated |
| **Total** | **~4 hours** | | |

---

## 10. What Success Looks Like

After corpus acquisition, the following files exist:

```
field-test/v0.1.0/corpus/
├── README.md
├── catalog.yaml
├── raw/                       # 68+ trajectories from 5 sources
│   ├── opencode/ (25-30)
│   ├── ci/ (10-15)
│   ├── sibling-repos/ (15-20)
│   ├── corrections/ (5-8)
│   └── cross-session/ (5-8)
├── curated/                   # 70 validated trajectories
│   ├── failures/ (30)
│   ├── successes/ (20)
│   ├── nearmiss/ (10)
│   ├── noisy/ (5)
│   └── corrections/ (5)
└── golden/                    # 10 regression-anchor trajectories
    ├── golden-manifest.json
    └── 10 JSONL files

corpus/public/                 # 30 shareable trajectories
└── README.md + JSONL files
```

**Validation passes:** `python scripts/validate_corpus.py` exits 0 with "All trajectories valid"
