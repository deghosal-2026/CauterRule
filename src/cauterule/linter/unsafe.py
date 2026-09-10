"""Unsafe directive check — blocks dangerous actions."""

from __future__ import annotations

import re

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

# Regex entries for patterns substring matching cannot express (#504).
# Word boundaries matter: `\beval\b` must not trip "evaluate"/"retrieve",
# `\bexec\s*\(` must not trip "execute".
_DANGEROUS_REGEXES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\|\s*(bash|sh|zsh|fish|dash)\b"), "pipe-to-shell is unsafe"),
    (
        re.compile(r"\b(curl|wget)\b.*\|\s*(bash|sh|zsh)\b"),
        "piping remote download into a shell is unsafe",
    ),
    (re.compile(r"\beval\b"), "use of eval is unsafe"),
    (re.compile(r"\bexec\s*\("), "use of exec() is unsafe"),
    (re.compile(r"\bmkfs\b"), "mkfs formats filesystems and destroys data"),
    (re.compile(r"\brm\b.*--recursive\b"), "recursive rm is destructive"),
    (re.compile(r"\bchmod\b.*\s-[a-z]*r[a-z]*\s"), "recursive chmod may be unsafe"),
    (re.compile(r"\b(shutdown|reboot|halt|poweroff)\b"), "host shutdown/reboot is unsafe"),
    (re.compile(r"\bgit\s+clean\b.*\s+/$"), "git clean on filesystem root is unsafe"),
    (re.compile(r":\(\)\s*\{\s*:.*\}\s*;"), "fork bomb is unsafe"),
]


def check_unsafe(directive: str) -> list[str]:
    """Return warnings if directive contains dangerous patterns."""
    lower = directive.lower()
    warnings = [f"unsafe: {reason}" for pat, reason in _DANGEROUS_PATTERNS if pat in lower]
    warnings.extend(
        f"unsafe: {reason}" for pat, reason in _DANGEROUS_REGEXES if pat.search(lower)
    )
    return warnings