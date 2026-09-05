# v0.1.0 — Docker Field Test WBS

**Part of:** M30 Comprehensive Field Test
**Execution order:** Strictly sequential — each task depends on the previous one completing.

## Dependencies

```
30.6.13 (Fixtures) ──> 30.6.14 (Compose) ──> 30.6.1 (Build) ──> 30.6.2 (CLI) ──> 30.6.3 (TUI) ──> 30.6.4 (MCP) ──> 30.6.5 (Pipeline) ──> 30.6.6 (Redact) ──> 30.6.7 (Export) ──> 30.6.8 (Git) ──> 30.6.9 (Loop) ──> 30.6.10 (MultiEnv) ──> 30.6.11 (Compose) ──> 30.6.12 (Script)
```

Fixtures first (they're needed by everything), then infrastructure, then individual test stages, then integration, then orchestration.

---

## Task 30.6.13: Test Fixtures Package

**Issue:** #381
**Files:** `tests/fixtures/`

| Sub-task | File | Exit Criteria |
|----------|------|---------------|
| 13.1 Fixtures package init | `tests/fixtures/__init__.py` | Exports all fixtures, importable |
| 13.2 Trajectory fixtures | `tests/fixtures/trajectories/git_push_failure.jsonl` | Valid JSONL, real git failure scenario |
| 13.3 Trajectory fixtures | `tests/fixtures/trajectories/docker_build_failure.jsonl` | Valid JSONL, real docker build failure |
| 13.4 Trajectory fixtures | `tests/fixtures/trajectories/python_import_failure.jsonl` | Valid JSONL, real python import error |
| 13.5 Trajectory fixtures | `tests/fixtures/trajectories/deploy_timeout.jsonl` | Valid JSONL, deployment timeout scenario |
| 13.6 Trajectory fixtures | `tests/fixtures/trajectories/test_failure.jsonl` | Valid JSONL, test suite failure |
| 13.7 Candidate rule fixtures | `tests/fixtures/candidates/candidate_git_push.yaml` | Valid CandidateRule YAML, "when git push fails" |
| 13.8 Candidate rule fixtures | `tests/fixtures/candidates/candidate_docker_build.yaml` | Valid CandidateRule YAML, "when docker build fails" |
| 13.9 Promoted rule fixtures | `tests/fixtures/rules/R-001.yaml` | Active StandingRule with full provenance |
| 13.10 Promoted rule fixtures | `tests/fixtures/rules/R-002.yaml` | Retired rule with retired_at/retirement_reason |
| 13.11 Promoted rule fixtures | `tests/fixtures/rules/R-003.yaml` | Superseded rule with superseded_by |
| 13.12 Pytest conftest | `tests/fixtures/conftest.py` | `test_trajectory`, `test_candidate`, `test_rule`, `test_store` fixtures |

**Exit gate:**
- [ ] `python -c "from tests.fixtures import *"` works
- [ ] All 5 trajectory JSONL files parse as Trajectory objects
- [ ] All 2 candidate YAML files parse as CandidateRule objects
- [ ] All 3 rule YAML files parse as StandingRule objects (with lifecycle fields)
- [ ] `pytest tests/fixtures/conftest.py` discovers all fixtures
- [ ] `ruff check tests/fixtures/` — clean
- [ ] `mypy tests/fixtures/` — clean

---

## Task 30.6.14: Update docker-compose.yaml

**Issue:** #382
**Files:** `docker-compose.yaml`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 14.1 Add `cauterule-test` service | pytest service, mount tests + src, run `pytest tests/ -v -m "not slow"` | Service starts and tests pass |
| 14.2 Add `cauterule-mcp` service | MCP server, stdio transport, mount rules volume | Service starts and accepts connections |
| 14.3 Add health checks | Each service has health check (command, interval, retries) | `docker compose ps` shows healthy |
| 14.4 Add env passthrough | CAUTERULE_LLM_PROVIDER, CAUTERULE_MODEL, OPENAI_API_KEY | Env vars reach container |
| 14.5 Add volume mounts | rules, corpus, examples, tests, src | Files mount correctly |
| 14.6 Add network | Network for MCP HTTP transport | Containers can communicate |

**Exit gate:**
- [ ] `docker compose config` validates without errors
- [ ] `docker compose up cauterule-test` runs tests and exits 0
- [ ] `docker compose up cauterule-demo` runs demo
- [ ] `docker compose up cauterule-mcp` starts MCP server
- [ ] `docker compose down` cleans up all containers

---

## Task 30.6.1: Docker Image Build & Install Verification

**Issue:** #370
**Files:** `tests/field/test_docker_build.py`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 1.1 Build image test | `subprocess.run(["docker", "build", "-t", "cauterule:field-test", "."])` | Returns 0 |
| 1.2 Version test | `docker run --rm cauterule:field-test --version` | Outputs `0.1.0` |
| 1.3 Help test | `docker run --rm cauterule:field-test --help` | Lists all 25+ commands |
| 1.4 Pip show test | `docker run ... pip show cauterule` | Shows installed package metadata |
| 1.5 Import test | `docker run ... python -c "import cauterule; print(cauterule.__version__)"` | Prints `0.1.0` |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_build.py -v` — all pass
- [ ] `ruff check tests/field/` — clean
- [ ] No Docker daemon errors

---

## Task 30.6.2: Docker CLI Integration Test

**Issue:** #371
**Files:** `tests/field/test_docker_cli.py`

| Sub-task | Command | Exit Criteria |
|----------|---------|---------------|
| 2.1 | `cauterule init` | Creates `cauterule.toml`, `rules/`, `.gitignore`, example agent |
| 2.2 | `cauterule extract --dry-run` | Produces CandidateRule with valid when/do |
| 2.3 | `cauterule test` | Runs replay, prints EvidenceReport with precision/recall/verdict |
| 2.4 | `cauterule promote` | Writes rule YAML, creates git commit |
| 2.5 | `cauterule list` | Shows table with id, trigger, status, hits, tags |
| 2.6 | `cauterule show <id>` | Prints full provenance (source → evidence → promotion) |
| 2.7 | `cauterule inject <task>` | Shows which rules would fire |
| 2.8 | `cauterule retire <id>` | Retires rule with reason, git commit |
| 2.9 | `cauterule history` | Prints timeline of promotions/retirements |
| 2.10 | `cauterule conflicts` | Lists detected conflicts |
| 2.11 | `cauterule validate` | Checks store integrity, passes |
| 2.12 | `cauterule health` | Prints health report |
| 2.13 | `cauterule search <query>` | Returns matching rules |
| 2.14 | `cauterule explain <id>` | Prints human-readable explanation |
| 2.15 | `cauterule config` | Views/edits configuration |
| 2.16 | `cauterule metrics` | Prints CLI summary |
| 2.17 | `cauterule report` | Generates markdown report |
| 2.18 | `cauterule pack list` | Lists installed rule packs |
| 2.19 | `cauterule pack info <name>` | Shows pack contents |
| 2.20 | `cauterule diff <id>` | Shows changes between versions |
| 2.21 | `cauterule audit <id>` | Prints provenance trail |
| 2.22 | `cauterule story` | Generates narrative blog post |
| 2.23 | `cauterule counterfactual` | Prints "would have avoided X failures" |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_cli.py -v` — all 23+ tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] Each command produces real effect (not echo)

