"""JSONL serialization for Trajectory.

Each trajectory is stored as a single JSON object per line, streamable.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from cauterule.models.trajectory import Trajectory


def dump_trajectory(trajectory: Trajectory) -> str:
    """Serialize *trajectory* to a JSON string (one line)."""
    return json.dumps(trajectory.to_dict(), ensure_ascii=False)


def load_trajectory(line: str) -> Trajectory:
    """Deserialize a JSON line to a :class:`Trajectory`."""
    data = json.loads(line)
    if not isinstance(data, dict):
        raise ValueError("JSONL line must decode to a mapping")
    return Trajectory.from_dict(data)


def dump_trajectories(trajectories: Iterable[Trajectory], path: str | Path) -> None:
    """Write *trajectories* to *path* as JSONL (one per line)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for t in trajectories:
            f.write(dump_trajectory(t) + "\n")


def load_trajectories(path: str | Path) -> Iterator[Trajectory]:
    """Stream trajectories from a JSONL file at *path*.

    Yields :class:`Trajectory` objects one by one. Skips blank lines.
    """
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            yield load_trajectory(stripped)


def append_trajectory(trajectory: Trajectory, path: str | Path) -> None:
    """Append a single *trajectory* to a JSONL file at *path*."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(dump_trajectory(trajectory) + "\n")
