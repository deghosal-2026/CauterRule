"""Injection formatter — produces clean markdown block."""
from __future__ import annotations

from cauterule.models.rule import StandingRule


def _format_single(rule: StandingRule, index: int) -> str:
    lines: list[str] = []
    lines.append(f"### Rule {index}: {rule.id}")
    lines.append(f"- **When**: {rule.when.trigger}")
    if rule.when.context:
        lines.append(f"- **Context**: {', '.join(rule.when.context)}")
    lines.append(f"- **Do**: {rule.do.directive}")
    if rule.do.because:
        lines.append(f"- **Because**: {rule.do.because}")
    if rule.tags:
        lines.append(f"- **Tags**: {', '.join(rule.tags)}")
    if rule.taxonomy:
        lines.append(f"- **Taxonomy**: {rule.taxonomy}")
    lines.append(f"- **Confidence**: {rule.confidence}")
    lines.append("")
    return "\n".join(lines)


def format_injection(rules: list[StandingRule]) -> str:
    """Produce a clean markdown block of active rules for injection.

    Args:
        rules: List of standing rules to format.

    Returns:
        A markdown string with each rule rendered as a sub-section.
        Returns ``"<!-- no active rules -->"`` when *rules* is empty.
    """
    if not rules:
        return "<!-- no active rules -->"
    blocks = [_format_single(r, i + 1) for i, r in enumerate(rules)]
    return "\n".join(blocks).strip()
