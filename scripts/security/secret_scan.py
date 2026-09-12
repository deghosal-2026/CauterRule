#!/usr/bin/env python3
"""Custom secret-regex scan for CI (#620).

Walks tracked source files, applies a set of high-signal secret patterns, and
fails if any match is found outside a file explicitly marked ``SECURITY-FIXTURE``
(intentional fake credentials in redaction/adversarial tests).

Usage:
    python scripts/security/secret_scan.py [paths...]

Exit codes:
    0 — no unmarked secrets found
    1 — unmarked secret-like matches found
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".venv",
    ".venv312",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".benchmarks",
    "dist",
    "build",
    "node_modules",
    "htmlcov",
    ".egg-info",
}

SKIP_SUFFIXES = {".pyc", ".pyo", ".so", ".dylib", ".whl", ".gz", ".db", ".bin", ".png", ".jpg"}

FIXTURE_MARKER = "SECURITY-FIXTURE"

SELF_EXCLUDE = {
    "scripts/security/secret_scan.py",
    ".github/workflows/security-scan.yml",
    ".trufflehog-exclude-paths.txt",
}

SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "stripe_key": re.compile(r"(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"),
    "jwt": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "generic_secret_assignment": re.compile(
        r"""(?i)(?:api[_-]?key|secret|token|password|passwd|pwd)\s*[:=]\s*['"]?[A-Za-z0-9_\-]{20,}"""
    ),
}


def _iter_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix in SKIP_SUFFIXES:
                continue
            files.append(path)
    return files


def _scan_file(path: Path, relative: str) -> list[tuple[str, int, str, str]]:
    findings: list[tuple[str, int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings
    if FIXTURE_MARKER in text:
        return findings
    for line_number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(line):
                findings.append((name, line_number, line.strip(), relative))
    return findings


def main(argv: list[str]) -> int:
    roots = [Path(arg) for arg in argv[1:]] or [Path()]
    findings: list[tuple[str, int, str, str]] = []
    for path in _iter_files(roots):
        relative = path.as_posix()
        if relative in SELF_EXCLUDE:
            continue
        findings.extend(_scan_file(path, relative))

    if findings:
        print("Secret-like matches found outside SECURITY-FIXTURE files:")
        for name, line_number, line, relative in sorted(findings, key=lambda f: f[3]):
            print(f"  [{name}] {relative}:{line_number}: {line[:120]}")
        return 1

    print("Secret regex scan clean — no unmarked matches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