---

## Task 30.6.3: Docker TUI Test (Textual Pilot)

**Issue:** #372
**Files:** `tests/field/test_docker_tui.py`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 3.1 ReviewScreen mounts | Textual Pilot starts ReviewScreen | Screen loads, no crash |
| 3.2 Candidates load | ReviewScreen populates from StoreManager | Candidates appear in list |
| 3.3 Evidence cards render | EvidenceCard widget shows "Prevented N, broke M" | Text appears in rendered output |
| 3.4 Confidence cards render | ConfidenceCard shows confidence/prevented/broken/hits/tags | All fields present |
| 3.5 Annotation screen | AnnotationScreen renders tag input, comment, category | All inputs present |
| 3.6 Batch review | BatchReviewScreen shows 10 candidates | 10 items rendered |
| 3.7 Filter works | FilterWidget narrows by tag/status/confidence | Filtered list shorter |
| 3.8 Approve promotes | Approve triggers `execute_promotion` | Rule file created |
| 3.9 Reject advances | Reject skips to next candidate | Index advanced |
| 3.10 Keybindings | q=quit, r=review, f=filter, a=approve, x=reject | Each key fires correct action |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_tui.py -v` — all 10+ tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] TUI runs headless (no DISPLAY needed)

---

## Task 30.6.4: Docker MCP Server Test

**Issue:** #373
**Files:** `tests/field/test_docker_mcp.py`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 4.1 MCP server starts | `cauterule mcp` launches in background | Process starts, listens on stdio |
| 4.2 `get_matching_rules(task)` | Send request, get response | Returns rules whose trigger is substring of task |
| 4.3 `get_rule(id)` | Send request with valid ID | Returns single rule with full provenance |
| 4.4 `list_rules(filter)` | Send request with optional filter | Returns filtered rule list |
| 4.5 `report_failure(trajectory)` | Send trajectory JSON | Returns candidate info, triggers extraction |
| 4.6 Stdio transport | JSON-RPC over stdin/stdout | Messages sent and received correctly |
| 4.7 HTTP transport | JSON-RPC over HTTP (if configured) | HTTP requests/responses work |
| 4.8 Error handling | Invalid ID, missing task, malformed JSON | Returns proper error responses |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_mcp.py -v` — all 8+ tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] All 4 MCP tools return correct responses

