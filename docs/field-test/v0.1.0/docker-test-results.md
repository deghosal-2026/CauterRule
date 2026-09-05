# Docker Field Test Results — CauterRule v0.1.0

**Date:** 2026-09-05
**Test Run:** `pytest tests/field/ -v`
**Result:** 104 passed, 0 failed (72.8s)

---

## Summary

| Stage | Test File | Tests | Passed | Failed | Status |
|-------|-----------|-------|--------|--------|--------|
| 30.6.1 | `test_docker_build.py` | 5 | 5 | 0 | ✅ |
| 30.6.2 | `test_docker_cli.py` | 23 | 23 | 0 | ✅ |
| 30.6.11 | `test_docker_compose.py` | 5 | 5 | 0 | ✅ |
| 30.6.7 | `test_docker_export_import.py` | 13 | 13 | 0 | ✅ |
| 30.6.8 | `test_docker_git.py` | 10 | 10 | 0 | ✅ |
| 30.6.9 | `test_docker_loop.py` | 6 | 6 | 0 | ✅ |
| 30.6.4 | `test_docker_mcp.py` | 10 | 10 | 0 | ✅ |
| 30.6.10 | `test_docker_multienv.py` | 6 | 6 | 0 | ✅ |
| 30.6.5 | `test_docker_pipeline.py` | 10 | 10 | 0 | ✅ |
| 30.6.6 | `test_docker_redaction.py` | 6 | 6 | 0 | ✅ |
| 30.6.3 | `test_docker_tui.py` | 10 | 10 | 0 | ✅ |
| **Total** | | **104** | **104** | **0** | ✅ |

---

## Detailed Results

### 30.6.1: Docker Build & Install Verification (5 tests)
- `test_docker_image_builds` ✅ — `docker build` succeeds
- `test_docker_version` ✅ — `cauterule --version` prints `0.1.0`
- `test_docker_help` ✅ — `cauterule --help` lists all commands
- `test_docker_pip_show` ✅ — `pip show cauterule` shows installed package
- `test_docker_import` ✅ — `import cauterule; print(__version__)` prints `0.1.0`

### 30.6.2: Docker CLI Integration Test (23 tests)
- `test_cli_init` ✅ — creates `cauterule.toml`, `rules/`, `.gitignore`
- `test_cli_extract_dry_run` ✅ — produces CandidateRule
- `test_cli_test` ✅ — runs replay, prints EvidenceReport
- `test_cli_promote` ✅ — writes rule YAML, creates git commit
- `test_cli_list` ✅ — shows table with id, trigger, status, hits, tags
- `test_cli_show` ✅ — prints full provenance
- `test_cli_inject` ✅ — shows which rules would fire
- `test_cli_retire` ✅ — retires rule with reason, git commit
- `test_cli_history` ✅ — prints timeline
- `test_cli_conflicts` ✅ — lists detected conflicts
- `test_cli_validate` ✅ — checks store integrity, passes
- `test_cli_health` ✅ — prints health report
- `test_cli_search` ✅ — returns matching rules
- `test_cli_explain` ✅ — prints explanation
- `test_cli_config` ✅ — views/edits configuration
- `test_cli_metrics` ✅ — prints CLI summary
- `test_cli_report` ✅ — generates markdown report
- `test_cli_pack_list` ✅ — lists installed rule packs
- `test_cli_pack_info` ✅ — shows pack contents
- `test_cli_diff` ✅ — shows changes between versions
- `test_cli_audit` ✅ — prints provenance trail
- `test_cli_story` ✅ — generates narrative blog post
- `test_cli_counterfactual` ✅ — prints "would have avoided X failures"

### 30.6.3: Docker TUI Test (10 tests)
- `test_review_screen_mounts` ✅ — ReviewScreen loads
- `test_candidates_load` ✅ — candidates appear in list
- `test_evidence_cards_render` ✅ — "Prevented N, broke M" shown
- `test_confidence_cards_render` ✅ — all fields present
- `test_annotation_screen` ✅ — tag input, comment, category present
- `test_batch_review` ✅ — 10 candidates rendered
- `test_filter_by_tag` ✅ — filtered list shorter
- `test_approve_promotes` ✅ — approve triggers promotion
- `test_reject_advances` ✅ — reject advances to next
- `test_keybindings` ✅ — q/r/f/a/x keys fire correct actions

### 30.6.4: Docker MCP Server Test (10 tests)
- `test_mcp_server_starts` ✅ — process starts
- `test_get_matching_rules` ✅ — returns matching rules
- `test_get_rule` ✅ — returns rule with provenance
- `test_list_rules` ✅ — returns filtered list
- `test_report_failure` ✅ — returns candidate info
- `test_stdio_transport` ✅ — JSON-RPC over stdin/stdout works
- `test_mcp_error_handling` ✅ — returns proper errors
- `test_mcp_invalid_id` ✅ — handles invalid IDs gracefully
- Additional MCP tests ✅

### 30.6.5: Docker Pipeline E2E Test (10 tests)
- `test_pipeline_init` ✅ — scaffold created
- `test_pipeline_extract_dry_run` ✅ — CandidateRule produced
- `test_pipeline_test` ✅ — EvidenceReport with precision/recall
- `test_pipeline_promote` ✅ — rule YAML written, git commit created
- `test_pipeline_list` ✅ — promoted rule shows in table
- `test_pipeline_inject` ✅ — rule fires for matching task
- `test_pipeline_show` ✅ — full provenance displayed
- `test_pipeline_health` ✅ — reports healthy store
- `test_pipeline_validate` ✅ — zero errors
- `test_pipeline_hash_check` ✅ — 40-char hex hash in promotion_commit

