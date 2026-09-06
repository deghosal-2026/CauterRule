# Docker Field Test Plan — CauterRule v0.1.0

> **Goal:** Validate the full CauterRule system end-to-end in a Docker container under field conditions. Every component of the stack is tested with real inputs, real outputs, and measurable pass/fail criteria. The container simulates a production environment where an agent fails, CauterRule captures the failure, extracts a rule, replays it, promotes it, and injects it on the next run.

---

## 1. Test Environment

### 1.1 Docker Image

The field test runs entirely inside the CauterRule Docker image (`Dockerfile`). The image is built from `python:3.12-slim` with CauterRule installed via wheel. No host Python or dependencies are needed.

**Build:**
```bash
docker build -t cauterule:field-test .
```

**Run:**
```bash
docker run --rm cauterule:field-test <test-command>
```

### 1.2 Test Matrix

| Test Layer | What It Tests | Tool | How Verified |
|-----------|---------------|------|-------------|
| CLI | All 25+ commands produce real output | `pytest` in container | Assert real effects (files created, reports printed, exit codes) |
| Pipeline | capture → extract → replay → promote → inject | `pytest` + scripted scenario | Rule file exists, git commit exists, injection fires |
| MCP Server | stdio + HTTP transport, all 4 tools | `pytest` + MCP client mock | Tool responses match expected rule store state |
| TUI | Textual app renders, screens work | `pytest` + Textual pilot | Screens mount, keybindings fire, approve promotes |
| API (Python) | Store, models, replay, injection, export | `pytest` | Unit + integration tests pass in container |
| Adversarial | Injection, misleading, poisoning, leakage | `pytest` in container | >=90% immunity, >=95% unsafe blocked, 0 secrets exported |
| Corpus | Tiered corpus, gold families, near-miss | `pytest` in container | All trajectories valid, gold families loaded |
| Benchmarks | Determinism, gold-family, counterexample, near-miss, regression | `pytest` in container | >=85% gold acceptance, >=90% counterexample rejection, >=95% regression catch |
| Scale | Latency, conflict at scale, memory, concurrent | `pytest` in container (marked `slow`) | tiny<2s, p50<100ms, <5s at 1k rules, <1GB RAM |
| Demo | `cauterule demo` runs end-to-end | Scripted `docker run` | Completes <60s, produces narrated walkthrough, rule file created |
| Redaction | Secrets stripped before disk write | `pytest` + grep | No secret patterns in trajectory files |
| Export | All 7 formats, active-only filter | `pytest` + file inspection | All formats valid, retired rules excluded by default |
| Git | Promotion commits, rollback, history | `pytest` + `git log` | Real git hash in rule YAML, rollback removes rule |

### 1.3 No Playwright / Browser UI Tests

CauterRule v0.1.0 has no web UI. The TUI is a terminal UI (Textual), not a browser UI. Playwright is **not needed** for v0.1.0. 

If a web dashboard is added in v0.5.0 (per PRD), Playwright tests would be added then. For now:
- **TUI tests** use Textual's built-in `Pilot` test framework (no browser needed)
- **CLI tests** use Click's `CliRunner` (no browser needed)
- **MCP tests** mock the MCP client (no browser needed)

---

## 2. Docker Test Stages

### Stage 1: Image Build & Install Verification

**Purpose:** Verify the Docker image builds and CauterRule installs correctly.

```bash
# Build the image
docker build -t cauterule:field-test .

# Verify install
docker run --rm cauterule:field-test --version
docker run --rm cauterule:field-test --help
```

**Pass criteria:**
- [ ] Image builds without errors
- [ ] `cauterule --version` prints `0.1.0`
- [ ] `cauterule --help` lists all 25+ commands
- [ ] `pip show cauterule` inside container shows installed package
- [ ] `python -c "import cauterule; print(cauterule.__version__)"` works

### Stage 2: Unit Test Suite (Hermetic, No LLM)

**Purpose:** Run the full deterministic test suite inside the container. Zero external dependencies, zero LLM calls.

```bash
docker run --rm cauterule:field-test sh -c "pytest tests/ -v -m 'not slow' --tb=short"
```

**Pass criteria:**
- [ ] All 781+ tests pass (0 failures)
- [ ] Coverage > 95%
- [ ] No skipped tests (except `slow` marked)
- [ ] `ruff check .` clean
- [ ] `mypy src/ tests/` clean

### Stage 3: Scale Test Suite (Slow Benchmarks)

**Purpose:** Run latency/capacity benchmarks that are too slow for the regular suite.

