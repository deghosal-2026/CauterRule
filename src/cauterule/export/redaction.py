"""Redact secrets from exported rule text.

Wraps the redaction engine to provide a convenience function for stripping
secrets from export output before writing to disk.
"""

from __future__ import annotations

from cauterule.redaction.engine import contains_secret, redact_text


def redact_export(text: str) -> str:
    """Strip secrets from *text* and return the redacted result.

    Uses the built-in secret patterns from :mod:`cauterule.redaction.patterns`.
    """
    return redact_text(text)


__all__ = ["contains_secret", "redact_export"]
