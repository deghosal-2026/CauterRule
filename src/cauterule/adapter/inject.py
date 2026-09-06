"""cauterule.inject() context manager."""

from __future__ import annotations

import contextlib
from collections.abc import Generator
from typing import Any

from cauterule.models.rule import StandingRule


@contextlib.contextmanager
def inject(
    task: str,
    rules: list[StandingRule] | None = None,
    **kwargs: Any,
) -> Generator[list[StandingRule], None, None]:
    """Context manager that prepares context with matching rules.

    In v0.1.0 this is a structured matcher stub: it filters *rules* by
    simple substring match on ``when.trigger`` and ``task``. Future versions
    will use the full injection engine with specificity ordering and budgets.

    Args:
        task: Task description to match rules against.
        rules: Optional list of promoted rules to filter. If ``None``, yields empty list.
        **kwargs: Additional context (tool, error, etc.) — reserved for future.

    Yields:
        List of matching :class:`StandingRule` objects.
    """
    _ = kwargs  # reserved
    if rules is None:
        yield []
        return

    # Simple substring matching: if trigger appears in task (case-insensitive).
    task_lower = task.lower()
    matched: list[StandingRule] = []
    for rule in rules:
        trigger = rule.when.trigger.lower()
        if trigger and trigger in task_lower:
            matched.append(rule)
        elif not trigger:
            continue
        # Also check context items: if any context phrase in task, boost (already matched).
        # For now, no additional filtering.

    yield matched
