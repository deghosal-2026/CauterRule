"""Store health report — coverage, stale rules, conflicts, etc."""

from __future__ import annotations

from datetime import UTC, datetime
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
            - ``stale_rules``: rules with no hits or never matched recently
            - ``coverage_gaps``: tags with few active rules
    """
    rules = load_rules_from_dir(base_dir)

    total = len(rules)
    by_status: dict[str, int] = {}
    confidences: list[float] = []
    active_rules: list[StandingRule] = []
    tag_counts: dict[str, int] = {}

    for r in rules:
        by_status[r.status] = by_status.get(r.status, 0) + 1
        confidences.append(r.confidence)
        if r.status == "active":
            active_rules.append(r)
            for t in r.tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    total_hits = sum(r.hit_count for r in active_rules)
    avg_effectiveness = total_hits / len(active_rules) if active_rules else 0.0

    stale_rules = [
        r.id for r in active_rules if r.hit_count == 0
    ]

    coverage_gaps = {
        tag: count
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1])
        if count == 1
    }

    now = datetime.now(UTC).isoformat()

    return {
        "total_rules": total,
        "by_status": by_status,
        "avg_confidence": round(avg_confidence, 4),
        "avg_effectiveness": round(avg_effectiveness, 4),
        "stale_rules": stale_rules,
        "coverage_gaps": coverage_gaps,
        "report_time": now,
    }
