"""Store health report — coverage, stale rules, conflicts, etc."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from cauterule.models.rule import StandingRule
from cauterule.serialization.rule_yaml import load_rules_from_dir


def health_report(base_dir: str = "rules") -> dict[str, Any]:
    """Produce a health snapshot of the rule store.

    Args:
        base_dir: Root rule-store directory.

    Returns:
        A dict with keys:
            - ``total_rules``
            - ``by_status``: counts per status
            - ``avg_confidence``
            - ``avg_effectiveness`` (hit_count / total matches heuristic)
            - ``stale_rules``: rules with last_match older than 30 days or never matched
            - ``conflict_count``: number of rules with conflicting triggers
    """
    rules = load_rules_from_dir(base_dir)

    total = len(rules)
    by_status: dict[str, int] = {}
    confidences: list[float] = []
    active_rules: list[StandingRule] = []

    for r in rules:
        by_status[r.status] = by_status.get(r.status, 0) + 1
        confidences.append(r.confidence)
        if r.status == "active":
            active_rules.append(r)

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    total_hits = sum(r.hit_count for r in active_rules)
    avg_effectiveness = total_hits / len(active_rules) if active_rules else 0.0

    now = datetime.now(UTC)
    cutoff = now - timedelta(days=30)
    stale_rules: list[str] = []
    for r in active_rules:
        if r.last_match is None:
            stale_rules.append(r.id)
            continue
        try:
            if isinstance(r.last_match, str):
                from datetime import datetime as dt_parse
                last = dt_parse.fromisoformat(r.last_match)
                if last.tzinfo is None:
                    last = last.replace(tzinfo=UTC)
                if last < cutoff:
                    stale_rules.append(r.id)
        except (ValueError, TypeError):
            stale_rules.append(r.id)

    trigger_map: dict[str, list[str]] = {}
    for r in active_rules:
        trigger_map.setdefault(r.when.trigger, []).append(r.id)
    conflict_count = sum(1 for ids in trigger_map.values() if len(ids) > 1)

    now_str = datetime.now(UTC).isoformat()

    return {
        "total_rules": total,
        "by_status": by_status,
        "avg_confidence": round(avg_confidence, 4),
        "avg_effectiveness": round(avg_effectiveness, 4),
        "stale_rules": stale_rules,
        "conflict_count": conflict_count,
        "report_time": now_str,
    }
