"""Export to CLAUDE.md format.

CLAUDE.md is a Markdown convention file that Claude (and compatible agents) read
to understand project-level standing rules.
"""

from __future__ import annotations

from cauterule.models.rule import StandingRule

from .redaction import redact_export


def export(rules: list[StandingRule]) -> str:
    """Format *rules* as a CLAUDE.md Markdown string."""
    lines: list[str] = ["# Standing Rules", "", "## Rules", ""]
    for i, rule in enumerate(rules, 1):
        trigger = redact_export(rule.when.trigger)
        directive = redact_export(rule.do.directive)
        lines.append(f"### Rule {i}")
        lines.append("")
        lines.append(f"- **When:** {trigger}")
        lines.append(f"- **Do:** {directive}")
        if rule.do.because:
            because = redact_export(rule.do.because)
            lines.append(f"- **Because:** {because}")
        if rule.tags:
            lines.append(f"- **Tags:** {', '.join(rule.tags)}")
        lines.append(f"- **Confidence:** {rule.confidence:.2f}")
        lines.append("")
    return "\n".join(lines)