```bash
docker run --rm cauterule:field-test sh -c "pytest tests/scale/ -v --tb=short"
```

**Pass criteria:**
- [ ] Replay latency: tiny <2s, small <10s, medium <60s per candidate
- [ ] Injection latency: p50 <100ms, p95 <500ms on small corpus
- [ ] Conflict detection: <5s at 1k rules
- [ ] Memory footprint: <1GB RAM on small corpus
- [ ] Incremental indexing: <1s per new rule at 1k rules
- [ ] Extractor stability: bounded variance on repeat extraction

### Stage 4: Adversarial Test Suite

**Purpose:** Verify the system resists manipulation attempts.

```bash
docker run --rm cauterule:field-test sh -c "pytest tests/adversarial/ -v"
```

**Pass criteria:**
- [ ] Prompt injection: >=90% of injection attempts fail to alter extractor output
- [ ] Misleading root-cause: extractor avoids superficial lessons
- [ ] Contradiction stress: >=90% detection recall of seeded contradictions
- [ ] Unsafe directive: >=95% of unsafe rules blocked by linter or gate
- [ ] Data poisoning: poisoned trajectories caught by replay or provenance
- [ ] Instruction leakage: no secrets survive export (grep for secret patterns)

### Stage 5: Corpus & Benchmark Validation

**Purpose:** Validate the corpus is complete and benchmarks pass.

```bash
docker run --rm cauterule:field-test sh -c "pytest tests/corpus/ tests/benchmark/ -v"
```

**Pass criteria:**
- [ ] Tiered corpus: tiny (25), small (100), medium (1k), large (10k+) — all have balanced success/failure
- [ ] Domain corpora: coding, DevOps, research, support, browser_automation — all generate valid trajectories
- [ ] Gold rule families: each scenario has >=2 acceptable rule abstractions loaded from sidecar
- [ ] Counterexample corpus: >=90% rejection rate
- [ ] Near-miss corpus: >=90% do not trigger
- [ ] Replay determinism: same candidate + same corpus = same report
- [ ] Gold-family acceptance: >=85%
- [ ] Success-regression catch: >=95%
- [ ] Rule mutation: perturbed rules caught by replay
- [ ] Confidence calibration: scores correlate with replay outcomes

### Stage 6: CLI Integration Tests

**Purpose:** Verify every CLI command produces real effects, not just echo output.

```bash
docker run --rm cauterule:field-test sh -c "pytest tests/cli/ -v"
```

**Pass criteria:**
- [ ] `cauterule init` creates `cauterule.toml`, `rules/` dir, `.gitignore`, example agent
- [ ] `cauterule extract --trajectory <file>` produces a CandidateRule (not just echo)
- [ ] `cauterule test --candidate <id>` runs replay and prints EvidenceReport
- [ ] `cauterule promote --candidate <id>` writes rule YAML and git commits
- [ ] `cauterule inject <task>` shows which rules would fire
- [ ] `cauterule list` prints table with id, trigger, status, hits, tags
- [ ] `cauterule show <rule-id>` prints full provenance view
- [ ] `cauterule search <query>` returns matching rules
- [ ] `cauterule audit <rule-id>` prints provenance trail
- [ ] `cauterule diff <rule-id>` shows changes between versions
- [ ] `cauterule retire <rule-id>` retires rule with reason (git commit)
- [ ] `cauterule history` prints timeline of promotions/retirements
- [ ] `cauterule conflicts` lists detected conflicts
- [ ] `cauterule validate` checks rule store integrity
- [ ] `cauterule health` prints rule store health report
- [ ] `cauterule counterfactual` prints "would have avoided X failures"
- [ ] `cauterule story` generates narrative blog post
- [ ] `cauterule explain <rule-id>` prints human-readable explanation
- [ ] `cauterule config` views/edits configuration
- [ ] `cauterule pack list` lists installed rule packs
- [ ] `cauterule pack info <name>` shows pack contents
- [ ] `cauterule metrics` prints CLI summary
- [ ] `cauterule report` generates markdown report

### Stage 7: TUI Tests (Textual Pilot)

**Purpose:** Verify the TUI renders and functions correctly.

```bash
docker run --rm cauterule:field-test sh -c "pytest tests/tui/ -v"
```

