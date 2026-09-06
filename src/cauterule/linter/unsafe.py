"""Unsafe directive check — blocks dangerous actions."""

from __future__ import annotations

_DANGEROUS_PATTERNS: list[tuple[str, str]] = [
    ("rm -rf", "use of rm -rf is destructive"),
    ("force push", "force push (--force) can destroy remote history"),
    ("push --force", "force push can destroy remote history"),
    ("drop table", "DROP TABLE is destructive"),
    ("delete from", "DELETE FROM without WHERE clause is destructive"),
    ("> /dev/sda", "writing to block device is unsafe"),
    ("chmod 777", "world-writable permissions are unsafe"),
    ("chown -R", "recursive ownership change may be unsafe"),
    ("dd if=", "dd command can destroy data"),
    (":(){ :|:& };:", "fork bomb is unsafe"),
]


def check_unsafe(directive: str) -> list[str]:
    """Return warnings if directive contains dangerous patterns."""
    lower = directive.lower()
    return [f"unsafe: {reason}" for pat, reason in _DANGEROUS_PATTERNS if pat in lower]