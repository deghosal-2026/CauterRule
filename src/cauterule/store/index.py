"""Index file manager — maintains ``rules/index.yaml``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from cauterule.models.rule import StandingRule


class IndexManager:
    """Read/write the rule-store index file.

    The index is a YAML mapping of ``{rule_id: {metadata...}}`` stored at
    ``<base_dir>/index.yaml``.
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
            return {}
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}

    def save_index(self, entries: dict[str, Any]) -> None:
        """Write *entries* to ``index.yaml``.

        Args:
            entries: A serializable dict.
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
        index[rule.id] = {
            "status": rule.status,
            "confidence": rule.confidence,
            "promoted_at": rule.promoted_at,
            "tags": list(rule.tags),
        }
        self.save_index(index)

    def remove_entry(self, rule_id: str) -> None:
        """Remove the index entry for *rule_id*.

        Args:
            rule_id: Id of the entry to remove.
        """
        index = self.load_index()
        index.pop(rule_id, None)
        self.save_index(index)

    def update_entry(self, rule: StandingRule) -> None:
        """Refresh the index entry for *rule*.

        Args:
            rule: The rule whose metadata to update in the index.
        """
        self.add_entry(rule)
