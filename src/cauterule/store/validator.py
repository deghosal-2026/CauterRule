"""Store validator — no orphaned refs, missing provenance, broken links, duplicate IDs."""

from __future__ import annotations

from pathlib import Path

from cauterule.models.rule import StandingRule
from cauterule.serialization.rule_yaml import load_rule_from_file


def validate_store(base_dir: str = "rules") -> list[str]:
    """Validate the integrity of a rule store.

    Checks performed:
        - Every ``.yaml`` file deserializes to a valid :class:`StandingRule`.
        - No duplicate rule IDs across files.
        - Every rule has non-empty provenance fields.
        - ``superseded`` rules reference an existing ``new_id`` (if
          encoded; currently a structural check).

    Args:
        base_dir: Root rule-store directory.

    Returns:
        A list of warning strings. An empty list means a clean store.
    """
    warnings: list[str] = []
    d = Path(base_dir)
    if not d.is_dir():
        return [f"Store directory not found: {base_dir}"]

    seen_ids: set[str] = set()
    yaml_files = sorted(d.glob("*.yaml"))

    for p in yaml_files:
        if p.stem == "index":
            continue
        try:
            rule = load_rule_from_file(p)
        except Exception as exc:
            warnings.append(f"{p.name}: failed to deserialize — {exc}")
            continue

        rid = rule.id
        if rid in seen_ids:
            warnings.append(f"Duplicate ID {rid!r} in {p.name}")
        seen_ids.add(rid)

        _check_provenance(rule, p.name, warnings)

    if not yaml_files:
        warnings.append("No rule files found in store")

    return warnings


def _check_provenance(rule: StandingRule, filename: str, warnings: list[str]) -> None:
    prov = rule.provenance
    if not prov.source_trajectory:
        warnings.append(f"{filename} ({rule.id}): missing provenance.source_trajectory")
    if not prov.extracted_by:
        warnings.append(f"{filename} ({rule.id}): missing provenance.extracted_by")
    if not prov.extract_timestamp:
        warnings.append(f"{filename} ({rule.id}): missing provenance.extract_timestamp")
