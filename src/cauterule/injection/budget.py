"""Context budget optimizer — rank rules, compress, fit token budget."""
from __future__ import annotations

from cauterule.injection.ordering import order_by_specificity
from cauterule.models.rule import StandingRule


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
    return selected