---

## Task 30.6.5: Docker Pipeline E2E Test

**Issue:** #374
**Files:** `tests/field/test_docker_pipeline.py`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 5.1 Init project | `cauterule init` creates scaffold | All expected files exist |
| 5.2 Extract dry-run | `cauterule extract --dry-run` on seeded trajectory | CandidateRule produced |
| 5.3 Replay test | `cauterule test` on candidate | EvidenceReport with precision/recall |
| 5.4 Promote | `cauterule promote` | Rule YAML written, git commit created |
| 5.5 List | `cauterule list` | Promoted rule shows in table |
| 5.6 Inject | `cauterule inject --task <matching>` | Rule fires, shown in output |
| 5.7 Show | `cauterule show <id>` | Full provenance displayed |
| 5.8 Health | `cauterule health` | Reports healthy store |
| 5.9 Validate | `cauterule validate` | Zero errors |
| 5.10 Hash check | Read rule YAML, verify `promotion_commit` | 40-char hex hash, not UUID |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_pipeline.py -v` — all 10 tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] Full loop completes in <60 seconds

---

## Task 30.6.6: Docker Redaction Verification Test

**Issue:** #375
**Files:** `tests/field/test_docker_redaction.py`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 6.1 API key redaction | Trajectory with `api_key=sk-1234567890` | `sk-1234567890` not in written file |
| 6.2 Token redaction | Trajectory with `token=ghp_abc123` | `ghp_abc123` not in written file |
| 6.3 Password redaction | Trajectory with `password=supersecret` | `supersecret` not in written file |
| 6.4 Redacted flag | After write, trajectory has `redacted: true` | `traj.redacted == True` |
| 6.5 Export redaction | Export functions produce no secrets | grep for secret patterns returns empty |
| 6.6 `@watch` decorator redaction | Decorated function with secret in kwargs | Secret not in captured trajectory |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_redaction.py -v` — all 6+ tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] 0 secrets in trajectory files or exports

---

## Task 30.6.7: Docker Export/Import Round-Trip Test

