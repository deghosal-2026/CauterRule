"""Consolidation engine — merge overlapping rules, archive losers."""

from __future__ import annotations

from dataclasses import replace

from cauterule.models.conflict import ConflictReport
from cauterule.models.rule import StandingRule


def _normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())


def consolidate(
    rules: list[StandingRule],
) -> tuple[list[StandingRule], list[ConflictReport]]:
    """Merge overlapping active rules and archive losers.

    Strategy:
      1. Identify all contradiction and overlap pairs.
      2. For each conflict, keep the more specific rule (higher specificity
         determined heuristically by context count + trigger word count) and
         supersede the other.
      3. Return the modified rule list and conflict reports.
    """
    reports: list[ConflictReport] = []
    merged: dict[str, StandingRule] = {r.id: r for r in rules}

    processed: set[tuple[str, str]] = set()

    active = [r for r in rules if r.status == "active"]
    for i in range(len(active)):
        for j in range(i + 1, len(active)):
            a, b = active[i], active[j]
            if _normalize(a.when.trigger) != _normalize(b.when.trigger):
                continue
            if _normalize(a.do.directive) == _normalize(b.do.directive):
                continue
            if (a.id, b.id) in processed or (b.id, a.id) in processed:
                continue
            processed.add((a.id, b.id))

            a_spec = len(a.when.context) + len(a.when.trigger.split())
            b_spec = len(b.when.context) + len(b.when.trigger.split())

            if a_spec >= b_spec:
                winner, loser = a, b
            else:
                winner, loser = b, a

            if loser.id not in merged or merged[loser.id].status != "active":
                continue

            merged[loser.id] = replace(loser, status="superseded")
            reports.append(
                ConflictReport(
                    type="contradiction",
                    rules=(winner.id, loser.id),
                    trigger=winner.when.trigger,
                    resolution=(
                        f"Consolidated: '{loser.id}' superseded by '{winner.id}' "
                        f"(higher specificity)"
                    ),
                )
            )

    return list(merged.values()), reports
