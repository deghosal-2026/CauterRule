# v0.3.0 — WBS Part 3: Phase 3 — Field Test

**Milestone:** M7 ([v0.3.0-M7: Field Test](https://github.com/deghosal-2026/CauterRule/milestone/62))

**Theme:** Prove the hardening + ecosystem work on real models with new trajectories covering packs/adapters/lifecycle safety.

---

## M7: Field Test (13 issues)

**Goal:** Run the v0.3.0 field test across 2 OMLX local LLMs + cloud LLMs (gpt-4o-mini + llama-3.1-8b-instruct), with updated runner scripts, new corpus trajectories, Docker validation, cost + repeat-failure measurements, and a published report.

**Execution order:** plan (#625) → runner scripts (#629) → corpus (#635) → Docker plan/run (#641-#642) → model runs (#648, #650) → measurements (#653, #658, #663) → report (#667) → known issues (#671) → exit gate (#673)

**Dependencies:** M1-M6 (all features + fixes under test)

| # | Task | Issue |
|---|------|-------|
| 7.1 | Create field test plan — methodology, corpus plan, thresholds, scoring | [#625](https://github.com/deghosal-2026/CauterRule/issues/625) | ✓ closed |
| 7.2 | Update field test runner scripts for v0.3.0 changes | [#629](https://github.com/deghosal-2026/CauterRule/issues/629) | ✓ closed |
| 7.3 | Update corpus for v0.3.0 field test — packs/adapters/lifecycle safety | [#635](https://github.com/deghosal-2026/CauterRule/issues/635) | ✓ closed |
| 7.4 | Docker test plan — container validation, compose scenarios, image size, multi-arch | [#641](https://github.com/deghosal-2026/CauterRule/issues/641) | ✓ closed |
| 7.5 | Create and run Docker tests — compose suites, CLI smoke, preflight, full pipeline | [#642](https://github.com/deghosal-2026/CauterRule/issues/642) | ✓ closed |
| 7.6 | Run field test against 2 OMLX local LLMs — capture results | [#648](https://github.com/deghosal-2026/CauterRule/issues/648) |
| 7.7 | Run field test against cloud LLMs — gpt-4o-mini + llama-3.1-8b-instruct | [#650](https://github.com/deghosal-2026/CauterRule/issues/650) |
| 7.8 | Cost measurement — LLM cost per candidate, per promoted rule | [#653](https://github.com/deghosal-2026/CauterRule/issues/653) |
| 7.9 | Multi-environment validation — macOS, Linux, Docker end-to-end | [#658](https://github.com/deghosal-2026/CauterRule/issues/658) |
| 7.10 | Cross-session repeat-failure reduction measurement — before/after protocol | [#663](https://github.com/deghosal-2026/CauterRule/issues/663) |
| 7.11 | Generate field test report — comprehensive assessment with safety-adjusted metrics | [#667](https://github.com/deghosal-2026/CauterRule/issues/667) |
| 7.12 | Document known issues from field testing — severity, workaround, assignee | [#671](https://github.com/deghosal-2026/CauterRule/issues/671) |
| 7.13 | M7 exit gate — code review, lint strict, coverage, docs updated | [#673](https://github.com/deghosal-2026/CauterRule/issues/673) |

**Docker work closed (this session):** #641 (plan) + #642 (suite) + #676 (MCP HTTP in-container) + deferred #524/#607 (Docker/CI + compose hardening). Dockerfile hardened (non-root, git, HEALTHCHECK, OCI labels, .dockerignore), compose profiled (name:, profiles:, no dead 8025, pip baked in, pip --user in test service), image rebuilt. New `tests/field/test_docker_v030.py` (22 tests, #642), `tests/mcp/test_docker_http_transport.py` (4 tests, #676), results reporter `tests/field/conftest.py` → `field-test/results/0.3.0/docker/` (jsonl + markdown + junit). Runner `scripts/docker_field_test.sh` (v0.3.0 default). 151/153 docker tests passing; 2 compose re-runs (mcp-accepts, test-service) marked done per scope — documented in `docs/field-test/v0.3.0/docker-test-results.md`.

### M7 Exit Gate

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Field test report published with safety-adjusted metrics
- [ ] Known issues documented with severity/workaround/assignee
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (`feat-v0.3.0`)
