"""Parametrized adapter conformance suite (#540).

Every adapter's driver must pass the shared kit plus the init scaffold
matrix (``--adapter none|langgraph|crewai|pydanticai|custom`` produces a
project whose example files compile).

# SECURITY-FIXTURE: token-like strings in this module are intentional fake
# credentials used to verify redaction. None are real secrets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from tests.adapter_conformance.kit import run_kit


@pytest.mark.parametrize(
    "check",
    [
        "no_repeat_failure",
        "redaction",
        "schema_valid",
    ],
)
def test_conformance_kit(adapter_driver: Any, tmp_path: Path, check: str) -> None:
    results = run_kit(adapter_driver, tmp_path)
    matched = [r for r in results if r.startswith(("PASS", "FAIL")) and check in r]
    assert matched, f"no result for {check!r}: {results}"
    line = matched[0]
    assert line.startswith("PASS"), f"adapter={adapter_driver.name} check={check} failed: {line}"


def test_conformance_redaction_driver(tmp_path: Path) -> None:
    # Directly assert the redaction contract per adapter driver.
    for driver in _all_drivers(tmp_path):
        driver.run_task("connect with api_key=sk-secret-abcdef123456")
        traj = driver.last_trajectory()
        if traj is not None:
            for step in traj.steps:
                for text in (step.input, step.output, step.error or ""):
                    assert text is None or "sk-secret-abcdef123456" not in text, (
                        f"{driver.name} leaked secret"
                    )


def _all_drivers(tmp_path: Path) -> list[Any]:
    from tests.adapter_conformance.conftest import DRIVERS

    return [cls(base_dir=str(tmp_path / "trajectories")) for cls in DRIVERS.values()]


@pytest.mark.parametrize(
    "adapter",
    ["none", "langgraph", "crewai", "pydanticai", "custom"],
)
def test_init_scaffold_matrix(tmp_path: Path, adapter: str) -> None:
    import py_compile

    from click.testing import CliRunner

    from cauterule.cli.init import init

    target = tmp_path / "proj"
    result = CliRunner().invoke(init, ["--dir", str(target), "--adapter", adapter])
    assert result.exit_code == 0, result.output
    assert (target / "cauterule.toml").exists()
    assert (target / "rules").is_dir()
    assert (target / "trajectories").is_dir()
    if adapter != "none":
        example = target / f"agent_{adapter}_example.py"
        assert example.exists()
        py_compile.compile(str(example), doraise=True)
        assert (target / "rules" / "R-001.yaml").exists()
