"""Index file manager — maintains ``rules/index.yaml``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from cauterule.models.rule import StandingRule


class IndexManager:
    """Read/write the rule-store index file.

    The index is a YAML mapping with a single ``rules`` key containing a
    list of rule entries: ``{rules: [{id, status, summary, tags, taxonomy, hit_count, last_match, pack}]}``.
    """

    def __init__(self, base_dir: str = "rules") -> None:
        """IndexManager(*base_dir*).

        Args:
            base_dir: Directory that contains ``index.yaml``.
        """
        self.base_dir = Path(base_dir)

    @property
    def _index_path(self) -> Path:
        return self.base_dir / "index.yaml"

    def _ensure_dir(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def load_index(self) -> dict[str, Any]:
        """Return the full index dict.

        Returns:
            The parsed YAML contents (a dict), or an empty dict if the
            index file does not exist.
        """
        path = self._index_path
        if not path.is_file():
            return {"rules": []}
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict) and "rules" in data:
            return data
        return {"rules": []}

    def save_index(self, entries: dict[str, Any]) -> None:
        """Write *entries* to ``index.yaml``.

        Args:
            entries: A serializable dict with a ``rules`` key.
        """
        self._ensure_dir()
        with self._index_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(entries, fh, sort_keys=False, allow_unicode=True)

    def add_entry(self, rule: StandingRule) -> None:
        """Append an index entry for *rule*.

        Args:
            rule: The rule whose metadata to index.
        """
        index = self.load_index()
        rules_list: list[dict[str, Any]] = index.get("rules", [])
        entry: dict[str, Any] = {
            "id": rule.id,
            "status": rule.status,
            "summary": f"when={rule.when.trigger!r} do={rule.do.directive!r}",
            "tags": list(rule.tags) if rule.tags else [],
            "hit_count": rule.hit_count,
            "last_match": rule.last_match,
            "pack": rule.pack,
        }
        if rule.taxonomy is not None:
            entry["taxonomy"] = rule.taxonomy
        rules_list.append(entry)
        index["rules"] = rules_list
        self.save_index(index)

    def remove_entry(self, rule_id: str) -> None:
        """Remove the index entry for *rule_id*.

        Args:
            rule_id: Id of the entry to remove.
        """
        index = self.load_index()
        rules_list: list[dict[str, Any]] = index.get("rules", [])
        index["rules"] = [e for e in rules_list if e.get("id") != rule_id]
        self.save_index(index)

    def update_entry(self, rule: StandingRule) -> None:
        """Refresh the index entry for *rule*.

        Args:
            rule: The rule whose metadata to update in the index.
        """
        index = self.load_index()
        rules_list: list[dict[str, Any]] = index.get("rules", [])
        entry: dict[str, Any] = {
            "id": rule.id,
            "status": rule.status,
            "summary": f"when={rule.when.trigger!r} do={rule.do.directive!r}",
            "tags": list(rule.tags) if rule.tags else [],
            "hit_count": rule.hit_count,
            "last_match": rule.last_match,
            "pack": rule.pack,
        }
        if rule.taxonomy is not None:
            entry["taxonomy"] = rule.taxonomy
        for i, existing in enumerate(rules_list):
            if existing.get("id") == rule.id:
                rules_list[i] = entry
                break
        else:
            rules_list.append(entry)
        index["rules"] = rules_list
        self.save_index(index)
