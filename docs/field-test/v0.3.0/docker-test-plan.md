# Docker Field Test Plan — CauterRule v0.3.0

> **Goal:** Validate the full CauterRule v0.3.0 system end-to-end in Docker containers under field conditions. Extends the v0.2.0 Docker plan (`docs/field-test/v0.2.0/docker-test-plan.md`, 15 stages, ~1350 tests) with the v0.3.0 surface: pack ecosystem, adapters, rule lifecycle, MCP security + HTTP transport, OTEL exporter, corpus/benchmark CLIs, preflight cost estimation, and the container hardening fixes from #524 and #607.

**Issues:** #641 (Docker test plan) · #642 (create + run Docker tests) · dependents #524 (Docker/CI fixes) · #607 (compose/Dockerfile hardening).
**Deliverables:** `docs/field-test/v0.3.0/docker-test-plan.md` (this plan) → `docs/field-test/v0.3.0/docker-test-results.md` (results), plus automated suite `tests/field/test_docker_v030.py`.

---

## 1. Changes vs v0.2.0 Docker Plan

| # | v0.2.0 stage | v0.3.0 change |
|---|--------------|---------------|
| 1 | Build & Install | **Container hardened**: `.dockerignore` added, non-root `USER`, `git` installed (unblocks `store/git.py` promotion), Dockerfile `HEALTHCHECK`, buildx OCI labels (`org.opencontainers.image.*`) — all from #524/#607 |
| 2 | Compose | **Rewrite per #607**: top-level `name: cauterule`, per-service `profiles:` (`demo` / `test` / `mcp`), dead port `8025` removed from demo, MCP runtime `pip install` moved to build time, 25 hardcoded test dirs replaced with mounted suites |
| 3 | Hermetic unit suite | Same `tests/` dirs plus `tests/integrations/` (OTEL exporter E2E) |
| 4 | Adversarial | Unchanged from v0.2.0 (50 on-disk trajectories) |
| 5 | Corpus & benchmarks | **NEW `cauterule corpus` + `cauterule benchmark` CLIs**; `benchmarks/` pytest-benchmark suite (5 hot paths); `benchmark run --compare` delta path; `corpus export --format csv` |
| 6 | CLI | Adds `corpus add/list/validate/lint/build/export`, `benchmark list/run`, `pack create/install/publish/info/tree/outdated` (full M5 surface), `otel test`, `mcp --transport http` |
| 7 | Packs | **NEW (v0.3.0 major):** `pack install` from GitHub/gist/local, `pack create`, publish with semver + safety scoring — packs must install and persist in the container |
| 8 | Adapters | **NEW (v0.3.0 major):** langgraph / crewai / pydanticai / decorator adapters must import and run inside the container |
| 9 | Lifecycle | **NEW (v0.3.0 major):** observe → specificity score → auto-promotion → retirement → supersession chains work across a container restart |
| 10 | MCP | **NEW (v0.3.0):** stdio still works; **HTTP transport with bearer auth, JSON-schema validation, rate limiting** (R6) — auth 401 / schema 400 / rate-limit 429 paths |
| 11 | Observability | **NEW (v0.3.0):** OTEL exporter emits `rule.match/promote/retire/replay.verdict` spans to a collector (in-container validation) |
| 12 | Preflight | **NEW (v0.3.0):** `cauterule preflight --cost-table` prints $/1k trajectories per model; `--max-cost` cap enforced before a run |
| 13 | Badge + webhook | **NEW (M5):** `cauterule badge` emits 'N rules learned' SVG/shields; promote fires `webhook` notification to a local listener |
| 14 | Demo | Same target <60s, but now through `docker compose --profile demo up` |
| 15 | Multi-env | **#607 scope:** image must build `--platform linux/amd64,linux/arm64`; both architectures smoke-tested |
| 16 | Image size | **NEW (v0.3.0):** measure `docker images` size vs v0.2.0 baseline, document growth (git + .dockerignore effects) |

---

## 2. Test Environment

