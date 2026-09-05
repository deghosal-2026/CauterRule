"""Overlap detector — non-contradictory overlapping triggers."""

from __future__ import annotations

from cauterule.models.conflict import ConflictReport
from cauterule.models.rule import StandingRule


def _normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())


def _tokenize(s: str) -> set[str]:
    return set(_normalize(s).split())


def detect_overlaps(rules: list[StandingRule]) -> list[ConflictReport]:
    """Return ConflictReports for active rules with overlapping trigger keywords that are not direct contradictions."""  # noqa: E501
    reports: list[ConflictReport] = []
    active = [r for r in rules if r.status == "active"]
    for i in range(len(active)):
        for j in range(i + 1, len(active)):
            a, b = active[i], active[j]
            a_tokens = _tokenize(a.when.trigger)
            b_tokens = _tokenize(b.when.trigger)
            common = a_tokens & b_tokens
            if not common:
                continue
            if _normalize(a.when.trigger) == _normalize(b.when.trigger):
                continue
            if _normalize(a.do.directive) == _normalize(b.do.directive):
                continue
            reports.append(
                ConflictReport(
                    type="overlap",
                    rules=(a.id, b.id),
                    trigger=a.when.trigger,
                    resolution=f"Rules '{a.id}' and '{b.id}' share trigger keywords "
                    f"({', '.join(sorted(common))}) but differ in directives: "
                    f"'{a.do.directive}' vs '{b.do.directive}'",
                )
            )
    return reports
