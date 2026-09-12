"""Source-trust / prompt-injection signal detection (#727).

Extraction can mine a rule from a trajectory whose tool output was itself an
adversarial payload. Replay + linter cannot tell such a rule apart from one
mined from a real failure, so the production promotion gate needs a *source*
signal, not a content signal. This module detects injection signatures in a
trajectory's tool I/O.
"""

from __future__ import annotations

import re

from cauterule.models.trajectory import Trajectory

# Known prompt-injection / instruction-override markers (case-insensitive).
_INJECTION_MARKERS: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous",
    "ignore the above",
    "disregard previous",
    "disregard the above",
    "disregard all prior",
    "system prompt",
    "you are now",
    "developer mode",
    "jailbreak",
    "<|im_start|>",
    "<|system|>",
    "[inst]",
    "### instruction",
    "override your",
    "do not follow the",
)

# Long base64 blobs are a common injection-obfuscation vector. Detection
# requires base64-specific punctuation (``+`` / ``/`` / padding ``=``) so that
# ordinary 40-char git SHAs and hex digests — which are ubiquitous in tool
# output — are NOT flagged as payloads.
_B64_RE = re.compile(r"[A-Za-z0-9+/]{60,}={0,2}")


def _has_encoded_blob(text: str) -> bool:
    for match in _B64_RE.finditer(text):
        blob = match.group(0)
        if "+" in blob or "/" in blob or blob.endswith("="):
            return True
    return False


def detect_injection_signal(trajectory: Trajectory) -> bool:
    """Return True if any step's tool I/O carries an injection signature."""
    for step in trajectory.steps:
        text = f"{step.input or ''}\n{step.output or ''}"
        if not text.strip():
            continue
        lowered = text.lower()
        if any(marker in lowered for marker in _INJECTION_MARKERS):
            return True
        if _has_encoded_blob(text):
            return True
    return False


def is_source_tainted(trajectory: Trajectory) -> bool:
    """Return True if the trajectory is flagged tainted or carries a signal."""
    return bool(trajectory.injection_signal) or detect_injection_signal(trajectory)
