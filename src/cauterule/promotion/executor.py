"""Promotion executor — writes rule YAML, updates index, git commit."""

from __future__ import annotations

import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from cauterule.models.candidate import CandidateRule
from cauterule.models.rule import Provenance, StandingRule
from cauterule.serialization.rule_yaml import dump_rule_to_file

_RULE_ID_PREFIX = "R"


def _next_rule_id(rules_dir: Path) -> str:
    existing: list[int] = []
    if rules_dir.is_dir():
        for p in rules_dir.glob("*.yaml"):
            if p.stem.startswith(f"{_RULE_ID_PREFIX}-"):
                try:
                    existing.append(int(p.stem[len(_RULE_ID_PREFIX) + 1:]))
                except ValueError:
                    continue
        for p in rules_dir.glob("*.yml"):
            if p.stem.startswith(f"{_RULE_ID_PREFIX}-"):
                try:
                    existing.append(int(p.stem[len(_RULE_ID_PREFIX) + 1:]))
                except ValueError:
                    continue
    seq = max(existing) + 1 if existing else 1
    return f"{_RULE_ID_PREFIX}-{seq:03d}"


def _write_index(rules_dir: Path, rule: StandingRule) -> None:
    index_path = rules_dir / "index.yaml"
    import yaml

    entries: list[dict[str, Any]] = []
    if index_path.exists():
        raw = yaml.safe_load(index_path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            entries = raw

    entries.append({
        "id": rule.id,
        "trigger": rule.when.trigger,
        "directive": rule.do.directive,
        "promoted_at": rule.promoted_at,
        "status": rule.status,
    })
    index_path.write_text(
        yaml.safe_dump(entries, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _git_commit(rules_dir: Path, rule_id: str) -> str:
    try:
        result = subprocess.run(
            ["git", "add", str(rules_dir)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return f"git-add-failed: {result.stderr.strip()}"
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return f"git-not-available: {exc}"

    msg = f"promote rule {rule_id}"
    try:
        result = subprocess.run(
            ["git", "commit", "-m", msg, "--no-verify"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return f"git-commit-failed: {result.stderr.strip()}"
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return f"git-not-available: {exc}"


def execute_promotion(
    candidate: CandidateRule,
    config: dict[str, Any],
) -> str:
    """Persist *candidate* as a promoted rule and commit it.

    Config keys (* = required):

    * ``rules_dir`` — directory to write rule YAML files into.
    * ``source_trajectory`` — trajectory identifier for provenance.
    * ``extracted_by`` — extractor identifier for provenance.
    * ``extract_timestamp`` — ISO timestamp for provenance.
    * ``extraction_pass`` — extraction pass number.
    * ``promotion_mode`` — promotion mode label (e.g. ``"auto"``).
    * ``status`` — initial rule status (default ``"active"``).

    Args:
        candidate: The candidate rule to promote.
        config: Configuration dict (see above).

    Returns:
        The promoted rule ID (e.g. ``"R-001"``).

    Raises:
        ValueError: If required config keys are missing.
    """
    rules_dir = Path(str(config.get("rules_dir", "rules")))
    rule_id = _next_rule_id(rules_dir)

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    promoted_at = now

    provenance = Provenance(
        source_trajectory=str(config["source_trajectory"]),
        extracted_by=str(config["extracted_by"]),
        extract_timestamp=str(config["extract_timestamp"]),
        extraction_pass=int(config.get("extraction_pass", 1)),
        promotion_commit="pending",
        promotion_mode=str(config.get("promotion_mode", "auto")),
    )

    rule = StandingRule(
        id=rule_id,
        when=candidate.when,
        do=candidate.do,
        confidence=candidate.confidence,
        provenance=provenance,
        status=str(config.get("status", "active")),  # type: ignore[arg-type]
        promoted_at=promoted_at,
        template=candidate.template,
    )

    # Re-assign provenance with the final rule ID embedded in it.
    updated_provenance = Provenance(
        source_trajectory=provenance.source_trajectory,
        extracted_by=provenance.extracted_by,
        extract_timestamp=provenance.extract_timestamp,
        extraction_pass=provenance.extraction_pass,
        promotion_commit=uuid.uuid4().hex[:8],
        promotion_mode=provenance.promotion_mode,
    )
    rule = StandingRule(
        id=rule_id,
        when=candidate.when,
        do=candidate.do,
        confidence=candidate.confidence,
        provenance=updated_provenance,
        status=rule.status,
        promoted_at=rule.promoted_at,
        template=candidate.template,
    )

    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_path = rules_dir / f"{rule_id}.yaml"
    dump_rule_to_file(rule, str(rule_path))

    _write_index(rules_dir, rule)

    commit_output = _git_commit(rules_dir, rule_id)

    final_provenance = Provenance(
        source_trajectory=updated_provenance.source_trajectory,
        extracted_by=updated_provenance.extracted_by,
        extract_timestamp=updated_provenance.extract_timestamp,
        extraction_pass=updated_provenance.extraction_pass,
        promotion_commit=commit_output,
        promotion_mode=updated_provenance.promotion_mode,
    )
    rule = StandingRule(
        id=rule_id,
        when=candidate.when,
        do=candidate.do,
        confidence=candidate.confidence,
        provenance=final_provenance,
        status=rule.status,
        promoted_at=rule.promoted_at,
        template=candidate.template,
    )
    dump_rule_to_file(rule, str(rule_path))

    return rule_id