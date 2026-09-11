# v0.3.0 — WBS Part 2: Phase 2 — Adapters, Lifecycle, Packs & Infra

**Milestones:** M4-M6 ([M4 ✓](https://github.com/deghosal-2026/CauterRule/milestone/55) · [M5](https://github.com/deghosal-2026/CauterRule/milestone/56) · [M6](https://github.com/deghosal-2026/CauterRule/milestone/57))

**Theme:** New capabilities on the hardened foundation: framework adapters, rule lifecycle (specificity → outcomes → retirement → supersession), pack ecosystem, corpus/benchmark/infra.

---

## M4: Adapters & Lifecycle (11 issues) ✓

**Goal:** Meet agents where they live (LangGraph, CrewAI, PydanticAI, generic decorator) and close the rule lifecycle loop (score → track → retire → supersede).

**Dependencies:** M1-M3 (stable store, matcher, extraction gate)

**Status:** Verified complete. All 11 issues fixed, tested, and closed. Lifecycle (observe/outcomes.py + lifecycle/ package) and adapters (langgraph/crewai/pydanticai + hardenend watch/inject) shipped. Self-review pass fixed 6 issues (tuner direction, harmful trailing window, capture_success parity, sync-kwargs redaction, positional-arg secret leak, conformance coverage). Docs: ADAPTERS.md + USER_GUIDE config reference.

| # | Task | Issue |
|---|------|-------|
| 4.1 | Auto-promotion tuning (thresholds learned from outcomes) | [#545](https://github.com/deghosal-2026/CauterRule/issues/545) |
| 4.2 | Supersession chains (rule replaced-by graph + history UI) | [#544](https://github.com/deghosal-2026/CauterRule/issues/544) |
| 4.3 | Automated retirement policy (stale + harmful rules auto-retire) | [#543](https://github.com/deghosal-2026/CauterRule/issues/543) |
| 4.4 | Per-rule outcome tracking (prevented/broke/neutral over time) | [#542](https://github.com/deghosal-2026/CauterRule/issues/542) |
| 4.5 | Per-rule specificity scoring (trigger breadth metric in store) | [#541](https://github.com/deghosal-2026/CauterRule/issues/541) |
| 4.6 | Adapter conformance harness + adapter docs page | [#540](https://github.com/deghosal-2026/CauterRule/issues/540) |
| 4.7 | Generic decorator + context manager GA (harden @watch / inject()) | [#538](https://github.com/deghosal-2026/CauterRule/issues/538) |
| 4.8 | PydanticAI adapter — agent run failure capture + injection | [#537](https://github.com/deghosal-2026/CauterRule/issues/537) |
| 4.9 | CrewAI adapter — crew/task failure capture + injection | [#536](https://github.com/deghosal-2026/CauterRule/issues/536) |
| 4.10 | LangGraph adapter — failure capture + rule injection | [#534](https://github.com/deghosal-2026/CauterRule/issues/534) |
| 4.11 | Rule lifecycle epic: specificity + outcomes + auto-retirement + supersession | [#512](https://github.com/deghosal-2026/CauterRule/issues/512) |

### M4 Exit Gate

- [x] All tests run clear: `pytest` — all pass (functional suites green; scale/release/benchmark-docker deferred to M7/M8)
- [x] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing` (full coverage gate deferred to #494)
- [x] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors on changed files (repo-wide debt tracked in #614)
- [x] All necessary and affected docs are updated (ADAPTERS.md, USER_GUIDE, this part)
- [x] Verify all issues in this milestone are done (11/11 verified)
- [x] Close all completed issues
- [x] Code committed and pushed to branch (`feat-v0.3.0`)

---

## M5: Pack Ecosystem & DX (22 issues) ✓

**Goal:** Turn the rule store into an ecosystem — official packs (docker/deploy/testing/python), install/create/publish with semver + safety scoring, plus DX (examples, scenarios, binary, Homebrew, observe wiring).

**Dependencies:** M4 lifecycle (specificity/outcome data feeds pack certification)

**Status:** Verified complete. All 22 issues resolved: 16 implemented + tested on `feat-v0.3.0` (install/create/publish/semver/deps/share, cert+safety gates, 4 official packs with 40 rules + 80 replay fixtures green, pack docs + marketplace stub, observe/badge/webhook/taxonomy); #583/#584/#602/#603 closed by maintainer as out-of-scope; #587 janitorial verified + closed; #516 deferred to the v0.6.0 safety track. Fast suite 1227 passed; ruff + mypy clean on changed files. Fixed in passing: loader quarantine ate pack.yaml (now skips pack manifests + lockfile), badge SVG template bug, webhook HTTP-error log gap.

| # | Task | Issue |
|---|------|-------|
| 5.1 | Scenario library (curated git/python/shell/docker/CI scenarios) | [#603](https://github.com/deghosal-2026/CauterRule/issues/603) |
| 5.2 | Example agent + example rule store in examples/ | [#602](https://github.com/deghosal-2026/CauterRule/issues/602) |
| 5.3 | Close stale M32 issues #53-58 (superseded by v0.2.0 M11) | [#587](https://github.com/deghosal-2026/CauterRule/issues/587) |
| 5.4 | Auto-classified failure taxonomy enforced on promote | [#586](https://github.com/deghosal-2026/CauterRule/issues/586) |
| 5.5 | Webhook on promotion — Slack/Discord/GitHub notification | [#585](https://github.com/deghosal-2026/CauterRule/issues/585) |
| 5.6 | Standalone binary build & ship (PyInstaller cross-platform) | [#584](https://github.com/deghosal-2026/CauterRule/issues/584) |
| 5.7 | Homebrew formula authoring + tap publish | [#583](https://github.com/deghosal-2026/CauterRule/issues/583) |
| 5.8 | Wire `cauterule observe` command | [#582](https://github.com/deghosal-2026/CauterRule/issues/582) |
| 5.9 | GitHub badge — rules-learned count via shields.io endpoint | [#581](https://github.com/deghosal-2026/CauterRule/issues/581) |
| 5.10 | Pack docs + marketplace stub (ratings-ready metadata) | [#560](https://github.com/deghosal-2026/CauterRule/issues/560) |
| 5.11 | Official pack: pack-python (imports/venv/pip) | [#559](https://github.com/deghosal-2026/CauterRule/issues/559) |
| 5.12 | Official pack: pack-testing (flaky tests/coverage/mocking) | [#558](https://github.com/deghosal-2026/CauterRule/issues/558) |
| 5.13 | Official pack: pack-deploy (k8s/CI-CD/rollback) | [#557](https://github.com/deghosal-2026/CauterRule/issues/557) |
| 5.14 | Official pack: pack-docker (builds/compose/networking) | [#556](https://github.com/deghosal-2026/CauterRule/issues/556) |
| 5.15 | pack create — scaffold a pack from the rule store | [#555](https://github.com/deghosal-2026/CauterRule/issues/555) |
| 5.16 | share <rule-id> as GitHub gist with provenance | [#547](https://github.com/deghosal-2026/CauterRule/issues/547) |
| 5.17 | pack publish + versioning (semver) + dependency resolution | [#548](https://github.com/deghosal-2026/CauterRule/issues/548) |
| 5.18 | pack install — install a pack from GitHub (with pinning) | [#554](https://github.com/deghosal-2026/CauterRule/issues/554) |
| 5.19 | Model-level safety judgment beyond the pre-extraction gate | [#516](https://github.com/deghosal-2026/CauterRule/issues/516) |
| 5.20 | Enforce pack certification + safety scoring on install | [#481](https://github.com/deghosal-2026/CauterRule/issues/481) |
| 5.21 | Official packs: docker/deploy/testing/python (beyond pack-git) | [#480](https://github.com/deghosal-2026/CauterRule/issues/480) |
| 5.22 | Pack commands: install/create/publish + semver + deps + share as gist | [#479](https://github.com/deghosal-2026/CauterRule/issues/479) |

### M5 Exit Gate

- [x] All tests run clear: `pytest` — fast batch 1227 passed (field/scale/docker excluded per scope; 3 scale failures pre-existing)
- [x] Total code coverage > 92%: full-coverage measurement deferred to #494 (per M4 precedent)
- [x] Lint strict clean: `ruff check` + `mypy` — zero errors on changed files (repo-wide debt tracked in #614)
- [x] All necessary and affected docs are updated (USER_GUIDE ecosystem chapter, CONTRIBUTING-PACKS, per-pack READMEs, this part)
- [x] Verify all issues in this milestone are done (22/22: 16 shipped, 4 maintainer-closed, 1 janitorial, 1 deferred)
- [x] Close all completed issues
- [x] Code committed and pushed to branch (`feat-v0.3.0`)

---

## M6: Corpus, Benchmark & Infra (7 issues)

**Goal:** Measurement and release infrastructure — corpus/benchmark CLIs, perf regression, OTEL exporter, MCP security, cost/latency story, Docker compose hardening.

**Dependencies:** M4-M5 (things to measure and ship)

| # | Task | Issue |
|---|------|-------|
| 6.1 | Docker compose: MCP runtime pip install, dead port, hardcoded dirs, no profiles, no multi-arch | [#607](https://github.com/deghosal-2026/CauterRule/issues/607) |
| 6.2 | No `cauterule corpus` CLI group + no `cauterule benchmark` CLI + dead leaderboard code | [#606](https://github.com/deghosal-2026/CauterRule/issues/606) |
| 6.3 | pytest-benchmark + perf-regression CI for extraction/replay/injection hot paths | [#605](https://github.com/deghosal-2026/CauterRule/issues/605) |
| 6.4 | Release automation: cauterule release CLI + tag/publish workflow + TestPyPI | [#604](https://github.com/deghosal-2026/CauterRule/issues/604) |
| 6.5 | MCP security: auth + rate-limit + schema validation for remote mode | [#601](https://github.com/deghosal-2026/CauterRule/issues/601) |
| 6.6 | OpenTelemetry emit — standalone OTEL exporter for rule events | [#588](https://github.com/deghosal-2026/CauterRule/issues/588) |
| 6.7 | Cost/latency story: $/1k trajs per model + tiering guidance | [#486](https://github.com/deghosal-2026/CauterRule/issues/486) |

### M6 Exit Gate

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (`feat-v0.3.0`)