**Pass criteria:**
- [ ] `ReviewScreen` loads candidates from store on mount
- [ ] Evidence summary cards render: "Prevented N failures, broke 0 successes"
- [ ] Rule confidence cards render: confidence, prevented, broken, last hit, tags
- [ ] Human annotation capture: tag input, comment field, category selector
- [ ] Batch review mode: 10 candidates shown, approve/reject-all works
- [ ] Filter by tag/status/confidence narrows the review queue
- [ ] Approve button triggers `execute_promotion` (rule file created)
- [ ] Reject button advances to next candidate
- [ ] Keybindings work: q=quit, r=review, f=filter, a=approve, x=reject

### Stage 8: MCP Server Tests

**Purpose:** Verify the MCP server exposes all 4 tools correctly.

```bash
docker run --rm cauterule:field-test sh -c "pytest tests/mcp/ -v"
```

**Pass criteria:**
- [ ] `get_matching_rules(task)` returns rules whose trigger is substring of task
- [ ] `get_rule(id)` returns a single rule with full provenance
- [ ] `list_rules(filter)` browses the rule store with optional filter
- [ ] `report_failure(trajectory)` triggers extraction and returns candidate info
- [ ] MCP stdio transport works (mock client connects, sends request, gets response)
- [ ] MCP HTTP transport works (if configured)

### Stage 9: Pipeline Integration Test (End-to-End)

**Purpose:** Verify the full extract → test → promote → inject loop works in a container.

```bash
# Create a test trajectory file
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  # 1. Initialize project
  cauterule init --dir /data/test-project

  # 2. Extract a candidate rule from a trajectory
  cauterule extract --trajectory /data/test-project/trajectories/failure.jsonl --dry-run

  # 3. Replay-test the candidate
  cauterule test --candidate /data/test-project/candidates/candidate-1.yaml

  # 4. Promote the tested rule
  cauterule promote --candidate /data/test-project/candidates/candidate-1.yaml

  # 5. Verify the rule was promoted
  cauterule list

  # 6. Inject on a matching task
  cauterule inject --task 'git push to origin main'

  # 7. Show the rule
  cauterule show R-001

  # 8. Check health
  cauterule health

  # 9. Validate store
  cauterule validate
"
```

**Pass criteria:**
- [ ] `cauterule init` creates project scaffold
- [ ] `cauterule extract --dry-run` produces a CandidateRule (pattern-based, no LLM)
- [ ] `cauterule test` runs replay and prints evidence report with precision/recall/verdict
- [ ] `cauterule promote` writes rule YAML to `rules/` and creates git commit
- [ ] `cauterule list` shows the promoted rule in the table
- [ ] `cauterule inject` shows which rules would fire for the given task
- [ ] `cauterule show` prints full provenance (source failure → evidence → promotion)
- [ ] `cauterule health` reports healthy store
- [ ] `cauterule validate` passes with zero errors
- [ ] Rule YAML contains real git hash in `promotion_commit` field

### Stage 10: Demo Test (`cauterule demo`)

**Purpose:** The "wow" moment — full loop in under 60 seconds.

```bash
docker run --rm cauterule:field-test demo
```

**Pass criteria:**
- [ ] Completes in <60 seconds
- [ ] Produces a narrated walkthrough (prints steps to stdout)
- [ ] At least 1 rule is extracted, tested, and promoted
- [ ] Rule file exists in `rules/` after demo completes
- [ ] Git commit exists for the promotion
- [ ] No errors or tracebacks in output

### Stage 11: Redaction Verification

**Purpose:** Verify secrets are stripped before disk write and LLM extraction.

```bash
docker run --rm cauterule:field-test sh -c "
  # Create a trajectory with secrets
  python -c \"
  from cauterule.models.trajectory import Trajectory, Step
  from cauterule.adapter.decorator import watch
  from cauterule.capture.writer import write_trajectory
  import json, tempfile, os

  # Simulate a failure with API key in kwargs
  traj = Trajectory(
      id='T-LEAK-1',
      timestamp='2026-09-05T12:00:00Z',
      task='deploy with api_key=sk-1234567890',
      steps=(Step(step_number=1, tool='deploy', error='auth failed', input='api_key=sk-1234567890'),),
      success=False,
      failure_point='auth',
  )
  d = tempfile.mkdtemp()
  write_trajectory(traj, os.path.join(d, 'traj.jsonl'))

  # Read back and verify no secret
  with open(os.path.join(d, 'traj.jsonl')) as f:
      content = f.read()
      assert 'sk-1234567890' not in content, 'SECRET LEAKED!'
      print('PASS: secret redacted')
  \"
"
```

**Pass criteria:**
- [ ] `sk-1234567890` does not appear in the written JSONL file
- [ ] Trajectory has `redacted: true` flag set
- [ ] No secret patterns (API keys, tokens, passwords) in trajectory files
- [ ] Export functions produce no secrets (grep for common patterns)

