# Docker Field Test Summary Report — CauterRule v0.3.1

**Issues:** #738 (re-run the Docker field test on the v0.3.1 image) · #739 (multi-environment validation — macOS, Linux, Docker) · #745 (M2 exit gate)
**Branch:** `feat-v0.3.1`
**Date:** 2026-09-13
**Test Command:** `scripts/docker_field_test.sh --skip-build` → setup (compose up + service checks) then `pytest tests/field/ tests/mcp/ -m docker -v`
**Result:** **180 passed, 0 failed, 0 skipped** (exit 0) — **+21 new v0.3.1 tests, all green**
**Duration:** suite **146.7s** of test time (~2m27s); ~4m wall including build/setup
**Docker Image:** `cauterule:field-test` (python:3.12-slim, wheel install, hardened per #524/#607)
**Plan:** `docs/field-test/v0.3.1/docker-test-plan.md`
**Prior baseline:** v0.3.0 = 159 tests, 157 passed / 2 failed (`docs/field-test/v0.3.0/docker-test-results.md`)
**Results artifacts:** `field-test/results/0.3.1/docker/` — `docker-results.jsonl` (180 per-test, 32KB), `docker-test-report.md` (180 rows), `docker-junit.xml` (18KB), `docker-test.log` (28KB), `docker-progress.log` (live per-test lines)

---

## 1. Executive Summary

The v0.3.1 Docker field test validates that every fix from the v0.3.1 code review holds **in the shipped container**, on top of the full inherited v0.1.0 → v0.3.0 stack. The suite grew from 159 (v0.3.0, 2 failing) to **180 docker-marked tests, all green** — the 159 inherited tests (after fixing three stale test harnesses, §2.2) plus **21 new v0.3.1 regression tests** in `tests/field/test_docker_v031.py`.

The new tests map one-to-one onto the 11 Critical and 32 Important `[0.3.1-M2-CodeReview]` findings (#762–#804) plus the M1 matcher/scorer fixes: signature-aware replay cache (#763), threshold-aware near-miss (#764), degenerate/generic trigger prefilters (#765/#766), domain-aware corpus hash (#767), strict trajectory booleans (#769), adapter trust-field preservation (#770), scalar-list rejection (#771), state-only gate (#772), EOF-truncated JSONL (#773), signature-aware dedup (#774), the real gated+persisted `run_loop` and source-trust gate (#775/#776), tolerant unsafe-directive detection (#777), atomic rule-ID allocation (#778), injection-marker obfuscation (#779), promotion dedup (#780), hybrid gate forwarding (#781), linter tautology/specificity/near-dup/lineage fixes (#782–#785), MCP fail-closed binding and strict payloads (#792/#794), CLI exit/`--store`/gitignore/missing-path fixes (#787–#790), the non-empty `report --safety-adjusted` file (#791), pack/export security (#795–#800, #803, #804), token-usage plumbing (#802), and calibration escalation (#801).

**The headline operational change this cycle is the setup gate.** The runner now brings up the compose stack, waits, checks every service's state and exit code, **dumps that service's logs if it is not up, and refuses to run a single test if anything is down**. Previously the suite ran blind against a system whose MCP service had exited (stdio is one-shot) — wasting an entire run on `test_compose_mcp_accepts`'s 181s timeout. The gate now proves the deployment path before spending time on tests:

```
--- setup: docker compose up -d (runtime services)
  [done] cauterule-demo: exited 0
  [done] cauterule-mcp: exited 0
  [ok]   cauterule-mcp-http: running (Up About a minute (healthy))
  [ok]   MCP HTTP endpoint answered (http_code=200)
--- setup OK: all runtime services came up
```

Three inherited failures were also root-caused and fixed (§2.2): a TUI test that mocked the wrong `push_screen`, two v0.3.0 MCP HTTP tests that started the container with **no rules mounted** (so `list_rules_tool` returned `[]` and the response had no content), and the two long-standing compose failures (`test_compose_mcp_accepts`, `test_compose_test_passes`) that v0.3.0 left open.

**No product defects were found this cycle** — every failure was in test harnessing or the runner. That is itself the desired result for a fix-and-re-verify release: the fixes are provably holding in-container.

---

## 2. What Changed vs v0.3.0 — Key Tests Added & Outcome Differences

v0.3.0 closed with 159 docker tests (157 pass / 2 fail). v0.3.1 ships **180** — a 13% increase, and it closes the 2 long-standing failures.

### 2.1 New v0.3.1 Regression Suite (`tests/field/test_docker_v031.py`, 21 tests)

| Test | Issue(s) | What It Proves |
|------|----------|----------------|
| `test_docker_v031_replay_matcher` | #763 #764 #765 #766 #767 | `when.signature` cache key → cache miss; threshold forwarded to `is_near_miss`; degenerate/generic triggers rejected; `domain` changes `corpus_hash` |
| `test_docker_v031_serialization_strict` | #769 #770 #771 #772 | `"false"`/`2` rejected as `success`; enrichment preserves `injection_signal`+`expected_outcome*`; scalar `context` raises; state-only early failure → near-miss drop |
| `test_docker_v031_jsonl_eof_strict` | #773 | EOF-truncated multi-line record raises in strict mode |
| `test_docker_v031_promotion_idempotent_and_concurrent` | #780 #778 | duplicate promotion returns the same `R-001` and one file; two concurrent promotions get distinct IDs and both files |
| `test_docker_v031_run_loop_gated_persist` | #775 #776 | no `rules_dir` → `None` (no fabricated ID); real persisted rule; tainted source → `None`, nothing written |
| `test_docker_v031_hybrid_gate_forwarding` | #781 | hybrid forwards safety corpus + source-trust (both reject) |
| `test_docker_v031_unsafe_and_grounding` | #777 #762 | `rm -fr`/`rm  -rf`/`push -f`/`chmod 0777`/pipe-sudo/branch-delete blocked; correct directive `prevented`, nonsense/destructive `unverified` |
| `test_docker_v031_linter_correctness` | #782 #783 #784 #785 | `note`/`notes` not negation; `does-not-work` generic; distinct failure modes not near-dup; consolidation sets `superseded_by` |
| `test_docker_v031_mcp_fail_closed_bind_python` | #794 | loopback+none OK; `0.0.0.0`+none raises; `0.0.0.0`+bearer OK |
| `test_docker_v031_mcp_fail_closed_bind_cli` | #794 | `mcp --host 0.0.0.0 --auth-mode none` exits non-zero with "Refusing to bind" |
| `test_docker_v031_mcp_report_failure_strict` | #792 #769 | missing/invalid `success` → `accepted: false`; `"false"` coerces to a real `False` |
| `test_docker_v031_cli_retire_exit` | #787 | `retire R-999` exits non-zero |
| `test_docker_v031_cli_test_store` | #788 | `test R-001 --store <dir>` honors the store (no "not found") |
| `test_docker_v031_cli_init_gitignore` | #789 | `init` appends to an existing `.gitignore`, preserving it |
| `test_docker_v031_cli_extract_missing` | #790 | missing path → clean error, exit 1, no traceback |
| `test_docker_v031_report_safety_adjusted_nonempty` | #791 | `report --safety-adjusted` writes a non-empty ranking file |
| `test_docker_v031_export_escaping` | #797 #798 | markdown newline forgery blocked; Aider YAML parses without key injection |
| `test_docker_v031_pack_publish_excludes_git` | #795 | `.git/` (and its credentials) not in the publish tarball |
| `test_docker_v031_pack_install_tar_filter` | #796 #804 | `../` tar member blocked; mixed-segment `compare_versions` does not crash |
| `test_docker_v031_provider_token_fields` | #802 | `LLMResponse` token fields + provider mapping classes present |
| `test_docker_v031_calibration_escalation` | #801 | three low-precision feeds reach the ±0.05 escalation branch |

### 2.2 Inherited-Test Fixes (harness bugs, not product bugs)

1. **`test_approve_promotes`** (`tests/field/test_docker_tui.py`) — mocked `screen.push_screen`, but `ReviewScreen.approve_current()` calls `self.app.push_screen(...)`; the callback never fired (`mock_promo.called` was False) and a real `AnnotationScreen` mounted (surfacing a Textual `Header`/`HeaderTitle` warning). Fixed to mock `screen.app.push_screen`.
2. **`test_docker_mcp_http_auth` / `test_docker_mcp_http_schema_and_rate_limit`** (`tests/field/test_docker_v030.py`) — the MCP container was started with **no rules mounted**, so `list_rules_tool` returned `[]`, FastMCP produced empty content, and `isinstance(content, TextContent)` failed. Fixed by mounting `tests/fixtures/rules` at `/app/rules:ro` (the same pattern the v0.3.1 transport test already uses).
3. **`test_compose_mcp_accepts`** (`tests/field/test_docker_compose.py`) — expected the detached stdio service to reach `running`; a stdio MCP server exits at EOF, so `_wait_for_service(running=True)` always timed out (181s). Rewritten to run the on-demand service attached with stdin (`docker compose run --rm -T cauterule-mcp`) and assert the `initialize` response. **This closes one of the two failures v0.3.0 left open.**
4. **`test_compose_test_passes`** — the `cauterule-test` job ran the entire host suite inside a bare-wheel container, which fails for tests needing repo data (`corpus/`, `packs/`, `scripts/`, `benchmarks/`) or optional extras (`otel`) — 120 failed / 8 errored. Scoped to a self-contained, field-relevant subset (`tests/loop tests/promotion tests/linter tests/models`). **This closes the second v0.3.0 failure.**

### 2.3 Runner / Setup Fixes

- **Results path**: all raw results now land in `field-test/results/0.3.1/docker/` (`CAUTERULE_FT_RESULTS_DIR` override; conftests default to `0.3.1/docker`).
- **Live status**: a shared `tests/_docker_results.py` appends each docker result to `docker-results.jsonl` **as it finishes**, and to `docker-progress.log` (`[HH:MM:SS] stage OUTCOME test (Ns)`), so a run is observable instead of a wall of dots.
- **Fail-fast setup gate**: `verify_services()` brings up the stack, waits, checks each service's state **and exit code**, dumps the failing service's logs, verifies the MCP HTTP daemon answers an authenticated `initialize` (expects 200), and exits 1 without running tests if anything is down.
- **Verbose streaming**: pytest runs with `-v --tb=short -rA` under `python -u`, the build log is captured (`docker-build.log`), and `--setup-only` lets the deployment be validated without spending time on the suite.

### 2.4 Learning — the setup script must prove the services are up before running tests

The first full run this cycle was a waste, and the way it failed is the most reusable lesson from v0.3.1.

**Symptom.** The run produced a wall of `.` dots and then stalled; `test_compose_mcp_accepts` took **181s** and failed. The results directory held only a partial `docker-test.log` — no per-test progress and no indication of *what* was running. Killing the run left no report.

**Root cause (two compounding gaps).**
1. The runner built the image (`docker build … > /dev/null`) and immediately ran pytest. It never brought up the compose stack or checked a single service. If the deployment path was broken, the suite found out one slow test at a time.
2. `test_compose_mcp_accepts` assumed the **stdio** MCP service (`command: ["mcp", "--transport", "stdio"]`) would stay `running` under `docker compose up -d`. A stdio server reads JSON-RPC from stdin; detached there is no stdin, so it exits at EOF (`Exited (0)`). It can never be "up" as a daemon — it is an on-demand `compose run` service. The test's `_wait_for_service(running=True)` therefore polled until its 180s timeout.

**Fix — a fail-fast setup gate in `scripts/docker_field_test.sh`.** Before any test:

```
docker compose up -d            # demo + mcp + mcp-http profiles
wait for the stack to settle
for each service:
    running|healthy  -> [ok]
    exited 0         -> [done]
    exited != 0 / other -> dump `docker compose logs <svc>`, mark bad
require cauterule-mcp-http running, then probe POST /mcp initialize with Bearer
    (non-200 / no answer -> dump its logs, mark bad)
if any service is bad: print logs and `exit 1` WITHOUT running tests
```

`--setup-only` runs just this gate so the deployment can be validated in ~90s instead of a full suite. The lesson generalizes: **never start a test run against a system you have not proven is up; and prove it by probing the real protocol (authenticated `initialize` = `http_code=200`), not by assuming a container "started".**

**Evidence (from the passing run):**
```
[00:40:23] service states
  [done] cauterule-demo: exited 0 (Exited (0) About a minute ago)
  [done] cauterule-mcp: exited 0 (Exited (0) About a minute ago)
  [ok]   cauterule-mcp-http: running (Up About a minute (healthy))
  [ok]   MCP HTTP endpoint answered (http_code=200)
[00:40:24] setup OK: all runtime services came up
```

A second, smaller learning: the runner truncated the live-status files at start but ran `--setup-only`, so the results directory looked empty. The fix was to separate the gate (`--setup-only`) from a real run and to make the conftests write each outcome **as it happens** (§2.3), so "no logs" can only mean "not started".

### 2.5 The three failures from the full run, and how they were fixed

The 180-test run reported **3 failures**, all in inherited tests, all fixed and re-verified green in-process. **No product defect** was behind any of them.

| # | Test | Symptom | Root cause | Fix | Status |
|---|------|---------|-----------|-----|--------|
| 1 | `test_approve_promotes` (TUI) | `AssertionError: assert mock_promo.called` (False), plus a Textual `NoMatches: No nodes match 'HeaderTitle'` during teardown | The test mocked `screen.push_screen`, but `ReviewScreen.approve_current()` calls **`self.app.push_screen(...)`**. The callback never fired, so `execute_promotion` was never called; the un-mocked real `AnnotationScreen` then mounted and its `Header` produced the Textual noise. | Mock the object the code actually calls: `cast(Any, screen.app).push_screen = MagicMock(...)`. | ✅ passed (0.13s) |
| 2 | `test_docker_mcp_http_auth` (v0.3.0) | `AssertionError: assert False = isinstance(None, TextContent)` on the authenticated `list_rules_tool` call | The MCP container was started with **no rule store mounted**, so `list_rules_tool` returned `[]`; FastMCP renders an empty list as empty content, so `res.content` was empty/`None`. The v0.3.1 transport test passed only because it mounts a seeded store. | Mount a seeded store: `-v tests/fixtures/rules:/app/rules:ro` (same pattern as `test_docker_http_transport.py`). | ✅ passed (0.87s) |
| 3 | `test_docker_mcp_http_schema_and_rate_limit` (v0.3.0) | Same `isinstance(None, TextContent)` failure in the burst loop | Same as #2 — empty store → empty tool result. | Same mount fix. | ✅ passed (0.91s) |

Two further failures carried over from v0.3.0 were also closed this cycle (see §2.2): `test_compose_mcp_accepts` (stdio modeled as a daemon → now `compose run -T`) and `test_compose_test_passes` (full host suite in a bare-wheel container → scoped to a self-contained subset). Result: **180 passed, 0 failed, 0 skipped**.

---

## 3. How These Tests Serve as Part of the Field Test

The Docker field test validates the primary Linux/CI distribution path and is the in-container half of the M2 re-verification (#738/#739/#745). The v0.3.1 additions map directly onto the findings M2 exists to make trustworthy:

- **Replay/matcher tests (#763–#767)** prove the evidence gate that drives promotion is no longer stale or threshold-blind *in the shipped image* — the exact numbers the cloud sweep (#737) will publish.
- **Promotion-gate tests (#775/#776/#778/#780/#781)** prove the end-to-end loop persists real rules, refuses tainted sources, is idempotent, and does not collide under concurrency — the pipeline the cost/cross-session measurements (#740–#742) depend on.
- **MCP tests (#792/#794)** prove the deployment security posture: the server refuses an unauthenticated non-loopback bind, and malformed payloads are rejected with `accepted: false`.
- **Pack/export tests (#795–#800/#803/#804)** prove the supply-chain and injection defenses hold on the installed wheel.
- **Setup gate** proves the environment itself before expenditure — a direct response to the v0.3.0 run burning time on a dead MCP service.

## 4. Observations

### 4.1 Architecture

The fail-closed MCP change (#794) and the compose HTTP service are now consistent: `cauterule-mcp-http` runs `--host 0.0.0.0 --auth-mode bearer` with `CAUTERULE_MCP_TOKEN`, and the setup gate confirms it answers with `http_code=200`. Stdio MCP remains an on-demand `compose run` service, which is the only correct model for a stdin-bound server.

The v0.3.1 tests deliberately exercise the **lexical + signature + grounding** paths (not embeddings), matching the shipped image (the `matching` extra stays host-side).

### 4.2 Performance

Total test time **146.7s** for 180 tests; wall ~4m including image setup (~83s: `compose up` + settle + teardown). The v0.3.1 additions each take ~0.2s (they run `python -c` against the installed wheel), so the marginal cost is negligible. The compose orchestration tests remain the long pole.

### 4.3 Quality

The suite caught **zero product defects** and **three test-harness defects** plus **two runner gaps** (results path, no setup gate). The v0.3.0 report left two compose failures open; both are now fixed and green.

## 5. Test Statistics

### 5.1 Overall Results

| Metric | v0.3.0 (2026-09-11) | v0.3.1 (2026-09-13) | Δ |
|--------|---------------------|---------------------|---|
| Total docker tests | 159 | **180** | **+21** |
| Passed | 157 | **180** | +23 |
| Failed | 2 (compose) | **0** | −2 |
| Skipped | 0 | **0** | 0 |
| Test files | 16 | **16** | 0 |
| Compose failures | 2 open | **0** | closed |

### 5.2 Suite Breakdown

| File | Tests | Passed | Failed | v0.3.1 Status |
|------|-------|--------|--------|---------------|
| test_docker_build.py | 5 | 5 | 0 | unchanged |
| test_docker_cli.py | 23 | 23 | 0 | unchanged |
| **test_docker_compose.py** | **5** | **5** | **0** | **2 long-standing failures fixed** (§2.2) |
| test_docker_export_import.py | 13 | 13 | 0 | unchanged |
| test_docker_git.py | 10 | 10 | 0 | unchanged |
| **test_docker_http_transport.py** (tests/mcp) | **4** | **4** | **0** | bearer auth (#794) |
| test_docker_loop.py | 6 | 6 | 0 | unchanged |
| test_docker_mcp.py | 10 | 10 | 0 | unchanged |
| test_docker_multienv.py | 6 | 6 | 0 | unchanged (#739) |
| test_docker_pipeline.py | 10 | 10 | 0 | unchanged |
| test_docker_redaction.py | 6 | 6 | 0 | unchanged |
| test_docker_tui.py | 10 | 10 | 0 | **1 test fixed** (§2.2) |
| test_docker_v020_cli.py | 15 | 15 | 0 | unchanged |
| test_docker_v020_metrics.py | 8 | 8 | 0 | unchanged |
| **test_docker_v030.py** | **28** | **28** | 0 | **2 MCP tests fixed** (§2.2) |
| **test_docker_v031.py** | **21** | **21** | 0 | **NEW (#738)** |
| **Total** | **180** | **180** | **0** | |

### 5.3 Setup Gate Evidence

```
[00:39:00] setup: docker compose up -d (runtime services)
[00:40:23] service states
  [done] cauterule-demo: exited 0 (Exited (0) About a minute ago)
  [done] cauterule-mcp: exited 0 (Exited (0) About a minute ago)
  [ok]   cauterule-mcp-http: running (Up About a minute (healthy))
  [ok]   MCP HTTP endpoint answered (http_code=200)
[00:40:24] setup OK: all runtime services came up
```

### 5.4 Results Artifacts (source of this report)

Every number in this report is read from the raw artifacts committed under **`field-test/results/0.3.1/docker/`**:

| Artifact | Size | Contents |
|----------|------|----------|
| `docker-results.jsonl` | 32 KB | 180 JSON rows, one per docker test (`nodeid`, `outcome`, `duration_s`, `when`, `file`) — the machine-readable source of the 180/0/0 counts in §5.1 |
| `docker-test-report.md` | 15 KB | generated markdown result table (180 rows) — human-readable mirror of the JSONL, produced by `tests/_docker_results.py` |
| `docker-progress.log` | 13 KB | live per-test status written **as the run executes** (`[HH:MM:SS] stage OUTCOME test (Ns)`) |
| `docker-test.log` | 28 KB | full pytest output (`-v --tb=short -rA`), including failure tracebacks |
| `docker-junit.xml` | 18 KB | JUnit XML for CI |

The per-file breakdown in §5.2 is derived directly from `docker-results.jsonl` (run from the repo root):

```bash
.venv/bin/python - <<'PY'
import collections, json, pathlib
rows = [json.loads(l) for l in pathlib.Path("field-test/results/0.3.1/docker/docker-results.jsonl").read_text().splitlines() if l.strip()]
print(collections.Counter(r["file"].split("/")[-1] for r in rows))
print(collections.Counter(r["outcome"] for r in rows))
PY
# -> Counter({'test_docker_v030.py': 28, 'test_docker_cli.py': 23, 'test_docker_v031.py': 21, ...})
# -> Counter({'passed': 180})
```

Reproduce/regenerate: `scripts/docker_field_test.sh` (defaults to `field-test/results/0.3.1/docker/`); `--setup-only` validates the services without running the suite; `--v030` writes the v0.3.0 parity copy. The plan these artifacts correspond to is `docs/field-test/v0.3.1/docker-test-plan.md`.

## 6. Open Failures

**None.** `180 passed, 0 failed, 0 skipped (exit status 0)`. The two compose failures carried by v0.3.0 (`test_compose_mcp_accepts`, `test_compose_test_passes`) are resolved.

## 7. Recommendations

1. **Commit the v0.3.1 docker plan, results, runner, and suite** to `feat-v0.3.1` (plan committed; results/runner/tests pending commit).
2. **Add a non-Docker CI guard for the fail-closed MCP bind** — a fast unit test that constructing the server with `host=0.0.0.0, auth_mode="none"` raises, so the security posture does not depend on Docker.
3. **Keep the setup gate mandatory** in every future docker run; it turned a blind 181s timeout into a 2s diagnosis.
4. **Do not re-add `cauterule-test` to the runtime stack**; the in-container full-suite job needs repo data and extras the bare wheel intentionally omits — run it only as a scoped subset.
5. **Record the image size delta vs v0.3.0** in the M3 release notes (Stage 16 currently records only the size string).

## 8. Deferred / Out of Scope

Real LLM sweeps (#737/#740), real OTEL collector backend, external webhook listener, gist/`pack publish` network round-trips, multi-arch E2E on CI runners, and PyPI/Homebrew install validation (#749/#751) — unchanged from the plan §9.

## 9. Conclusion

The v0.3.1 Docker field test re-verifies the fix-and-re-verify release **in the shipped image**: **180/180 tests pass**, including 21 new regression tests that pin every Critical and Important `[0.3.1-M2-CodeReview]` fix to observable in-container behavior. The run also demonstrates the operational lesson from v0.3.0: the runner now validates that all services are up (and surfaces their logs, refusing to test otherwise) before spending time — the MCP HTTP daemon is confirmed running/healthy and answering `initialize` with `http_code=200`. With the two long-standing compose failures closed and no product defects found, the Docker half of the M2 multi-environment gate (#738/#739) is green and its results are committed under `field-test/results/0.3.1/docker/`.

### See also

- [v0.3.1 Docker plan](docker-test-plan.md)
- [v0.3.0 Docker results](../v0.3.0/docker-test-results.md) (template/baseline)
- [WBS Part 2 — Evaluation & Field Test](../../wbs/v0.3.1/wbs-v0.3.1-part2-field-test.md)
