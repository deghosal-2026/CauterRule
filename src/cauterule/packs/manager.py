"""Pack manager — discover and inspect installed rule packs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from cauterule.packs.format import PackManifest
from cauterule.store.manager import resolve_inside, validate_rule_id


def list_packs(base_dir: str = "rules") -> list[str]:
    """List available pack names under ``<base_dir>/packs/``.

    A directory is considered a pack if it contains a ``manifest.yaml`` file.

    Args:
        base_dir: Root directory for rule packs.

    Returns:
        Sorted list of pack names.
    """
    packs_root = Path(base_dir) / "packs"
    if not packs_root.is_dir():
        return []

    names: list[str] = sorted(
        p.name
        for p in packs_root.iterdir()
        if p.is_dir() and (p / "manifest.yaml").is_file()
    )
    return names


def pack_info(name: str, base_dir: str = "rules") -> dict[str, Any]:
    """Return metadata for a named pack as a plain dict.

    Args:
        name: Pack name.
        base_dir: Root directory for rule packs.

    Returns:
        A dict with manifest fields plus a ``rule_count`` key.

    Raises:
        FileNotFoundError: If the pack does not exist.
        ValueError: If *name* is unsafe for paths (#499).
    """
    validate_rule_id(name)
    manifest_path = resolve_inside(Path(base_dir) / "packs", name, "manifest.yaml")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Pack manifest not found: {manifest_path}")

    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest = PackManifest.from_dict(raw)
    info = manifest.to_dict()
    info["rule_count"] = len(manifest.rules)
    return info