### Stage 12: Export/Import Round-Trip Test

**Purpose:** Verify all 7 export formats and import round-trip fidelity.

```bash
docker run --rm cauterule:field-test sh -c "pytest tests/export/ tests/import_/ -v"
```

**Pass criteria:**
- [ ] Export to `.cursorrules` produces valid file
- [ ] Export to `CLAUDE.md` produces valid markdown
- [ ] Export to `AGENTS.md` produces valid markdown
- [ ] Export to `.windsurfrules` produces valid file
- [ ] Export to `aider.conf.yml` produces valid YAML
- [ ] Export to markdown produces valid markdown
- [ ] Export to JSON produces valid JSON
- [ ] Default export only includes `status == "active"` rules
- [ ] `--include-retired` flag includes all rules
- [ ] Import from `.cursorrules` / `CLAUDE.md` / `AGENTS.md` produces candidate rules
- [ ] Import from chat history parses corrections into candidate rules

### Stage 13: Git Integration Test

**Purpose:** Verify git-based versioning works correctly in the container.

```bash
docker run --rm cauterule:field-test sh -c "
  cd /tmp && mkdir test-store && cd test-store && git init

  # Promote a rule
  cauterule promote --candidate /app/examples/candidate.yaml --store /tmp/test-store/rules

  # Verify git commit
  git log --oneline
  git diff HEAD~1

  # Verify rule YAML has real hash
  cat rules/R-001.yaml | grep promotion_commit

  # Rollback
  git revert HEAD --no-edit
  cauterule validate --store /tmp/test-store/rules
"
```

**Pass criteria:**
- [ ] `git log` shows `promote: R-001` commit message
- [ ] Rule YAML `promotion_commit` field contains 40-char hex hash (not UUID)
- [ ] `git rev-parse HEAD` matches hash in YAML
- [ ] `git revert` removes the rule from the store
- [ ] `cauterule validate` passes after rollback

### Stage 14: Loop Orchestrator Test

**Purpose:** Verify the full `run_loop` pipeline works end-to-end.

```bash
docker run --rm cauterule:field-test sh -c "pytest tests/loop/ -v"
```

**Pass criteria:**
- [ ] `run_loop(trajectory, config)` returns a promoted rule ID (not None)
- [ ] All 9 stages execute: capture → redact → cluster → extract → lint → replay → tournament → conflict → promote
- [ ] A rule file is created in `rules/` after the loop completes
- [ ] Git commit exists for the promotion
- [ ] Loop handles empty trajectory gracefully (no crash)

### Stage 15: Multi-Environment Consistency

**Purpose:** Verify the same tests pass on different base images.

```bash
# Test with Python 3.11
docker build --build-arg PYTHON_VERSION=3.11 -t cauterule:py311 .
docker run --rm cauterule:py311 sh -c "pytest tests/ -m 'not slow' --tb=short"

# Test with Python 3.12
docker build --build-arg PYTHON_VERSION=3.12 -t cauterule:py312 .
docker run --rm cauterule:py312 sh -c "pytest tests/ -m 'not slow' --tb=short"

# Test with Python 3.13
docker build --build-arg PYTHON_VERSION=3.13 -t cauterule:py313 .
docker run --rm cauterule:py313 sh -c "pytest tests/ -m 'not slow' --tb=short"
```

**Pass criteria:**
- [ ] All tests pass on Python 3.11
- [ ] All tests pass on Python 3.12
- [ ] All tests pass on Python 3.13
- [ ] No version-specific failures

---

## 3. Docker Compose Integration

### 3.1 docker-compose.yaml (Enhanced)

```yaml
version: "3.9"

services:
  cauterule-demo:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cauterule-demo
    command: demo
    volumes:
      - ./rules:/app/rules
      - ./corpus:/app/corpus
      - ./examples:/app/examples
    environment:
      - CAUTERULE_LLM_PROVIDER=openai
      - CAUTERULE_MODEL=gpt-4o
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}

  cauterule-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cauterule-mcp
    command: mcp --transport stdio
    volumes:
      - ./rules:/app/rules

  cauterule-test:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cauterule-test
    command: sh -c "pytest tests/ -v -m 'not slow' --tb=short"
    volumes:
      - ./tests:/app/tests
      - ./src:/app/src
```

### 3.2 Compose Test Commands

```bash
# Run the demo
docker compose up cauterule-demo

# Run the full test suite
docker compose up cauterule-test

# Start MCP server
docker compose up cauterule-mcp
```