**Issue:** #376
**Files:** `tests/field/test_docker_export_import.py`

| Sub-task | Format | Exit Criteria |
|----------|--------|---------------|
| 7.1 Export .cursorrules | `cauterule export --format cursor` | Valid file, parsable |
| 7.2 Export CLAUDE.md | `cauterule export --format claude` | Valid markdown |
| 7.3 Export AGENTS.md | `cauterule export --format agents` | Valid markdown |
| 7.4 Export .windsurfrules | `cauterule export --format windsurf` | Valid file |
| 7.5 Export aider.conf.yml | `cauterule export --format aider` | Valid YAML |
| 7.6 Export markdown | `cauterule export --format markdown` | Valid markdown |
| 7.7 Export JSON | `cauterule export --format json` | Valid JSON |
| 7.8 Active-only filter | Default export excludes retired | Only `status=="active"` rules |
| 7.9 Include-retired flag | `--include-retired` includes all | Retired rules present |
| 7.10 Import .cursorrules | Import from .cursorrules | CandidateRule produced |
| 7.11 Import CLAUDE.md | Import from CLAUDE.md | CandidateRule produced |
| 7.12 Import AGENTS.md | Import from AGENTS.md | CandidateRule produced |
| 7.13 Import chat history | Parse past corrections | CandidateRule produced |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_export_import.py -v` — all 13+ tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] Round-trip preserves id, when, do, tags, confidence

---

## Task 30.6.8: Docker Git Integration Test

**Issue:** #377
**Files:** `tests/field/test_docker_git.py`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 8.1 Git init | `git init` in temp dir | Repo created |
| 8.2 Promote rule | `cauterule promote` creates rule YAML | File exists |
| 8.3 Commit message | `git log --oneline` | Shows `promote: <id>` |
| 8.4 Hash in YAML | Read YAML `promotion_commit` field | 40-char hex string |
| 8.5 Hash matches | `git rev-parse HEAD` | Matches hash in YAML |
| 8.6 Rollback | `git revert HEAD --no-edit` | Executes without error |
| 8.7 Rule removed | After rollback, rule YAML gone | File does not exist |
| 8.8 Validate after rollback | `cauterule validate` | Passes with zero errors |
| 8.9 Retire creates commit | `cauterule retire` | `git log` shows new commit |
| 8.10 History | `cauterule history` | Shows timeline of events |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_git.py -v` — all 10 tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] Real git hash in YAML, not UUID

---

## Task 30.6.9: Docker Loop Orchestrator Test

**Issue:** #378
**Files:** `tests/field/test_docker_loop.py`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 9.1 run_loop returns ID | `run_loop(trajectory, config)` | Returns string (rule ID) |
| 9.2 Rule file created | Rule YAML exists in `rules/` | File exists |
| 9.3 Git commit exists | `git log` shows promotion commit | Commit exists |
| 9.4 9 stages execute | Check provenance for all 9 stages | All stages present |
| 9.5 Empty trajectory | `run_loop` with empty trajectory | No crash, graceful handling |
| 9.6 Non-extractable | Trajectory with no lesson | No rule promoted, returns None |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_loop.py -v` — all 6 tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] Loop produces real promoted rule

---

## Task 30.6.10: Docker Multi-Environment Test

**Issue:** #379 (#383 also)
**Files:** `tests/field/test_docker_multienv.py`

| Sub-task | Python | Exit Criteria |
|----------|--------|---------------|
| 10.1 Build 3.11 image | `docker build --build-arg PYTHON_VERSION=3.11` | Builds without errors |
| 10.2 Run tests on 3.11 | `pytest tests/ -m "not slow"` | All pass |
| 10.3 Build 3.12 image | `docker build --build-arg PYTHON_VERSION=3.12` | Builds without errors |
| 10.4 Run tests on 3.12 | `pytest tests/ -m "not slow"` | All pass |
| 10.5 Build 3.13 image | `docker build --build-arg PYTHON_VERSION=3.13` | Builds without errors |
| 10.6 Run tests on 3.13 | `pytest tests/ -m "not slow"` | All pass |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_multienv.py -v` — all 6 tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] 0 version-specific failures across 3.11/3.12/3.13

