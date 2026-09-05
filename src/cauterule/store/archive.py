"""Archive manager — moves retired rules to ``rules/archived/``."""

from __future__ import annotations

from pathlib import Path

from cauterule.serialization.rule_yaml import dump_rule_to_file, load_rule_from_file


def archive_rule(rule_id: str, base_dir: str = "rules") -> Path:
    """Move a retired rule file into the ``archived/`` subdirectory.

    The source file is removed after a successful copy.

    Args:
        rule_id: Id of the rule to archive.
        base_dir: Root rule-store directory.

    Returns:
        The destination :class:`Path` of the archived file.

    Raises:
        FileNotFoundError: If the rule file does not exist.
    """
    src = Path(base_dir) / f"{rule_id}.yaml"
    if not src.is_file():
        msg = f"Rule file not found: {src}"
        raise FileNotFoundError(msg)

    archive_dir = Path(base_dir) / "archived"
    archive_dir.mkdir(parents=True, exist_ok=True)
    dst = archive_dir / f"{rule_id}.yaml"

    rule = load_rule_from_file(src)
    dump_rule_to_file(rule, dst)
    src.unlink()
    return dst
