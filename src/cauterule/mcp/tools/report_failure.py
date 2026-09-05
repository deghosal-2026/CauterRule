"""MCP tool: ``report_failure`` — submit a failure trajectory for extraction."""

from __future__ import annotations

from typing import Any


def report_failure(trajectory_json: str) -> dict[str, Any]:
    """Accept a trajectory JSON and trigger extraction pipeline.

    The *trajectory_json* is handed to the extraction engine for analysis
    and candidate rule generation. Currently a stub that validates the
    input and returns a result descriptor.

    Args:
        trajectory_json: JSON-serialised trajectory of the failed agent run.

    Returns:
        A dict with keys ``"accepted"`` (bool), ``"trajectory_length"``
        (int), and ``"message"`` (str).
    """
    import json

    try:
        data = json.loads(trajectory_json)
    except json.JSONDecodeError as exc:
        return {
            "accepted": False,
            "trajectory_length": 0,
            "message": f"Invalid JSON: {exc}",
        }

    if not isinstance(data, dict):
        return {
            "accepted": False,
            "trajectory_length": 0,
            "message": "Trajectory must be a JSON object",
        }

    steps = data.get("steps", []) if isinstance(data, dict) else []
    length = len(steps) if isinstance(steps, list) else 0

    return {
        "accepted": True,
        "trajectory_length": length,
        "message": f"Trajectory accepted for extraction ({length} steps).",
    }
