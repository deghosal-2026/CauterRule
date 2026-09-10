"""JSONL serialization for Trajectory.

Each trajectory is stored as a single JSON object per line, streamable.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from cauterule.log import get_logger
from cauterule.models.trajectory import Trajectory

_log = get_logger(__name__)


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


def load_trajectories(
    path: str | Path,
    *,
    strict: bool = False,
    on_skip: Callable[[int, str], None] | None = None,
) -> Iterator[Trajectory]:
    """Stream trajectories from a JSONL file at *path*.

    Skips blank lines. Malformed lines are skipped with a warning
    (file:line + error) unless *strict* is True, in which case the
    first bad line raises (#597). When *on_skip* is given it is called
    with ``(line_number, error_message)`` for every skipped line so
    callers can expose a skip count.
    """
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                yield load_trajectory(stripped)
            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
                message = f"{p}:{lineno}: skipping bad JSONL line ({exc})"
                if strict:
                    raise ValueError(message) from exc
                _log.warning(message)
                if on_skip is not None:
                    on_skip(lineno, str(exc))


@dataclass(frozen=True)
class LoadResult:
    """Outcome of :func:`load_trajectories_result`."""

    loaded: list[Trajectory]
    skipped: int
    errors: list[str] = field(default_factory=list)


def load_trajectories_result(path: str | Path, *, strict: bool = False) -> LoadResult:
    """Load all trajectories from *path*, collecting skip info (#597)."""
    errors: list[str] = []

    def _record(lineno: int, error: str) -> None:
        errors.append(f"line {lineno}: {error}")

    loaded = list(load_trajectories(path, strict=strict, on_skip=_record))
    return LoadResult(loaded=loaded, skipped=len(errors), errors=errors)


def append_trajectory(trajectory: Trajectory, path: str | Path) -> None:
    """Append a single *trajectory* to a JSONL file at *path*."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(dump_trajectory(trajectory) + "\n")