---

## Task 30.6.11: Docker Compose Orchestration

**Issue:** #384
**Files:** `tests/field/test_docker_compose.py`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 11.1 Start all services | `docker compose up -d` | All 3 services start |
| 11.2 Demo completes | `docker compose up cauterule-demo` | Exits 0, rule promoted |
| 11.3 MCP accepts connections | Connect to MCP stdio/HTTP | `get_matching_rules` returns results |
| 11.4 Test service passes | `docker compose up cauterule-test` | All tests pass, exits 0 |
| 11.5 Clean shutdown | `docker compose down` | All containers removed |

**Exit gate:**
- [ ] `pytest tests/field/test_docker_compose.py -v` — all 5 tests pass
- [ ] `ruff check tests/field/` — clean
- [ ] All 3 services work together

---

## Task 30.6.12: Test Orchestration Script

**Issue:** #380
**Files:** `scripts/docker_field_test.sh`

| Sub-task | Description | Exit Criteria |
|----------|-------------|---------------|
| 12.1 Script exists | `scripts/docker_field_test.sh` | Executable, in repo |
| 12.2 Build stage | Builds Docker image | Exits 0 |
| 12.3 All 15 stages | Runs all stages sequentially | Each reports pass/fail |
| 12.4 Summary | Prints "X passed, Y failed, Z total" | Output present |
| 12.5 Exit code 0 | All stages pass | `$?` is 0 |
| 12.6 Exit code 1 | Any stage fails | `$?` is 1 |
| 12.7 `--stage <N>` | Runs single stage | Only that stage runs |
| 12.8 `--skip-build` | Reuses existing image | Skips build step |
| 12.9 `--verbose` | Detailed output | Extra output present |

**Exit gate:**
- [ ] `scripts/docker_field_test.sh --help` prints usage
- [ ] `scripts/docker_field_test.sh --stage 1` runs only stage 1
- [ ] `scripts/docker_field_test.sh --skip-build` skips build
- [ ] `bash scripts/docker_field_test.sh` completes all stages
- [ ] `ruff check scripts/` — clean

---

## M30.6 Docker Field Test Exit Gate

Before M30.6 closes, ALL of the following must be true:

- [x] 30.6.13: Test fixtures package — all 12 sub-tasks complete
- [x] 30.6.14: docker-compose.yaml updated — all 6 sub-tasks complete
- [x] 30.6.1: Docker build & install — all 5 sub-tasks complete
- [x] 30.6.2: Docker CLI integration — all 23 sub-tasks complete
- [x] 30.6.3: Docker TUI test — all 10 sub-tasks complete
- [x] 30.6.4: Docker MCP server test — all 8 sub-tasks complete
- [x] 30.6.5: Docker pipeline E2E test — all 10 sub-tasks complete
- [x] 30.6.6: Docker redaction test — all 6 sub-tasks complete
- [x] 30.6.7: Docker export/import test — all 13 sub-tasks complete
- [x] 30.6.8: Docker git integration test — all 10 sub-tasks complete
- [x] 30.6.9: Docker loop test — all 6 sub-tasks complete
- [x] 30.6.10: Docker multi-env test — all 6 sub-tasks complete
- [x] 30.6.11: Docker compose test — all 5 sub-tasks complete
- [x] 30.6.12: Orchestration script — all 9 sub-tasks complete
- [x] `pytest tests/field/ -v` — all pass
- [x] `ruff check tests/field/ scripts/` — clean
- [x] `mypy tests/field/` — clean
- [x] All 14 GitHub issues (#370-#384) closed
- [x] Commit: `milestone: M30.6 Docker field test complete`
- [x] Push to main