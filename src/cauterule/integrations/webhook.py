"""Webhook notifier — sends POST requests on promotion events."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, urlopen

_logger = logging.getLogger(__name__)


class WebhookNotifier:
    """Sends HTTP POST notifications when a rule is promoted.

    Args:
        url: Target webhook URL.
        timeout: Request timeout in seconds.
    """

    def __init__(self, url: str, timeout: int = 10) -> None:
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
                return 200 <= resp.status < 300
        except Exception:
            _logger.exception("Webhook POST failed for %s", self.url)
            return False