"""Tests for the Terraform provider issue tracker converter (#704)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from cauterule.models.trajectory import Trajectory

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "convert_terraform_issues_to_corpus.py"

_ISSUES = [
    {
        "number": 1001,
        "title": "terraform apply fails with state lock",
        "body": "Error: Error acquiring the state lock: ConditionalCheckFailedException: The conditional request failed\nLock Info: dynamodb state lock contention",
    },
    {
        "number": 1002,
        "title": "resource already exists",
        "body": "Error: creating S3 Bucket (my-bucket): BucketAlreadyExists: The requested bucket name is not available. resource already exists",
    },
    {
        "number": 1003,
        "title": "provider auth failure",
        "body": "Error: No valid credential sources found: failed to get credentials: AccessDenied, auth failure, no valid credential sources",
    },
    {
        "number": 1004,
        "title": "dependency cycle error",
        "body": "Error: Cycle: aws_instance.foo, aws_security_group.bar dependency cycle detected",
    },
    {
        "number": 1005,
        "title": "drift detected on next plan",
        "body": "Note: Objects have changed outside of Terraform. drift detected: perpetual diff, resource drift",
    },
    {
        "number": 1006,
        "title": "provisioning timeout",
        "body": "Error: waiting for EKS Cluster to create: timeout while waiting for state to become 'ACTIVE' (timeout - last state: 'CREATING')",
    },
]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("convert_terraform_issues", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_classify_and_extract() -> None:
    module = _load()
    assert (
        module.classify("Error acquiring the state lock: ConditionalCheckFailedException")
        == "lifecycle/terraform/state_lock"
    )
    assert (
        module.classify("BucketAlreadyExists resource already exists")
        == "lifecycle/terraform/already_exists"
    )
    assert (
        module.classify("No valid credential sources found AccessDenied auth failure")
        == "lifecycle/terraform/auth"
    )
    assert (
        module.classify("Cycle: aws_instance.foo dependency cycle")
        == "lifecycle/terraform/dependency_cycle"
    )
    assert (
        module.classify("drift detected objects have changed outside")
        == "lifecycle/terraform/drift"
    )
    assert (
        module.classify("timeout while waiting for state to become ACTIVE")
        == "lifecycle/terraform/timeout"
    )
    assert module.classify("nothing relevant at all") == "lifecycle/terraform/issue"
    error = module.extract_error("```\nError: state lock failed\n```")
    assert "state lock failed" in error.lower()


def test_convert_produces_schema_valid_and_balanced_records() -> None:
    module = _load()
    records = module.convert_terraform_issues(_ISSUES)
    for record in records:
        Trajectory.from_dict(record)
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]
    assert len(failures) == 6
    assert successes
    assert failures[0]["source_repo"] == "hashicorp/terraform-provider-aws"
    assert failures[0]["expected_outcome"] == "should_extract"
    assert failures[0]["failure_class"].startswith("lifecycle/")
    assert failures[0]["steps"][0]["error"]
    # check expected failure_class mapping for known samples
    by_num = {r["trajectory_id"]: r for r in failures}
    assert by_num["terraform-issue-1001"]["failure_class"] == "lifecycle/terraform/state_lock"
    assert by_num["terraform-issue-1004"]["failure_class"] == "lifecycle/terraform/dependency_cycle"


def test_convert_respects_limit() -> None:
    module = _load()
    assert (
        len([r for r in module.convert_terraform_issues(_ISSUES * 5, limit=2) if not r["success"]])
        == 2
    )


def test_cli_writes_failure_and_success_files(tmp_path: Path) -> None:
    module = _load()
    src = tmp_path / "issues.json"
    src.write_text(json.dumps(_ISSUES), encoding="utf-8")
    out = tmp_path / "lifecycle_infra"
    succ = tmp_path / "successes"
    module.main(
        ["--issues", str(src), "--output", str(out), "--success-output", str(succ), "--limit", "2"]
    )
    failure_rows = [
        json.loads(line)
        for line in (out / "terraform-issues.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    success_rows = [
        json.loads(line)
        for line in (succ / "terraform-successes.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert len(failure_rows) == 2 and success_rows
    for record in failure_rows + success_rows:
        Trajectory.from_dict(record)