Builds the hardened image (assumes #524/#607 landed):

```bash
docker build -t cauterule:field-test .
# multi-arch (on capable host / buildx):
docker buildx build --platform linux/amd64,linux/arm64 -t cauterule:field-test .
```

Base image `python:3.12-slim`, wheel install via `python -m build`. v0.3.0 expectations from the image: `git` present, non-root runtime user, `HEALTHCHECK` defined, OCI labels on `docker inspect`, `mcp` dependency baked in (no runtime `pip install`).

---

## 3. Test Matrix

| Test Layer | What It Tests | How Verified | v0.3.0-specific |
|------------|---------------|--------------|-----------------|
| Build & hardening | `.dockerignore` honored, non-root user, git present, healthcheck, OCI labels | `docker build` + `docker inspect` | ✅ NEW (#524/#607) |
| Compose scenarios | `docker compose --profile demo up`, no dead port, MCP service profiles | `docker compose config` + `up` | ✅ NEW (#607) |
| CLI | v0.3.0 command surface renders | subprocess in container | `corpus`, `benchmark`, `pack`, `otel test`, `mcp --transport http` |
| Pipeline | capture → preflight → gate → extract → replay → promote (git commit inside container) → inject | scripted scenario | git promotion now works in-container |
| Packs | `pack create` (scaffold from store), `pack install` (local/gist), `pack list`, pack rules loaded + injected, persists across restart | subprocess | ✅ NEW (M5) |
| Adapters | `import cauterule.adapter.{langgraph,crewai,pydanticai,decorator}` imports cleanly | python -c in container | ✅ NEW (M4) |
| Lifecycle | observe → outcomes tracked → specificity scored → retirement/supersession | subprocess + store inspection | ✅ NEW (M4) |
| MCP stdio | 4 tools respond on stdio transport | mock client | — |
| MCP HTTP + security | HTTP transport: unauth 401, bad payload 400, rate-limit 429, authed happy path | curl / python client | ✅ NEW (M6 #601) |
| Observability / OTEL | `rule.match`/`promote`/`retire`/`replay.verdict` spans hit mock collector | in-container collector + `otel test` | ✅ NEW (M6 #588) |
| Preflight | `preflight --cost-table` + `--max-cost` enforcement | subprocess | ✅ NEW (M6 #486) |
| Badge / Webhook | `badge` SVG + shields URL; promote fires webhook to listener | subprocess + local HTTP listener | ✅ NEW (M5 #581/#585) |
| Corpus & benchmarks | `corpus validate/lint/build/export` + `benchmark list`/`benchmark run` | subprocess + pytest-benchmark | ✅ NEW (M6 #606/#605) |
| Adversarial | 6 corpora produce 0 promoted rules | `pytest tests/adversarial/` | — |
| Scale | latency/memory/indexing targets | `pytest tests/scale/` (slow) | — |
| Demo | full loop <60s via compose profile | `docker compose --profile demo up` | ✅ changed |
| Image size | measure + diff vs baseline | `docker images` | ✅ NEW |
| Multi-arch | amd64 + arm64 both build & smoke | buildx | ✅ NEW (#607) |

---

## 4. Test Stages

### Stage 1 — Build & Hardening (#524, #607)
```bash
docker build -t cauterule:field-test .
docker run --rm cauterule:field-test --version
docker run --rm cauterule:field-test --help
docker inspect cauterule:field-test
```
Pass:
- `--help` lists `extract`, `promote`, `review`, `preflight`, `corpus`, `benchmark`, `pack`, `otel`, `mcp`, `demo`, `health`.
- Runtime user is **non-root** (`docker run --rm cauterule:field-test id`).
- `git` present: `docker run --rm cauterule:field-test git --version`.
- `HEALTHCHECK` present: `docker inspect` shows `"Healthcheck"` config.
- OCI labels present: `org.opencontainers.image.version/description/source`.
- Build context excludes `.venv/`, `.git/`, caches (verify via `docker build --no-cache` log or image size).
- `mcp` dependency baked in: `docker run --rm cauterule:field-test sh -c "python -c 'import mcp' && echo ok"` — **no runtime pip install** (#607).

### Stage 2 — Compose Scenarios (#607)
```bash
docker compose config                # name: cauterule, profiles present
docker compose --profile demo up -d --build
docker compose --profile demo ps     # healthcheck green
docker compose --profile demo run --rm cauterule-demo cauterule --help
```
Pass:
- `name: cauterule` at top level; `profiles:` on every service; demo has **no** `ports:` (stdio MCP, no dead `8025` mapping).
- `cauterule-mcp` service uses `profiles: [mcp]` — a bare `docker compose up` starts **zero** services.
- MCP service healthcheck no longer depends on `pgrep` (procps); uses a portable `python`/`cauterule --help` style check.
- Test service mounts a globbed suite set (no 25 hardcoded dirs).

### Stage 3 — CLI Surface (v0.3.0 commands)
```bash
docker run --rm cauterule:field-test sh -c "
  cauterule corpus --help
  cauterule benchmark --help && cauterule benchmark list
  cauterule pack --help
  cauterule otel --help
  cauterule mcp --help | grep -i transport
  cauterule preflight --cost-table
"
```
Pass: each group renders its subcommands; `benchmark list` prints the 5 benchmark names; `preflight --cost-table` prints the $/1k per-model table.

### Stage 4 — Corpus & Benchmark CLIs (M6 #606/#605)
```bash
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  cauterule init --dir /data/p
  cauterule corpus add /data/p/trajectories/failure.jsonl --domain raw --tags 'ft,docker'
  cauterule corpus list --format json
  cauterule corpus validate
  cauterule corpus lint
  cauterule corpus build --output /data/p/corpus-store.jsonl
  cauterule corpus export --format jsonl
"
```
Plus benchmark job (CLI surface, not raw pytest):
```bash
docker run --rm cauterule:field-test sh -c "pip install -q pytest-benchmark && \
  cauterule benchmark list && \
  cauterule benchmark run conflict_consolidation && \
  cauterule benchmark run --all --compare /app/benchmarks/baseline.json"
```
Pass: corpus round-trips add→list→validate→lint→build→export (`--format jsonl` **and** `--format csv`); `benchmark list` prints the 5 names; `run <name>` runs exactly one; `run --all --compare baseline.json` prints per-benchmark deltas against the checked-in baseline (15 hot paths: extraction, replay_matcher, injection_budget, conflict_consolidation, observe_coverage).

### Stage 5 — Packs (M5 — v0.3.0 major)
```bash
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  cauterule init --dir /data/p
  cauterule pack create ft-pack --store /data/p/rules --from-tag ft-docker
  cauterule pack install pack-git --store /data/p/rules       # or a gist URL
  cauterule pack list --store /data/p/rules
  cauterule pack info pack-git --store /data/p/rules
  cauterule pack tree pack-git --store /data/p/rules
"
```
Pass: `pack create` scaffolds a shippable pack (pack.yaml + rules) from the store; installed pack appears in `pack list`, dependencies resolve (`tree`), rules load into the store.

### Stage 6 — Pack Persistence (M5)
```bash
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  cauterule pack install pack-git --store /data/rules
"
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  cauterule pack list --store /data/rules | grep pack-git
  cauterule rules --store /data/rules | wc -l   # >= expected
"
```
Pass: pack and its rules survive container restart via persisted `rules/` volume (#641 volume scenario).

### Stage 7 — Adapters (M4 — v0.3.0 major)
```bash
docker run --rm cauterule:field-test sh -c "
  python -c 'import cauterule.adapter.langgraph, cauterule.adapter.crewai, cauterule.adapter.pydanticai, cauterule.adapter.decorator; print(\"adapters-ok\")'
  python -c 'from cauterule.adapter.inject import inject; print(\"inject-ok\")'
"
```
Pass: all four adapter modules + `inject` import cleanly; a decorator round-trip capture works hermetic (no LLM):
```bash
docker run --rm cauterule:field-test sh -c "
  cd /tmp && cauterule init --dir /tmp/p
  python - <<'PY'
from cauterule.adapter.decorator import watch
import cauterule
@watch(project_dir='/tmp/p')
def fail_fn():
    raise RuntimeError('boom')
try: fail_fn()
except Exception: pass
print('captured' if len(list(cauterule.store.list_rules('/tmp/p/rules'))) >= 0 else 'err')
PY
"
```

### Stage 8 — Lifecycle (M4 — v0.3.0 major)
```bash
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  cauterule observe --trajectory /data/p/trajectories/failure.jsonl --store /data/rules
  cauterule show --hits --store /data/rules
  cauterule specificity --store /data/rules
"
```
Pass: observe records outcomes; per-rule hits/outcomes visible; specificity scoring present. Retirement/supersession verified by inspecting store state after engineered staleness inputs (functionality covered by hermetic `tests/lifecycle/`; container stage only asserts commands run and store mutates across restart).

### Stage 9 — MCP stdio + HTTP + Security (M6 #601)
```bash
# stdio (unchanged baseline — #527 parity)
docker run --rm -d --name mcp-stdio cauterule:field-test mcp --transport stdio
docker exec mcp-stdio sh -c "ls /app/rules"

# HTTP with auth + schema validation + rate limit
docker run --rm -d -p 9025:9025 --name mcp-http \
  -e CAUTERULE_MCP_TOKEN=test-token \
  cauterule:field-test mcp --transport http --host 0.0.0.0 --port 9025 --auth-mode bearer

# 1. unauthenticated -> 401
curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:9025/report_failure -H 'Content-Type: application/json' -d '{"trajectory":[],"error":"e"}'
# 2. authenticated but malformed payload -> 400
curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:9025/report_failure -H 'Authorization: Bearer test-token' -H 'Content-Type: application/json' -d '{"error":"missing trajectory"}'
# 3. burst over limit -> 429 + Retry-After
for i in $(seq 1 20); do curl -s -o /dev/null -X POST http://localhost:9025/report_failure -H 'Authorization: Bearer test-token' -H 'Content-Type: application/json' -d '{"trajectory":[{"s":1}],"error":"e"}'; done | head -1
# 4. valid authed in-budget -> 2xx, flows through
curl -s -X POST http://localhost:9025/report_failure -H 'Authorization: Bearer test-token' -H 'Content-Type: application/json' -d '{"trajectory":[{"s":1}],"error":"e"}'
```
Pass: 401 → 400 → 429 (with `Retry-After`) → happy path; `mode=none` with a non-loopback host logs a warning and is rejected (or explicitly dev-only).

### Stage 10 — OTEL Exporter (M6 #588)
```bash
# in-container mock collector + exporter round-trip
docker run --rm -d --name otel-collector -p 4317:4317 your-collector-image  # or in-process mock
docker run --rm \
  -e CAUTERULE_OTEL_ENABLED=true -e CAUTERULE_OTEL_ENDPOINT=http://host.docker.internal:4317 \
  cauterule:field-test otel test
```
Pass: `otel test` round-trips a synthetic span, reports success; engine events (`rule.match`, `rule.promote`, `rule.retire`, `replay.verdict`) are emitted when the corresponding commands run. Failure path: bad endpoint logs + does **not** raise into the pipeline.

### Stage 11 — Preflight + Cost (M6 #486)
```bash
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  cauterule preflight --corpus /data/p/trajectories/failure.jsonl --max-cost 0.50
"
```
Pass: preflight prints estimated cost + time and proceeds under cap; exits FAIL with clear message when estimate > `--max-cost`.

### Stage 12 — Pipeline E2E (with git promotion — unblocked in-container)
```bash
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  cauterule init --dir /data/p
  cauterule preflight --corpus /data/p/trajectories/failure.jsonl
  cauterule extract --trajectory /data/p/trajectories/failure.jsonl --dry-run
  cauterule test --candidate /data/p/candidates/candidate-1.yaml
  cauterule promote --candidate /data/p/candidates/candidate-1.yaml   # git commit inside container
  cd /data/p && git log --oneline | head -1
  cauterule list && cauterule inject 'git push origin main'
  cauterule observe --trajectory /data/p/trajectories/failure.jsonl
"
```
Pass: full loop; `git log` shows the promotion commit (**regression from v0.2.0** — git now installed per #524).

### Stage 13 — Badge + Webhook (M5 #581/#585)
```bash
# Badge: emit the 'N rules learned' badge (SVG + shields URL)
docker run --rm -v $(pwd)/field-test-data:/data cauterule:field-test sh -c "
  cauterule badge --store /data/rules --format svg > /tmp/badge.svg
  grep -qi '<svg' /tmp/badge.svg && echo 'svg-ok'
  cauterule badge --store /data/rules --format url
"
# Webhook: start a local listener on the host, promote, verify delivery
docker run --rm -d -p 9027:9027 --name wl python:3.12-slim sh -c "pip -q install http.server; python -c \"from http.server import HTTPServer,BaseHTTPRequestHandler; import sys; sys.path.insert(0,'/'); \
  class H(BaseHTTPRequestHandler):
    def do_POST(self): self.send_response(200); self.end_headers(); open('/tmp/events.log','a').write(self.rfile.read(int(self.headers['Content-Length'])).decode()); 
    def log_message(self,*a): pass
  HTTPServer(('0.0.0.0',9027),H).serve_forever()\""
docker run --rm -v $(pwd)/field-test-data:/data \
  -e CAUTERULE_WEBHOOK_URL=http://host.docker.internal:9027 cauterule:field-test sh -c "
  cauterule promote --candidate /data/p/candidates/candidate-1.yaml --store /data/rules"
docker logs wl
```
Pass: `badge` emits a valid SVG and a shields URL; after promote, the webhook listener receives a JSON delivery with `rule_id`/`event=promotion` payload (M5 #585).

### Stage 14 — Demo via Compose
```bash
docker compose --profile demo run --rm cauterule-demo
```
Pass: <60s, ≥1 rule promoted (or documented mock/skip on non-LLM environments), healthcheck green after `up`.

### Stage 15 — Rule Store Persistence (#641 volume scenarios)
```bash
docker run --rm -d --name a -v $(pwd)/field-test-data/rules:/app/rules cauterule:field-test extract --trajectory /data/failure.jsonl
docker stop a && docker rm a
docker run --rm -v $(pwd)/field-test-data/rules:/app/rules cauterule:field-test list   # container B sees rules from A
```
Pass: rules extracted in container A are visible in container B; config overrides via mounted volume (`cauterule.toml`) take effect.

### Stage 16 — Image Size (#641)
```bash
docker images cauterule:field-test --format "{{.Size}}"
```
Pass: size recorded and diffed against the v0.2.0 image tag; growth attributable to `git` + new deps (packaging/etc.) documented; `.dockerignore` prevents `.venv`/cache bloat.

### Stage 17 — Multi-Arch (#607)
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t cauterule:field-test .
```
Pass: both architectures build; on an Apple Silicon host, verify the arm64 image runs `--version` and demo; on CI, verify amd64.

### Stage 18 — Resource Limits + Network (#641)
```bash
docker run --rm --memory=1g --cpus=2 cauterule:field-test demo      # resource-constrained demo
docker run --rm --network none cauterule:field-test --help          # air-gapped: core CLI works offline
```
Pass: demo completes under 1GB/2 CPU or fails gracefully with a clear error; `--help`/`--version` work offline (LLM calls fail with actionable message).

---

## 5. Automated Suite (#642 — `tests/field/test_docker_v030.py`)

Mirrors the plan as pytest methods, following `tests/field/test_docker_*.py` patterns:

| Test | Scenarios covered | Stage |
|------|-------------------|-------|
| `test_docker_build_hardening` | non-root user, git, healthcheck, OCI labels, mcp baked in | 1 |
| `test_docker_compose_config` | `name:`, `profiles:`, no dead port, globbed test mounts | 2 |
| `test_docker_cli_smoke` | `--help`/`--version` list v0.3.0 commands | 1 |
| `test_docker_preflight` | preflight + `--cost-table` + `--max-cost` | 11 |
| `test_docker_corpus_cli` | add/list/validate/lint/build/export round-trip (jsonl + csv) | 4 |
| `test_docker_benchmark_cli` | `benchmark list`; `run <name>`; `run --all --compare` deltas | 4 |
| `test_docker_extract_test_promote` | full pipeline incl. git commit | 12 |
| `test_docker_pack_create` | `pack create` scaffolds pack from store | 5 |
| `test_docker_pack_install` | pack install/list/info/tree | 5 |
| `test_docker_pack_persistence` | packs survive restart | 6 |
| `test_docker_adapter_import` | 4 adapter modules + inject import | 7 |
| `test_docker_lifecycle` | observe/specificity/hits mutate store | 8 |
| `test_docker_mcp_stdio` | stdio transport parity | 9 |
| `test_docker_mcp_http_auth` | 401/400/429/happy path | 9 |
| `test_docker_otel_emit` | `otel test` + span emission (mock collector) | 10 |
| `test_docker_badge` | `badge` SVG + shields URL | 13 |
| `test_docker_webhook` | promote fires webhook to local listener | 13 |
| `test_docker_rules_persistence` | rules survive restart, container B sees them | 15 |
| `test_docker_image_size` | measure + record vs baseline | 16 |
| `test_docker_multi_arch` | buildx both platforms (skippable on non-capable host) | 17 |
| `test_docker_resource_limits` | memory/cpu constrained run | 18 |
| `test_docker_network_isolated` | air-gapped `--help`/`--version` | 18 |

Runner integration: add a `--docker` flag to `scripts/run-field-test.py` (gap in current runner) that invokes only `tests/field/test_docker_v030.py` and emits `field-test/v0.3.0/docker-test-report.md` with PASS/FAIL per test, test counts, and timings.

---

## 6. docker-compose.yaml Post-#607 Shape (target)

```yaml
name: cauterule

services:
  cauterule-demo:
    profiles: [demo]
    build: { context: ., dockerfile: Dockerfile }
    command: demo
    volumes:
      - ./rules:/app/rules
      - ./corpus:/app/corpus
    environment: [CAUTERULE_LLM_PROVIDER, CAUTERULE_MODEL, OPENAI_API_KEY]
    healthcheck:
      test: ["CMD-SHELL", "cauterule --help > /dev/null 2>&1"]
      interval: 30s
      retries: 3
    # NO ports: — MCP is stdio here; HTTP is a profiled, gated service

  cauterule-mcp:
    profiles: [mcp]
    build: { context: ., dockerfile: Dockerfile }
    entrypoint: ["cauterule", "mcp", "--transport", "stdio"]   # mcp baked in, no pip
    volumes: ["./rules:/app/rules"]
    environment: [CAUTERULE_LLM_PROVIDER, CAUTERULE_MODEL, OPENAI_API_KEY, CAUTERULE_MCP_TOKEN]
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import socket; socket.create_connection(('localhost',9000))\" || exit 1"]
      interval: 30s
      retries: 3

  cauterule-test:
    profiles: [test]
    build: { context: ., dockerfile: Dockerfile }
    entrypoint: ["sh", "-c"]
    command: ["pip install -q pytest pytest-benchmark && python -m pytest tests/ -m 'not slow and not docker' --tb=short -q -p no:cacheprovider"]
    volumes: ["./tests:/app/tests:ro"]
    environment: [CAUTERULE_LLM_PROVIDER, CAUTERULE_MODEL, OPENAI_API_KEY]
    healthcheck:
      test: ["CMD-SHELL", "cauterule --help > /dev/null 2>&1"]
      interval: 30s
      retries: 3
```

---

## 7. Pass/Fail Summary

| Stage | Tests | Pass Criteria |
|-------|-------|---------------|
| 1. Build & Hardening | 8 | Non-root, git, healthcheck, OCI labels, no runtime pip |
| 2. Compose | 6 | Profiles, name, no dead port, healthcheck green |
| 3. CLI Surface | 7 | All v0.3.0 groups render |
| 4. Corpus & Benchmark | 12 | Round-trip (jsonl+csv) + `--compare` deltas + 15 benchmarks green |
| 5. Packs | 7 | Create/install/list/info/tree |
| 6. Pack Persistence | 2 | Survive restart |
| 7. Adapters | 4 | Import + hermetic capture |
| 8. Lifecycle | 3 | observe/specificity/hits mutate store |
| 9. MCP + Security | 6 | stdio parity + 401/400/429/happy |
| 10. OTEL | 3 | Span round-trip + non-fatal on failure |
| 11. Preflight/Cost | 3 | Cost table + cap enforcement |
| 12. Pipeline E2E | 8 | Full loop incl. git commit |
| 13. Badge/Webhook | 4 | SVG + shields URL; webhook delivery | 
| 14. Demo | 3 | <60s, healthcheck green |
| 15. Persistence | 3 | Cross-container rule survival |
| 16. Image Size | 1 | Baseline diff documented |
| 17. Multi-Arch | 2 | amd64 + arm64 build/smoke |
| 18. Resource/Network | 2 | Graceful under limits, offline CLI |
| **Total** | **~70 new tests** (excludes 127 inherited v0.2.0 tests; see `docker-test-results.md`) | **All stages pass** |

---

## 8. Deferred / Out of Scope

- Real LLM sweeps (M7 #648/#650 measure separately), real OTEL collector backend (Jaeger/Tempo quickstart is docs-only here; container uses a mock/in-process collector), Homebrew/binary tests (M8 #657), PyPI publish (M8 #649), GitHub Action (M8 #614), external SaaS webhook delivery (Stage 13 uses an in-container/local listener only), gist tab publish (`pack publish`/`share` need network credentials — verified out of band).

---

## 9. Results Artifact

The #641/#642 run writes `docs/field-test/v0.3.0/docker-test-results.md` (PASS/FAIL per stage, test counts, timings, image size deltas, multi-arch matrix) — parallel to `docs/field-test/v0.2.0/docker-test-results.md`, with a regression table comparing v0.3.0 vs v0.2.0 Docker behavior.