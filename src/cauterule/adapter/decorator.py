"""@cauterule.watch decorator."""

from __future__ import annotations

import functools
import time
import uuid
from typing import Any, Callable

from cauterule.capture.failure import detect_failure_class, detect_failure_point
from cauterule.capture.metadata import enrich_trajectory
from cauterule.capture.step import StepCollector
from cauterule.capture.writer import write_trajectory
from cauterule.models.trajectory import Trajectory


def watch(
    func: Callable[..., Any] | None = None,
    *,
    base_dir: str = "trajectories",
    capture_success: bool = True,
) -> Callable[..., Any]:
    """Decorator to capture a trajectory for an agent function.

    Wraps *func*: on call, collects a single step representing the function
    invocation. On success creates a ``Trajectory`` with ``success=True``,
    on exception with ``success=False``. The trajectory is enriched and
    written to ``trajectories/YYYY-MM-DD/`` via :func:`write_trajectory`.

    Can be used as ``@watch`` or ``@watch(base_dir=\"...\")``.

    Args:
        func: Function to wrap.
        base_dir: Base directory for trajectory files.
        capture_success: If ``False``, only failures are captured.
    """

    def decorator(inner: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(inner)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            collector = StepCollector()
            start = time.time()
            try:
                result = inner(*args, **kwargs)
                if not capture_success:
                    return result
                # Success step.
                collector.add(
                    tool=inner.__name__,
                    input=str({"args": args, "kwargs": kwargs})[:2000],
                    output=str(result)[:2000],
                    state={"duration": time.time() - start},
                )
                steps = collector.steps()
                traj = Trajectory(
                    id=f"T-{uuid.uuid4().hex[:8]}",
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    task=inner.__name__,
                    steps=steps,
                    success=True,
                    failure_point=detect_failure_point(steps),
                    failure_class=detect_failure_class(steps),
                )
                traj = enrich_trajectory(traj)
                write_trajectory(traj, base_dir=base_dir)
                return result
            except Exception as exc:
                collector.add(
                    tool=inner.__name__,
                    input=str({"args": args, "kwargs": kwargs})[:2000],
                    error=str(exc),
                    state={"duration": time.time() - start},
                )
                steps = collector.steps()
                traj = Trajectory(
                    id=f"T-{uuid.uuid4().hex[:8]}",
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    task=inner.__name__,
                    steps=steps,
                    success=False,
                    failure_point=detect_failure_point(steps),
                    failure_class=detect_failure_class(steps),
                )
                traj = enrich_trajectory(traj)
                write_trajectory(traj, base_dir=base_dir)
                raise

        return wrapper

    if func is not None and callable(func):
        return decorator(func)
    return decorator
