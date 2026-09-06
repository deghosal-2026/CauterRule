"""Export to aider.conf.yml format.

aider.conf.yml is a YAML configuration file that aider reads for
convention/rule settings.
"""

from __future__ import annotations

from cauterule.models.rule import StandingRule

from .redaction import redact_export


def export(rules: list[StandingRule], include_retired: bool = False) -> str:
    """Format *rules* as an aider.conf.yml YAML string.

    Only active rules are exported unless *include_retired* is ``True``.
    """
    if not include_retired:
        rules = [r for r in rules if r.status == "active"]
    if not rules:
        return "# No rules\nrules: []\n"

    lines: list[str] = ["# Standing rules for aider", "rules:"]
    for rule in rules:
        trigger = redact_export(rule.when.trigger)
        directive = redact_export(rule.do.directive)
        lines.append(f'  - when: "{trigger}"')
        lines.append(f'    do: "{directive}"')
        if rule.do.because:
            because = redact_export(rule.do.because)
            lines.append(f'    because: "{because}"')
        if rule.tags:
            tags_str = ", ".join(f'"{t}"' for t in rule.tags)
            lines.append(f"    tags: [{tags_str}]")
    lines.append("")
    return "\n".join(lines)
