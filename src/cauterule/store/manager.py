"""Store manager — CRUD for standing rules on the file system."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import StandingRule
from cauterule.serialization.rule_yaml import (
    dump_rule_to_file,
    load_rule_from_file,
    load_rules_from_dir,
)


class StoreManager:
    """File-system CRUD for :class:`StandingRule` instances.

    Each rule is persisted as an individual YAML file named ``<id>.yaml``
    inside *base_dir*.
    """

    def __init__(self, base_dir: str = "rules") -> None:
        """StoreManager(*base_dir*).

        Args:
            base_dir: Directory holding rule files.
        """
        self.base_dir = Path(base_dir)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _rule_path(self, rule_id: str) -> Path:
        return self.base_dir / f"{rule_id}.yaml"

    def _ensure_dir(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_rule(self, rule_id: str) -> StandingRule | None:
        """Return the rule with *rule_id*, or ``None`` if it does not exist."""
        path = self._rule_path(rule_id)
        if not path.is_file():
            return None
        return load_rule_from_file(path)

    def list_rules(self, status: str | None = None) -> list[StandingRule]:
        """Return all rules, optionally filtered by *status*.

        Args:
            status: Optional status filter (``"active"``, ``"retired"``, etc.).

        Returns:
            List of :class:`StandingRule` instances.
        """
        self._ensure_dir()
        rules = load_rules_from_dir(self.base_dir)
        if status is not None:
            rules = [r for r in rules if r.status == status]
        return rules

    def add_rule(self, rule: StandingRule) -> str:
        """Persist *rule* to disk and return its id.

        Args:
            rule: The rule to persist.

        Returns:
            The rule's id.
        """
        self._ensure_dir()
        dump_rule_to_file(rule, self._rule_path(rule.id))
        return rule.id

    def retire_rule(self, rule_id: str, reason: str) -> None:
        """Mark a rule as retired and update its ``id`` to include a suffix.

        Args:
            rule_id: Id of the rule to retire.
            reason: Reason for retirement (stored via rule provenance or
                    a status flag — currently the rule is re-written with
                    status ``"retired"``).
        """
        import time
        rule = self.get_rule(rule_id)
        if rule is None:
            msg = f"Rule {rule_id!r} not found"
            raise ValueError(msg)
        if rule.status != "active":
            msg = f"Cannot retire rule {rule_id!r}: status is {rule.status!r}"
            raise ValueError(msg)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        retired = StandingRule(
            id=rule.id,
            when=rule.when,
            do=rule.do,
            confidence=rule.confidence,
            provenance=rule.provenance,
            status="retired",
            promoted_at=rule.promoted_at,
            hit_count=rule.hit_count,
            last_match=rule.last_match,
            tags=rule.tags,
            taxonomy=rule.taxonomy,
            template=rule.template,
            pack=rule.pack,
            retired_at=now,
            retirement_reason=reason,
        )
        dump_rule_to_file(retired, self._rule_path(rule_id))

    def supersede_rule(self, rule_id: str, new_id: str) -> None:
        """Mark *rule_id* as superseded by *new_id*.

        The existing rule is re-written with status ``"superseded"``.

        Args:
            rule_id: Id of the rule to supersede.
            new_id: Id of the rule that replaces it.
        """
        import time
        rule = self.get_rule(rule_id)
        if rule is None:
            msg = f"Rule {rule_id!r} not found"
            raise ValueError(msg)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        superseded = StandingRule(
            id=rule.id,
            when=rule.when,
            do=rule.do,
            confidence=rule.confidence,
            provenance=rule.provenance,
            status="superseded",
            promoted_at=rule.promoted_at,
            hit_count=rule.hit_count,
            last_match=rule.last_match,
            tags=rule.tags,
            taxonomy=rule.taxonomy,
            template=rule.template,
            pack=rule.pack,
            retired_at=now,
            superseded_by=new_id,
        )
        dump_rule_to_file(superseded, self._rule_path(rule_id))