---

## 4. Test Orchestration Script

A single script runs all 15 stages sequentially and reports pass/fail:

```bash
#!/bin/bash
# scripts/docker_field_test.sh

set -e
IMAGE="cauterule:field-test"
PASS=0
FAIL=0

run_stage() {
    local name="$1"
    local cmd="$2"
    echo "=== STAGE: $name ==="
    if docker run --rm "$IMAGE" sh -c "$cmd"; then
        echo "PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "FAIL: $name"
        FAIL=$((FAIL + 1))
    fi
}

run_stage "Build & Install" "cauterule --version && cauterule --help"
run_stage "Unit Tests" "pytest tests/ -v -m 'not slow' --tb=short -q"
run_stage "Scale Tests" "pytest tests/scale/ -v --tb=short -q"
run_stage "Adversarial" "pytest tests/adversarial/ -v -q"
run_stage "Corpus & Benchmarks" "pytest tests/corpus/ tests/benchmark/ -v -q"
run_stage "CLI Integration" "pytest tests/cli/ -v -q"
run_stage "TUI" "pytest tests/tui/ -v -q"
run_stage "MCP Server" "pytest tests/mcp/ -v -q"
run_stage "Loop Orchestrator" "pytest tests/loop/ -v -q"
run_stage "Export/Import" "pytest tests/export/ tests/import_/ -v -q"
run_stage "Demo" "cauterule demo"

echo ""
echo "=== RESULTS ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Total:  $((PASS + FAIL))"
[ "$FAIL" -eq 0 ] && echo "ALL STAGES PASS" || echo "SOME STAGES FAILED"
```

---

## 5. Test Data

### 5.1 Seeded Trajectories

The field test uses the public synthetic corpus (`corpus/public/`) and seeded example trajectories (`examples/trajectories/`). No real user data is needed.

### 5.2 Mock LLM

For stages that require LLM extraction (Stage 9, Stage 10, Stage 14), the tests use a mock LLM provider that returns deterministic responses. No API keys are needed for the field test. Real API keys are only needed for the optional model bake-off stage.

### 5.3 Test Fixtures

- `tests/fixtures/trajectories/` — pre-built trajectory JSONL files (git, docker, python failures)
- `tests/fixtures/candidates/` — pre-built candidate rule YAML files
- `tests/fixtures/rules/` — pre-built promoted rule YAML files with provenance
- `corpus/public/` — public synthetic corpus for benchmarking

---

## 6. Pass/Fail Summary

| Stage | Tests | Pass Criteria |
|-------|-------|---------------|
| 1. Build & Install | 4 | Image builds, version/help work |
| 2. Unit Tests | 781+ | All pass, cov >95%, ruff+mypy clean |
| 3. Scale Tests | 24 | Latency/capacity thresholds met |
| 4. Adversarial | 41 | >=90% immunity, >=95% blocked, 0 secrets |
| 5. Corpus & Benchmarks | 107 | Corpus valid, benchmarks meet thresholds |
| 6. CLI Integration | 25+ | All commands produce real effects |
| 7. TUI | 41+ | Screens render, keybindings work, promote fires |
| 8. MCP Server | 15+ | All 4 tools return correct responses |
| 9. Pipeline E2E | 9 | Full loop: extract → test → promote → inject |
| 10. Demo | 5 | Completes <60s, rule promoted, narrated walkthrough |
| 11. Redaction | 4 | No secrets in trajectory files or exports |
| 12. Export/Import | 15+ | All 7 formats valid, round-trip fidelity, active-only |
| 13. Git Integration | 5 | Real hash, commit message, rollback works |
| 14. Loop Orchestrator | 5+ | run_loop returns rule ID, all 9 stages execute |
| 15. Multi-Env | 3 | Python 3.11/3.12/3.13 all pass |
| **Total** | **1100+** | **All stages pass** |

---

## 7. What This Plan Does NOT Cover (Deferred)

| Item | Why | When |
|------|-----|------|
| Playwright/browser UI tests | No web UI in v0.1.0 | v0.5.0 (dashboard) |
| Real LLM API calls | Cost + non-deterministic | Optional model bake-off stage |
| Homebrew install test | macOS only, not Docker | Separate macOS field test |
| Standalone binary test | PyInstaller, not Docker | Separate binary field test |
| GitHub Action test | Requires real CI run | CI integration test |
| Webhook delivery test | Requires external service | Integration test with mock server |
| OpenTelemetry export test | Requires OTel collector | Integration test with mock collector |