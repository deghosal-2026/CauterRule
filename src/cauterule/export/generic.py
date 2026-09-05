"""Export rules to generic Markdown and JSON formats."""

from __future__ import annotations

import json
from typing import Any

from cauterule.models.rule import StandingRule

from .redaction import redact_export


def export_markdown(rules: list[StandingRule]) -> str:
    """Format *rules* as generic Markdown."""
    lines: list[str] = ["# Rules", ""]
    for i, rule in enumerate(rules, 1):
        trigger = redact_export(rule.when.trigger)
        directive = redact_export(rule.do.directive)
        lines.append(f"## Rule {i}")
        lines.append("")
        lines.append(f"- **When:** {trigger}")
        lines.append(f"- **Do:** {directive}")
        if rule.do.because:
            because = redact_export(rule.do.because)
            lines.append(f"- **Because:** {because}")
        if rule.tags:
            lines.append(f"- **Tags:** {', '.join(rule.tags)}")
        lines.append(f"- **Confidence:** {rule.confidence:.2f}")
        if rule.taxonomy:
            lines.append(f"- **Taxonomy:** {rule.taxonomy}")
        lines.append("")
    return "\n".join(lines)


def _serialize_rule(rule: StandingRule) -> dict[str, Any]:
    """Serialize a rule to a JSON-safe dict with redacted strings."""
    d: dict[str, Any] = {
        "id": rule.id,
        "when": {"trigger": redact_export(rule.when.trigger), "context": list(rule.when.context)},
        "do": {"directive": redact_export(rule.do.directive)},
        "confidence": rule.confidence,
        "status": rule.status,
        "promoted_at": rule.promoted_at,
        "hit_count": rule.hit_count,
    }
    if rule.do.because:
        d["do"]["because"] = redact_export(rule.do.because)
    if rule.tags:
        d["tags"] = list(rule.tags)
    if rule.taxonomy:
        d["taxonomy"] = rule.taxonomy
    if rule.template:
        d["template"] = rule.template
    if rule.pack:
        d["pack"] = rule.pack
    return d


def export_json(rules: list[StandingRule]) -> str:
    """Format *rules* as a JSON string."""
    data = [_serialize_rule(r) for r in rules]
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
