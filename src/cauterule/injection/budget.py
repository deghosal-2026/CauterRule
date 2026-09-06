"""Context budget optimizer — rank rules, compress, fit token budget."""
from __future__ import annotations

from cauterule.injection.ordering import order_by_specificity
from cauterule.models.rule import RuleDo, RuleWhen, StandingRule


def _compress_rule(rule: StandingRule) -> StandingRule:
    """Return a compressed version with trigger + directive only."""
    return StandingRule(
        id=rule.id,
        when=RuleWhen(trigger=rule.when.trigger, context=()),
        do=RuleDo(directive=rule.do.directive, because=None),
        confidence=rule.confidence,
        provenance=rule.provenance,
        status=rule.status,
        promoted_at=rule.promoted_at,
        tags=(),
        taxonomy=None,
    )


def _one_liner(rule: StandingRule) -> StandingRule:
    """Return a one-liner version: 'When {trigger} → Do {directive}'."""
    one_line = f"When {rule.when.trigger} → Do {rule.do.directive}"
    return StandingRule(
        id=rule.id,
        when=RuleWhen(trigger=rule.when.trigger, context=()),
        do=RuleDo(directive=one_line, because=None),
        confidence=rule.confidence,
        provenance=rule.provenance,
        status=rule.status,
        promoted_at=rule.promoted_at,
        tags=(),
        taxonomy=None,
    )


def _rule_token_estimate(rule: StandingRule) -> int:
    total = len(rule.when.trigger.split()) * 2
    total += len(rule.do.directive.split()) * 2
    total += sum(len(c.split()) * 2 for c in rule.when.context)
    if rule.do.because:
        total += len(rule.do.because.split()) * 2
    total += len(rule.tags) * 2
    if rule.taxonomy:
        total += 3
    total += 10  # formatting overhead
    return total


def optimize_budget(rules: list[StandingRule], max_tokens: int = 4096) -> list[StandingRule]:
    """Select and order rules to fit within *max_tokens*.

    Rules are first ranked by specificity (most specific first) and then
    greedily selected until the estimated token budget is exhausted.
    Rules that do not fit are compressed to trigger + directive only.
    If still too tight after compression, they are rendered as a one-liner.
    If still too tight, the rule is dropped.

    Args:
        rules: List of standing rules to consider.
        max_tokens: Maximum allowed token count (default 4096).

    Returns:
        Subset of *rules* that fits within the budget, ordered by specificity.
    """
    ranked = order_by_specificity(rules)
    selected: list[StandingRule] = []
    running_total = 0
    for rule in ranked:
        cost = _rule_token_estimate(rule)
        if running_total + cost <= max_tokens:
            selected.append(rule)
            running_total += cost
            continue
        compressed = _compress_rule(rule)
        cost = _rule_token_estimate(compressed)
        if running_total + cost <= max_tokens:
            selected.append(compressed)
            running_total += cost
            continue
        mini = _one_liner(rule)
        cost = _rule_token_estimate(mini)
        if running_total + cost <= max_tokens:
            selected.append(mini)
            running_total += cost
    return selected
