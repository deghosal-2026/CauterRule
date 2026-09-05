"""Per-rule hit counter — aggregate hit counts across the rule store."""

from __future__ import annotations

from cauterule.store.manager import StoreManager


def get_hit_counts(store: StoreManager) -> dict[str, int]:
    """Return a dict mapping each rule id to its current hit count."""
    return {r.id: r.hit_count for r in store.list_rules()}
