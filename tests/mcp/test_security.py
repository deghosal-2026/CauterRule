"""Tests for MCP remote-mode security: auth + rate-limit + schema (#601)."""

from __future__ import annotations

import json

import pytest

from cauterule.mcp.auth import McpAuthError, bearer_from_headers, check_bearer, resolve_tokens
from cauterule.mcp.ratelimit import RateLimiter, TokenBucket
from cauterule.mcp.validation import McpValidationError, validate_payload, validate_report_failure


def _headers(token: str | None = None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


class TestAuth:
    def test_valid_bearer(self) -> None:
        client = check_bearer(_headers("secret"), ["secret"])
        assert client.startswith("token:")

    def test_missing_header(self) -> None:
        with pytest.raises(McpAuthError):
            check_bearer({}, ["secret"])

    def test_wrong_token(self) -> None:
        with pytest.raises(McpAuthError):
            check_bearer(_headers("wrong"), ["secret"])

    def test_no_tokens_configured(self) -> None:
        with pytest.raises(McpAuthError):
            check_bearer(_headers("x"), [])

    def test_none_mode_skips(self) -> None:
        assert check_bearer({}, [], mode="none") == "anonymous-local"

    def test_env_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CAUTERULE_MCP_TOKEN", "env-secret")
        assert "env-secret" in resolve_tokens()
        assert bearer_from_headers({"authorization": "Bearer env-secret"}) == "env-secret"


class TestRateLimit:
    def test_allows_within_capacity(self) -> None:
        limiter = TokenBucket(capacity=3, refill_per_min=60.0)
        assert [limiter.allow("c") for _ in range(3)] == [0.0, 0.0, 0.0]

    def test_rejects_over_capacity_with_retry_after(self) -> None:
        limiter = TokenBucket(capacity=1, refill_per_min=0.0)
        assert limiter.allow("c") == 0.0
        assert limiter.allow("c") > 0

    def test_per_client_isolation(self) -> None:
        limiter = TokenBucket(capacity=1, refill_per_min=0.0)
        assert limiter.allow("a") == 0.0
        assert limiter.allow("b") == 0.0

    def test_is_rate_limiter(self) -> None:
        assert isinstance(TokenBucket(), RateLimiter)


class TestValidation:
    def test_valid_payload(self) -> None:
        payload = {"trajectory": {"steps": []}, "error": "boom"}
        assert validate_payload(payload) == payload

    def test_missing_trajectory(self) -> None:
        with pytest.raises(McpValidationError) as exc_info:
            validate_payload({"error": "boom"})
        assert any("trajectory" in e for e in exc_info.value.errors)

    def test_wrong_type(self) -> None:
        with pytest.raises(McpValidationError):
            validate_payload({"trajectory": {"steps": []}, "tags": "not-a-list"})

    def test_bad_quality_label(self) -> None:
        with pytest.raises(McpValidationError):
            validate_payload({"trajectory": {}, "quality_label": "bogus"})

    def test_legacy_bare_trajectory_wrapped(self) -> None:
        traj = {"steps": [], "task": "t"}
        assert validate_report_failure(json.dumps(traj)) == {"trajectory": traj}

    def test_invalid_json(self) -> None:
        with pytest.raises(McpValidationError):
            validate_report_failure("{nope")


class TestServerGuard:
    def _server(self, tmp_path, **kwargs):
        from cauterule.mcp.server import CauteruleMCPServer
        from cauterule.store.manager import StoreManager

        return CauteruleMCPServer(StoreManager(base_dir=str(tmp_path)), **kwargs)

    def test_stdio_skips_enforcement(self, tmp_path) -> None:
        server = self._server(tmp_path, auth_mode="bearer", auth_tokens=["s"])
        client, error = server._guard()
        assert (client, error) == ("stdio", None)

    def test_remote_unauthenticated_rejected(self, tmp_path, monkeypatch) -> None:
        server = self._server(tmp_path, auth_mode="bearer", auth_tokens=["s"])
        monkeypatch.setattr(server, "_request_headers", staticmethod(lambda: {"X-A": "b"}))
        _, error = server._guard()
        assert error is not None and error["status"] == 401

    def test_remote_authenticated_allowed(self, tmp_path, monkeypatch) -> None:
        server = self._server(tmp_path, auth_mode="bearer", auth_tokens=["s"])
        monkeypatch.setattr(
            server, "_request_headers", staticmethod(lambda: {"Authorization": "Bearer s"})
        )
        client, error = server._guard()
        assert error is None
        assert client.startswith("token:")

    def test_remote_malformed_payload_rejected(self, tmp_path, monkeypatch) -> None:
        server = self._server(tmp_path, auth_mode="bearer", auth_tokens=["s"])
        monkeypatch.setattr(
            server, "_request_headers", staticmethod(lambda: {"Authorization": "Bearer s"})
        )
        _, error = server._guard(payload_check=json.dumps({"error": "x"}))
        assert error is not None and error["status"] == 400

    def test_remote_rate_limited(self, tmp_path, monkeypatch) -> None:
        from cauterule.mcp.ratelimit import TokenBucket

        server = self._server(
            tmp_path, auth_mode="bearer", auth_tokens=["s"],
            rate_limiter=TokenBucket(capacity=1, refill_per_min=0.0),
        )
        monkeypatch.setattr(
            server, "_request_headers", staticmethod(lambda: {"Authorization": "Bearer s"})
        )
        _, first = server._guard()
        assert first is None
        _, second = server._guard()
        assert second is not None and second["status"] == 429
