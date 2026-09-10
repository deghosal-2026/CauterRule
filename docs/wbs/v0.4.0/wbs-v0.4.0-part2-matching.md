# v0.4.0 — WBS Part 2: Phase 2 — Advanced Matching, Extraction & Fleet

**Milestones:** M3-M4 ([M3](https://github.com/deghosal-2026/CauterRule/milestone/60) · [M4](https://github.com/deghosal-2026/CauterRule/milestone/61))

**Theme:** The two biggest leaps: a matcher that understands meaning (embeddings + hybrid) and rules that travel across agents (registry, transfer, governance, fleet).

---

## M3: Advanced Matching & Extraction (8 issues)

**Goal:** Replace paraphrase-alias whack-a-mole with embedding semantic matching + hybrid weighting + local vector index, and calibrate confidence to empirical precision.

**Dependencies:** M1-M2 (integration trajectories + outcome data to train/tune against)

| # | Task | Issue |
|---|------|-------|
| 3.1 | Confidence calibration service (empirical precision mapping) | [#574](https://github.com/deghosal-2026/CauterRule/issues/574) |
| 3.2 | Cross-failure pattern detection (Nth failure → stronger rule) | [#573](https://github.com/deghosal-2026/CauterRule/issues/573) |
| 3.3 | Local rule embedding index (build/update/query CLI) | [#572](https://github.com/deghosal-2026/CauterRule/issues/572) |
| 3.4 | Hybrid matching (structured + semantic weights) + per-corpus tuning | [#571](https://github.com/deghosal-2026/CauterRule/issues/571) |
| 3.5 | Embedding-based semantic matcher (local model + API fallback) | [#570](https://github.com/deghosal-2026/CauterRule/issues/570) |
| 3.6 | Confidence calibration to empirical precision + calibration curves | [#511](https://github.com/deghosal-2026/CauterRule/issues/511) |
| 3.7 | Cross-failure pattern detection — 4th failure of type → stronger rule | [#510](https://github.com/deghosal-2026/CauterRule/issues/510) |
| 3.8 | Semantic + hybrid matching + local vector index + match --semantic (epic) | [#509](https://github.com/deghosal-2026/CauterRule/issues/509) |

### M3 Exit Gate

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (v0.4.0 branch — TBD, confirm before Phase 1)

---

## M4: Multi-Agent & Fleet (11 issues)

**Goal:** Rules leave a single agent behind — shared registry, cross-agent transfer with adaptation log, profiles, governance workflow, federation, inheritance, and fleet CLI.

**Dependencies:** M3 (transfer/adaptation needs the semantic matcher to judge similarity)

| # | Task | Issue |
|---|------|-------|
| 4.1 | Cross-pack + cross-fleet conflict detection | [#592](https://github.com/deghosal-2026/CauterRule/issues/592) |
| 4.2 | Rule inheritance — child agents inherit parent rules with overrides | [#591](https://github.com/deghosal-2026/CauterRule/issues/591) |
| 4.3 | cauterule fleet CLI (fleet status/health/rollout) | [#580](https://github.com/deghosal-2026/CauterRule/issues/580) |
| 4.4 | Rule federation (dedupe + conflict resolve across fleets) | [#579](https://github.com/deghosal-2026/CauterRule/issues/579) |
| 4.5 | Agent profiles — type/env/domain scoping for rules | [#578](https://github.com/deghosal-2026/CauterRule/issues/578) |
| 4.6 | Rule governance workflow (propose→approve→adopt) | [#577](https://github.com/deghosal-2026/CauterRule/issues/577) |
| 4.7 | Shared central rule registry (server + client) | [#576](https://github.com/deghosal-2026/CauterRule/issues/576) |
| 4.8 | Cross-agent rule transfer with adaptation log (A→B) | [#575](https://github.com/deghosal-2026/CauterRule/issues/575) |
| 4.9 | Rule DSL + pack marketplace + federated learning (epic) | [#515](https://github.com/deghosal-2026/CauterRule/issues/515) |
| 4.10 | Rule A/B testing + auto-tuning + rollback dashboard + provenance graph | [#514](https://github.com/deghosal-2026/CauterRule/issues/514) |
| 4.11 | Multi-agent fleet epic: transfer + shared registry + governance + profiles | [#513](https://github.com/deghosal-2026/CauterRule/issues/513) |

### M4 Exit Gate

- [ ] All tests run clear: `pytest` — all pass
- [ ] Total code coverage > 92%: `pytest --cov=src/cauterule --cov-report=term-missing`
- [ ] Lint strict clean: `ruff check .` + `mypy src/ tests/` — zero errors
- [ ] All necessary and affected docs are updated
- [ ] Verify all issues in this milestone are done
- [ ] Close all completed issues
- [ ] Code committed and pushed to branch (v0.4.0 branch — TBD, confirm before Phase 1)