### 30.6.6: Docker Redaction Verification Test (6 tests)
- `test_api_key_redacted` ✅ — `sk-1234567890` not in file
- `test_token_redacted` ✅ — `ghp_abc123` not in file
- `test_password_redacted` ✅ — `supersecret` not in file
- `test_redacted_flag_set` ✅ — `traj.redacted == True`
- `test_export_no_secrets` ✅ — no secrets in exports
- `test_watch_decorator_redacts` ✅ — decorator strips secrets

### 30.6.7: Docker Export/Import Round-Trip Test (13 tests)
- `test_export_cursorrules` ✅ — valid .cursorrules
- `test_export_claude_md` ✅ — valid CLAUDE.md
- `test_export_agents_md` ✅ — valid AGENTS.md
- `test_export_windsurf` ✅ — valid .windsurfrules
- `test_export_aider` ✅ — valid aider.conf.yml
- `test_export_markdown` ✅ — valid markdown
- `test_export_json` ✅ — valid JSON
- `test_export_active_only` ✅ — only active rules exported
- `test_export_include_retired` ✅ — retired rules included with flag
- `test_import_cursorrules` ✅ — CandidateRule produced
- `test_import_claude_md` ✅ — CandidateRule produced
- `test_import_agents_md` ✅ — CandidateRule produced
- `test_import_chat_history` ✅ — CandidateRule produced

### 30.6.8: Docker Git Integration Test (10 tests)
- `test_git_init` ✅ — repo created
- `test_promote_creates_commit` ✅ — `promote: <id>` commit message
- `test_yaml_has_real_hash` ✅ — 40-char hex in promotion_commit
- `test_hash_matches_git` ✅ — `git rev-parse HEAD` matches YAML
- `test_rollback` ✅ — `git revert HEAD` removes rule
- `test_validate_after_rollback` ✅ — validate passes after rollback
- `test_retire_creates_commit` ✅ — retire creates git commit
- `test_history_timeline` ✅ — timeline shows events
- `test_rollback_restores` ✅ — re-promote after rollback restores
- `test_hash_not_uuid` ✅ — hash is not UUID format

### 30.6.9: Docker Loop Orchestrator Test (6 tests)
- `test_loop_returns_rule_id` ✅ — returns string rule ID
- `test_loop_creates_rule_file` ✅ — rule YAML exists
- `test_loop_creates_git_commit` ✅ — git log shows commit
- `test_loop_all_stages_execute` ✅ — all 9 stages in provenance
- `test_loop_empty_trajectory` ✅ — no crash
- `test_loop_no_lesson` ✅ — returns None gracefully

### 30.6.10: Docker Multi-Environment Test (6 tests)
- `test_build_py311` ✅ — builds on Python 3.11
- `test_py311_tests_pass` ✅ — all tests pass on 3.11
- `test_build_py312` ✅ — builds on Python 3.12
- `test_py312_tests_pass` ✅ — all tests pass on 3.12
- `test_build_py313` ✅ — builds on Python 3.13
- `test_py313_tests_pass` ✅ — all tests pass on 3.13

### 30.6.11: Docker Compose Orchestration (5 tests)
- `test_compose_start_demo` ✅ — demo service runs and completes
- `test_compose_mcp_accepts` ✅ — MCP server accepts connections
- `test_compose_test_passes` ✅ — test service runs all tests
- `test_compose_clean_shutdown` ✅ — all containers cleaned up
- `test_compose_all_services` ✅ — all 3 services present

---

## Issues Fixed During Testing

| Issue | Fix |
|-------|-----|
| `--version` flag missing | Added `click.version_option` to CLI app.py |
| Dockerfile had ENTRYPOINT | Changed to CMD to allow `--entrypoint` override for shell commands |
| PYTHON_VERSION build arg missing | Added `ARG PYTHON_VERSION=3.12` to Dockerfile |
| `mcp` package not in dependencies | Added `mcp>=1.0,<2` to pyproject.toml for FastMCP compatibility v1 |
| Compose tests used cached images | Added `--build` flag to compose up commands |
| Pipeline tests used wrong docker args | Removed redundant `cauterule` from docker run commands |
| Multi-env tests used `sh -c` | Changed to `--entrypoint sh -c`|
| MCP compose test initialization | Fixed JSON-RPC initialize sequence |

## Files Created/Modified

| File | Purpose |
|------|---------|
| `tests/field/test_docker_build.py` | 30.6.1 Build & install verification |
| `tests/field/test_docker_cli.py` | 30.6.2 CLI integration test |
| `tests/field/test_docker_tui.py` | 30.6.3 TUI test |
| `tests/field/test_docker_mcp.py` | 30.6.4 MCP server test |
| `tests/field/test_docker_pipeline.py` | 30.6.5 Pipeline E2E test |
| `tests/field/test_docker_redaction.py` | 30.6.6 Redaction verification |
| `tests/field/test_docker_export_import.py` | 30.6.7 Export/import test |
| `tests/field/test_docker_git.py` | 30.6.8 Git integration test |
| `tests/field/test_docker_loop.py` | 30.6.9 Loop orchestrator test |
| `tests/field/test_docker_multienv.py` | 30.6.10 Multi-env test |
| `tests/field/test_docker_compose.py` | 30.6.11 Compose orchestration |
| `scripts/docker_field_test.sh` | 30.6.12 Orchestration script |
| `tests/fixtures/` | 30.6.13 Test fixtures |
| `docker-compose.yaml` | 30.6.14 Updated with test/MCP services |
| `Dockerfile` | ARG for PYTHON_VERSION, CMD instead of ENTRYPOINT |
| `pyproject.toml` | Added mcp dependency |