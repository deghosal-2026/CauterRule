"""Webhook notifier — sends POST requests on promotion events."""

from __future__ import annotations

import ipaddress
import json
import logging
import socket
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

_logger = logging.getLogger(__name__)

# Hostnames that always resolve to this machine (#508).
_LOCAL_NAMES = frozenset({"localhost", "localhost.localdomain", "ip6-localhost"})


def _validate_webhook_url(url: str) -> None:
    """Reject webhook URLs unsafe to POST to (#508).

    Allows ``http``/``https`` only; rejects loopback, link-local (cloud
    metadata, e.g. 169.254.169.254), multicast, and reserved address
    space, plus localhost-style hostnames.

    Raises:
        ValueError: If *url* is not an allowed webhook target.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        raise ValueError(f"invalid webhook URL: {url!r}") from None
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"webhook URL must use http(s): {parsed.scheme!r}")
    host = (parsed.hostname or "").lower()
    if not host or host in _LOCAL_NAMES:
        raise ValueError(f"webhook URL host not allowed: {host!r}")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        # DNS name: resolve best-effort and check the result. Unresolvable
        # names are allowed (offline/air-gapped setups) — the literal-IP
        # checks above are the hard guarantee.
        try:
            resolved = socket.gethostbyname(host)
        except OSError:
            return
        ip = ipaddress.ip_address(resolved)
    if ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        raise ValueError(f"webhook URL host not allowed: {host!r}")


class WebhookNotifier:
    """Sends HTTP POST notifications when a rule is promoted.

    Args:
        url: Target webhook URL.
        timeout: Request timeout in seconds.
    """

    def __init__(self, url: str, timeout: int = 10) -> None:
        _validate_webhook_url(url)
        self.url = url
        self.timeout = timeout

    def notify_promotion(
        self,
        rule_id: str,
        title: str,
        timestamp: str | None = None,
    ) -> bool:
        """Send a promotion event to the configured webhook URL.

        Args:
            rule_id: Identifier of the promoted rule.
            title: Human-readable title of the rule.
            timestamp: ISO-8601 timestamp; defaults to current UTC time.

        Returns:
            True if the POST succeeded (2xx), False otherwise.
        """
        payload: dict[str, Any] = {
            "event": "rule_promoted",
            "promotion": {
                "rule_id": rule_id,
                "title": title,
                "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            },
        }
        body = json.dumps(payload).encode("utf-8")
        req = Request(
            self.url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return bool(200 <= resp.status < 300)
        except Exception:
            # Log the host only — never the full URL/query (may embed
            # tokens), per #508.
            host = urlparse(self.url).hostname or "unknown-host"
            _logger.exception("Webhook POST failed for host %s", host)
            return False