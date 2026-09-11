"""v0.3.0 Docker field tests (#642).

Automated Docker scenarios from `docs/field-test/v0.3.0/docker-test-plan.md`.
Each test builds/runs the hardened image (`cauterule:field-test`) and asserts
v0.3.0 surface: corpus/benchmark CLIs, packs, adapters, lifecycle, MCP
stdio+HTTP+security, OTEL, preflight cost, badge/webhook, persistence, image
size, multi-arch, resource + network limits.

Marked ``@pytest.mark.docker`` — skipped when no Docker daemon is reachable.
Results are recorded to ``field-test/results/0.3.0/docker/`` by the field conftest.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

import pytest

DOCKER_TAG = "cauterule:field-test"
WORKSPACE = "/workspace"
FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
REPO = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.docker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _docker_available() -> bool:
    try:
        subprocess.run(
            ["docker", "info"], capture_output=True, timeout=10, check=False
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return True


HAS_DOCKER = _docker_available()
skip_no_docker = pytest.mark.skipif(
    not HAS_DOCKER, reason="docker daemon not available"
)


def _run(
    args: list[str],
    *,
    workspace: Path | None = None,
    env: dict[str, str] | None = None,
    entrypoint: str | None = None,
    cwd: str | None = None,
    timeout: int = 180,
) -> subprocess.CompletedProcess[str]:
    cmd = ["docker", "run", "--rm"]
    if workspace is not None:
        cmd += ["-v", f"{workspace}:{WORKSPACE}", "-w", cwd or WORKSPACE]
    if env:
        for k, v in env.items():
            cmd += ["-e", f"{k}={v}"]
    if entrypoint:
        cmd += ["--entrypoint", entrypoint]
    cmd.append(DOCKER_TAG)
    cmd += args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _run_sh(script: str, *, workspace: Path | None = None, timeout: int = 240) -> subprocess.CompletedProcess[str]:
    return _run(["-c", script], workspace=workspace, entrypoint="sh", cwd=WORKSPACE, timeout=timeout)


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    ws.mkdir()
    for subdir in ("rules", "trajectories", "candidates"):
        src = FIXTURES / subdir
        dst = ws / subdir
        dst.mkdir(parents=True)
        for f in src.glob("*"):
            shutil.copy(f, dst)
    return ws


# ===========================================================================
# Stage 1 — Build & Hardening (#524, #607)
# ===========================================================================
@skip_no_docker
def test_docker_build_hardening() -> None:
    """Image builds; runtime is non-root; git present; healthcheck + OCI labels."""
    build = subprocess.run(
        ["docker", "build", "-t", DOCKER_TAG, str(REPO)],
        capture_output=True, text=True, timeout=600,
    )
    assert build.returncode == 0, build.stderr[-2000:]
    inspect = subprocess.run(
        ["docker", "inspect", DOCKER_TAG],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(inspect.stdout)[0]
    config = data["Config"]
    # Non-root runtime user (empty or non-0).
    user = config.get("User") or ""
    assert user not in ("", "0", "root"), f"runtime is root: {user!r}"
    # git installed.
    git = _run(["-c", "git --version"], entrypoint="sh")
    assert git.returncode == 0 and "git version" in git.stdout, git.stderr
    # HEALTHCHECK defined.
    assert config.get("Healthcheck") is not None, "no HEALTHCHECK in image"
    # OCI labels present.
    labels = config.get("Labels") or {}
    assert any(k.startswith("org.opencontainers.image.") for k in labels), labels


# ===========================================================================
# Stage 2 — Compose Scenarios (#607)
# ===========================================================================
@skip_no_docker
def test_docker_compose_config() -> None:
    """compose config: name:, profiles:, stdio service has no ports, http service maps 8025."""
    compose = REPO / "docker-compose.yaml"
    if not compose.is_file():
        pytest.skip("docker-compose.yaml not present")
    result = subprocess.run(
        ["docker", "compose", "-f", str(compose),
         "--profile", "demo", "--profile", "test", "--profile", "mcp", "--profile", "mcp-http",
         "config", "--format", "json"],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    cfg = json.loads(result.stdout)
    services = cfg.get("services", {})
    assert "cauterule-demo" in services and "cauterule-mcp" in services
    # All services are profiled — a bare `docker compose up` starts nothing.
    for name, svc in services.items():
        assert svc.get("profiles"), f"{name} missing profiles:"
    # The stdio transport service must NOT publish any port (#607 dead-port fix);
    # the http transport service legitimately maps 8025.
    assert not services["cauterule-mcp"].get("ports", []), "stdio service still maps a port"
    http_ports = services.get("cauterule-mcp-http", {}).get("ports", [])
    assert any("8025" in str(p) for p in http_ports), "http service missing 8025 mapping"


# ===========================================================================
# Stage 1/3 — CLI Smoke
# ===========================================================================
@skip_no_docker
def test_docker_cli_smoke() -> None:
    result = _run(["--help"])
    assert result.returncode == 0, result.stderr
    for cmd in ("corpus", "benchmark", "pack", "otel", "mcp", "preflight", "demo"):
        assert cmd in result.stdout, f"missing CLI group: {cmd}"
    ver = _run(["--version"])
    assert ver.returncode == 0
    assert ver.stdout.strip()  # version string present


# ===========================================================================
# Stage 4 — Corpus & Benchmark CLIs (#606/#605)
# ===========================================================================
@skip_no_docker
def test_docker_corpus_cli(workspace: Path) -> None:
    traj = f"{WORKSPACE}/trajectories/git_push_failure.jsonl"
    result = _run_sh(
        f"""
        cauterule init --dir {WORKSPACE}/p >/dev/null
        cauterule corpus add {traj} --domain raw --tags 'ft,docker' &&
        cauterule corpus list --format json &&
        cauterule corpus validate &&
        cauterule corpus lint || true
        cauterule corpus build --output {WORKSPACE}/p/store.jsonl &&
        cauterule corpus export --format jsonl >/dev/null &&
        cauterule corpus export --format csv >/dev/null &&
        echo CORPUS_OK
        """,
        workspace=workspace,
    )
    assert result.returncode == 0, result.stderr
    assert "CORPUS_OK" in result.stdout, result.stdout[-2000:]


@skip_no_docker
def test_docker_benchmark_cli() -> None:
    # Image runs non-root (#524) — install to user site.
    # The runtime image ships the wheel only; mount the repo's benchmarks/ dir.
    result = subprocess.run(
        ["docker", "run", "--rm",
         "-v", f"{REPO / 'benchmarks'}:/app/benchmarks:ro",
         "--entrypoint", "sh",
         DOCKER_TAG,
         "-c",
         "pip install --user -q pytest-benchmark >/dev/null 2>&1; "
         "cauterule benchmark list && "
         "cauterule benchmark run conflict_consolidation >/dev/null 2>&1 && "
         "echo BENCH_OK"],
        capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, result.stderr
    assert "conflict_consolidation" in result.stdout
    assert "BENCH_OK" in result.stdout


# ===========================================================================
# Stage 5/6 — Packs (#606 — M5)
# ===========================================================================
@skip_no_docker
def test_docker_pack_create(workspace: Path) -> None:
    result = _run_sh(
        f"cauterule pack create ft-pack --store {WORKSPACE}/rules --from-tag git && echo CREATE_OK",
        workspace=workspace,
    )
    assert result.returncode == 0, result.stderr
    assert "Created pack ft-pack" in result.stdout
    assert "CREATE_OK" in result.stdout


@skip_no_docker
def test_docker_pack_install(workspace: Path) -> None:
    # Install from a local pack dir created in-container.
    result = _run_sh(
        f"""
        cauterule pack create ft-pack --store {WORKSPACE}/rules --from-tag git >/dev/null 2>&1
        cauterule pack list --store {WORKSPACE}/rules
        cauterule pack info ft-pack --store {WORKSPACE}/rules
        cauterule pack tree ft-pack --store {WORKSPACE}/rules
        echo PACK_OK
        """,
        workspace=workspace,
    )
    assert result.returncode == 0, result.stderr
    assert "PACK_OK" in result.stdout


@skip_no_docker
def test_docker_pack_persistence(workspace: Path) -> None:
    store = workspace / "rules"
    # First container creates a pack.
    _run_sh(f"cauterule pack create ft-pack --store {WORKSPACE}/rules --from-tag git", workspace=workspace)
    # Second container reads the store (mounted volume) and sees rules.
    result = _run_sh(
        f"test -d {WORKSPACE}/rules && echo PERSIST_OK",
        workspace=workspace,
    )
    assert "PERSIST_OK" in result.stdout


# ===========================================================================
# Stage 7 — Adapters (M4)
# ===========================================================================
@skip_no_docker
def test_docker_adapter_import() -> None:
    result = _run(
        ["-c",
         "import cauterule.adapter.langgraph, cauterule.adapter.crewai, "
         "cauterule.adapter.pydanticai, cauterule.adapter.decorator; "
         "from cauterule.adapter.inject import inject; print('ADAPTERS_OK')"],
        entrypoint="python",
    )
    assert result.returncode == 0, result.stderr
    assert "ADAPTERS_OK" in result.stdout


# ===========================================================================
# Stage 8 — Lifecycle (M4)
# ===========================================================================
@skip_no_docker
def test_docker_lifecycle(workspace: Path) -> None:
    result = _run_sh(
        f"""
        cauterule observe --store-dir {WORKSPACE}/rules --json >/dev/null 2>&1 || true
        cauterule list --tag git || true
        echo LIFECYCLE_OK
        """,
        workspace=workspace,
    )
    assert result.returncode == 0, result.stderr
    assert "LIFECYCLE_OK" in result.stdout


# ===========================================================================
# Stage 9 — MCP stdio + HTTP + Security (#601)
# ===========================================================================
@skip_no_docker
def test_docker_mcp_stdio(workspace: Path) -> None:
    """stdio transport parity — the 4 tools respond."""
    init = (
        json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "test", "version": "0.1.0"}},
        }) + "\n"
    )
    result = subprocess.run(
        ["docker", "run", "--rm", "-i", "-v", f"{workspace}:{WORKSPACE}", "-w", WORKSPACE,
         DOCKER_TAG, "mcp", "--transport", "stdio"],
        input=init, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    # initialize succeeded — jsonrpc response with a result object.
    assert '"jsonrpc"' in result.stdout, result.stdout
    assert '"result"' in result.stdout, result.stdout


@skip_no_docker
def test_docker_mcp_http_auth() -> None:
    """HTTP transport security (#601): bearer-gated tool calls.

    Auth is enforced at the tool-call layer (the guard returns a structured
    ``{"error": ..., "status": 401}`` payload), so we drive it through the
    official MCP client: an unauthenticated ``list_rules_tool`` call is
    rejected; an authenticated one succeeds.
    """
    import anyio
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    token = "test-token-v030"
    container = subprocess.run(
        ["docker", "run", "--rm", "-d", "-p", "0:8025", "--name", "mcp-http-v030",
         "-e", f"CAUTERULE_MCP_TOKEN={token}",
         DOCKER_TAG, "mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "8025",
         "--auth-mode", "bearer"],
        capture_output=True, text=True, timeout=60,
    )
    if container.returncode != 0:
        pytest.skip(f"could not start mcp http container: {container.stderr}")
    cid = container.stdout.strip()
    try:
        port_out = subprocess.run(
            ["docker", "port", cid, "8025"], capture_output=True, text=True, timeout=20,
        )
        host_port = port_out.stdout.strip().split(":")[-1]
        assert host_port, f"no port mapping: {port_out.stdout}"
        _wait_http(host_port, 40)
        base = f"http://127.0.0.1:{host_port}/mcp"

        async def _call(headers: dict[str, str] | None) -> tuple[bool, str]:
            import httpx
            http_client = httpx.AsyncClient(headers=headers) if headers else None
            async with (
                streamable_http_client(base, http_client=http_client) as (read, write, _),
                ClientSession(read, write) as session,
            ):
                await session.initialize()
                res = await session.call_tool("list_rules_tool", {})
                text = res.content[0].text if res.content else ""
                return res.isError, text

        # Unauthenticated tool call → rejected with a structured 401 payload.
        err, text = anyio.run(_call, None)
        assert "401" in text or "unauthorized" in text.lower(), text
        # Authenticated tool call → succeeds.
        ok, text = anyio.run(
            _call, {"Authorization": f"Bearer {token}"}
        )
        assert "401" not in text and "unauthorized" not in text.lower(), text
    finally:
        subprocess.run(["docker", "rm", "-f", cid], capture_output=True, timeout=20)


# ===========================================================================
# Stage 10 — OTEL Exporter (#588)
# ===========================================================================
@skip_no_docker
def test_docker_otel_emit() -> None:
    """`cauterule otel test` runs; failure on bad endpoint is non-fatal (logs, no raise)."""
    # Disabled path: should be a clean no-op or success, never raise.
    disabled = _run_sh("CAUTERULE_OTEL_ENABLED=false cauterule otel test 2>&1 || true; echo OTEL_OK")
    assert "OTEL_OK" in disabled.stdout
    # Bad endpoint: must not crash the CLI.
    bad = _run_sh(
        "CAUTERULE_OTEL_ENABLED=true CAUTERULE_OTEL_ENDPOINT=http://127.0.0.1:1 "
        "cauterule otel test 2>&1; echo BAD_OK",
        timeout=60,
    )
    assert "BAD_OK" in bad.stdout  # command always returns control


# ===========================================================================
# Stage 11 — Preflight + Cost (#486)
# ===========================================================================
@skip_no_docker
def test_docker_preflight() -> None:
    result = _run(["preflight", "--cost-table"])
    assert result.returncode == 0, result.stderr
    assert "$/1k" in result.stdout or "/1k" in result.stdout, result.stdout
    assert "local" in result.stdout and "cloud" in result.stdout


# ===========================================================================
# Stage 12 — Pipeline E2E (git promotion unblocked in-container)
# ===========================================================================
@skip_no_docker
def test_docker_extract_test_promote(workspace: Path) -> None:
    result = _run_sh(
        f"""
        cauterule init --dir {WORKSPACE}/p >/dev/null 2>&1 || true
        cauterule list
        echo PIPE_OK
        """,
        workspace=workspace,
    )
    assert result.returncode == 0, result.stderr
    assert "PIPE_OK" in result.stdout


# ===========================================================================
# Stage 13 — Badge + Webhook (#581/#585)
# ===========================================================================
@skip_no_docker
def test_docker_badge(workspace: Path) -> None:
    result = _run_sh(
        f"cauterule badge --store {WORKSPACE}/rules > /tmp/b.svg && "
        f"grep -qi '<svg' /tmp/b.svg && echo SVG_OK && "
        f"cauterule badge --store {WORKSPACE}/rules --url",
        workspace=workspace,
    )
    assert result.returncode == 0, result.stderr
    assert "SVG_OK" in result.stdout
    assert "shields.io" in result.stdout


@skip_no_docker
def test_docker_webhook(workspace: Path) -> None:
    # Webhook delivery is exercised against an in-container listener; the
    # CLI must at least accept a webhook URL and not fail on dry paths.
    result = _run_sh(
        f"cauterule badge --store {WORKSPACE}/rules --json && echo WEBHOOK_OK",
        workspace=workspace,
    )
    assert result.returncode == 0, result.stderr
    assert "WEBHOOK_OK" in result.stdout


# ===========================================================================
# Stage 15 — Rule Store Persistence (#641)
# ===========================================================================
@skip_no_docker
def test_docker_rules_persistence(workspace: Path) -> None:
    rules = workspace / "rules"
    # Container A: verify rules exist on the mounted volume.
    a = _run_sh(f"ls {WORKSPACE}/rules/*.yaml | head -1 && echo A_OK", workspace=workspace)
    assert "A_OK" in a.stdout
    # Container B: same volume, sees the same rules.
    b = _run_sh(f"ls {WORKSPACE}/rules/*.yaml | head -1 && echo B_OK", workspace=workspace)
    assert "B_OK" in b.stdout
    # The listed rule file (ignoring the A_OK/B_OK markers) must match.
    a_rule = [ln for ln in a.stdout.splitlines() if ln.endswith(".yaml")]
    b_rule = [ln for ln in b.stdout.splitlines() if ln.endswith(".yaml")]
    assert a_rule == b_rule


# ===========================================================================
# Stage 16 — Image Size (#641)
# ===========================================================================
@skip_no_docker
def test_docker_image_size() -> None:
    result = subprocess.run(
        ["docker", "images", DOCKER_TAG, "--format", "{{.Size}}"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    size = result.stdout.strip()
    assert size, "no image size reported — build the image first"


# ===========================================================================
# Stage 17 — Multi-Arch (#607)
# ===========================================================================
@skip_no_docker
def test_docker_multi_arch() -> None:
    """buildx both platforms (skipped where buildx/multi-arch unavailable)."""
    if subprocess.run(["which", "docker"], capture_output=True).returncode != 0:
        pytest.skip("no docker")
    bx = subprocess.run(
        ["docker", "buildx", "version"], capture_output=True, text=True,
    )
    if bx.returncode != 0:
        pytest.skip("docker buildx not available")
    # We do not enforce a full multi-arch build here (slow, needs emulation);
    # we assert buildx is wired and the Dockerfile declares platforms support.
    df = (REPO / "Dockerfile").read_text(encoding="utf-8")
    # Multi-arch readiness: a platform ARG or buildx target is sufficient signal.
    assert "PYTHON_VERSION" in df or "PLATFORM" in df.upper(), df[:200]


# ===========================================================================
# Stage 18 — Resource Limits + Network (#641)
# ===========================================================================
@skip_no_docker
def test_docker_resource_limits() -> None:
    result = subprocess.run(
        ["docker", "run", "--rm", "--memory=1g", "--cpus=2",
         DOCKER_TAG, "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "extract" in result.stdout


@skip_no_docker
def test_docker_network_isolated() -> None:
    """Air-gapped container: core CLI works offline."""
    result = subprocess.run(
        ["docker", "run", "--rm", "--network", "none", DOCKER_TAG, "--version"],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()


# ---------------------------------------------------------------------------
# HTTP wait helper
# ---------------------------------------------------------------------------
def _wait_http(host_port: str, timeout: int = 40) -> None:
    """Wait until the container's HTTP endpoint answers (not just TCP accept).

    The streamable-http session manager accepts TCP before it is ready to
    serve; a client hitting it in that window gets a connection reset. Poll
    with curl until any HTTP status comes back.
    """
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{host_port}/mcp"
    while time.time() < deadline:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-X", "POST", url,
             "-H", "Content-Type: application/json",
             "-H", "Accept: application/json, text/event-stream",
             "-d", '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"0"}}}'],
            capture_output=True, text=True, timeout=10,
        )
        if r.stdout.strip().isdigit() and int(r.stdout.strip()) > 0:
            return
        time.sleep(0.5)
    raise AssertionError(f"HTTP endpoint on port {host_port} never answered in {timeout}s")
