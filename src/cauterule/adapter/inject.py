"""cauterule.inject() context manager."""

from __future__ import annotations

import contextlib
from collections.abc import Generator
from typing import Any

from cauterule.injection.matcher import _error_matches, _tag_matches, _tool_matches
from cauterule.models.rule import StandingRule


@contextlib.contextmanager
def inject(
    task: str,
    rules: list[StandingRule] | None = None,
    **kwargs: Any,
) -> Generator[list[StandingRule], None, None]:
    """Context manager that prepares context with matching rules.

    Uses the structured matcher from :mod:`cauterule.injection.matcher`
    so that ``tool=``, ``error=``, and ``tags=`` context is honored
    identically to the CLI injection path (#526).

    Args:
        task: Task description to match rules against.
        rules: Optional list of promoted rules to filter.
        **kwargs: Additional context (tool, error, tags, etc.).

    Yields:
        List of matching :class:`StandingRule` objects.
    """
    if rules is None:
        yield []
        return

    context_args: dict[str, Any] = {
        k: v for k, v in kwargs.items() if k in ("tool", "error", "tags")
    }

    task_lower = task.lower()
    matched: list[StandingRule] = []
    for rule in rules:
        trigger = rule.when.trigger.lower()
        if not trigger or trigger not in task_lower:
            continue
        if not _tool_matches(rule, **context_args):
            continue
        if not _error_matches(rule, **context_args):
            continue
        if not _tag_matches(rule, **context_args):
            continue
        matched.append(rule)

    yield matched
