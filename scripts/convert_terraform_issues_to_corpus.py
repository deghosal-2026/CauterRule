#!/usr/bin/env python3
r"""Convert Terraform provider issue reports to a reference corpus (#704).

``hashicorp/terraform-provider-aws`` (MPL-2.0) — plus
``hashicorp/terraform-provider-azurerm`` for diversity — contains
genuine ``terraform apply``/``plan``/``destroy`` failures:
state-lock contention (DynamoDB/S3), resource-already-exists,
provider auth failures, dependency-cycle, drift-detection, and
provisioning timeouts. Each issue becomes a failure reference
trajectory under ``corpus/public/lifecycle_infra/`` with a failure
class derived from the error text; a small set of successful-apply
counterparts is emitted for #707 balance.

Usage:
    python scripts/convert_terraform_issues_to_corpus.py \
        --issues /tmp/tf.json \
        --output corpus/public/lifecycle_infra \
        --success-output corpus/public/successes \
        --limit 20

Fetch samples with gh:
    gh api "search/issues?q=repo:hashicorp/terraform-provider-aws+state+lock&per_page=15" \
        --jq '[.items[] | {number,title,body}]' > /tmp/tf.json
    gh api "repos/hashicorp/terraform-provider-aws/issues?state=all&per_page=15" \
        --jq '[.[] | {number,title,body}]' > /tmp/tf.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_TS = "2026-09-11T00:00:00+00:00"
_SOURCE_REPO = "hashicorp/terraform-provider-aws"
_ERROR_RE = re.compile(
    r"error|failed|timeout|timed out|refused|exception|unavailable|"
    r"already exists|alreadyexists|exists|lock|drift|cycle|auth|denied|credentials",
    re.IGNORECASE,
)

# Ordered from most specific to most generic.
_CLASSIFIERS: tuple[tuple[str, str], ...] = (
    ("acquiring the state lock", "lifecycle/terraform/state_lock"),
    ("state lock", "lifecycle/terraform/state_lock"),
    ("conditionalcheckfailed", "lifecycle/terraform/state_lock"),
    ("dynamodb", "lifecycle/terraform/state_lock"),
    ("state already locked", "lifecycle/terraform/state_lock"),
    ("lock info", "lifecycle/terraform/state_lock"),
    ("already exists", "lifecycle/terraform/already_exists"),
    ("alreadyexists", "lifecycle/terraform/already_exists"),
    ("bucketalreadyexists", "lifecycle/terraform/already_exists"),
    ("resource already exists", "lifecycle/terraform/already_exists"),
    ("no valid credential", "lifecycle/terraform/auth"),
    ("failed to get credentials", "lifecycle/terraform/auth"),
    ("accessdenied", "lifecycle/terraform/auth"),
    ("access denied", "lifecycle/terraform/auth"),
    ("unauthorized", "lifecycle/terraform/auth"),
    ("invalid credentials", "lifecycle/terraform/auth"),
    ("expired token", "lifecycle/terraform/auth"),
    ("no valid credential sources", "lifecycle/terraform/auth"),
    ("auth failure", "lifecycle/terraform/auth"),
    ("assume role", "lifecycle/terraform/auth"),
    ("signature", "lifecycle/terraform/auth"),
    ("credentials", "lifecycle/terraform/auth"),
    ("auth", "lifecycle/terraform/auth"),
    ("cycle", "lifecycle/terraform/dependency_cycle"),
    ("dependency cycle", "lifecycle/terraform/dependency_cycle"),
    ("cycle error", "lifecycle/terraform/dependency_cycle"),
    ("drift", "lifecycle/terraform/drift"),
    ("objects have changed outside", "lifecycle/terraform/drift"),
    ("perpetual drift", "lifecycle/terraform/drift"),
    ("perpetual diff", "lifecycle/terraform/drift"),
    ("inconsistent", "lifecycle/terraform/drift"),
    ("timeout", "lifecycle/terraform/timeout"),
    ("timed out", "lifecycle/terraform/timeout"),
    ("context deadline exceeded", "lifecycle/terraform/timeout"),
    ("waiting for", "lifecycle/terraform/timeout"),
    ("provisioning timeout", "lifecycle/terraform/timeout"),
    ("deadline", "lifecycle/terraform/timeout"),
)


def classify(body: str) -> str:
    """Derive a lifecycle/terraform failure_class from issue body text."""
    lowered = body.lower()
    # Normalize: remove punctuation for some classifiers.
    normalized = re.sub(r"[^a-z0-9]+", " ", lowered)
    # Also keep original lowered for substring matching.
    for needle, failure_class in _CLASSIFIERS:
        # Use normalized matching for multi-word needles that may have punctuation.
        needle_normalized = re.sub(r"[^a-z0-9]+", " ", needle.lower()).strip()
        if needle_normalized and needle_normalized in normalized:
            return failure_class
        if needle in lowered:
            return failure_class
    return "lifecycle/terraform/issue"


def extract_error(body: str) -> str:
    """Extract the most error-like snippet from an issue body."""
    for block in re.findall(r"```(.*?)```", body, re.DOTALL):
        if _ERROR_RE.search(block):
            return str(block).strip()[:1000]
    for line in body.splitlines():
        if _ERROR_RE.search(line):
            return str(line).strip()[:1000]
    return str(body).strip()[:1000]


def _tool_for_body(body: str) -> str:
    lowered = body.lower()
    # All terraform failures share the same tool.
    if "terraform" in lowered:
        return "terraform"
    return "terraform"


def _input_for_body(body: str) -> str:
    lowered = body.lower()
    if "destroy" in lowered:
        return "terraform destroy"
    if "plan" in lowered and "apply" not in lowered:
        return "terraform plan"
    if "apply" in lowered:
        return "terraform apply"
    # Heuristic: timeout/drift often surface on plan/apply, default to apply.
    if "drift" in lowered:
        return "terraform plan"
    return "terraform apply"


def _failure(issue: dict[str, Any], index: int, ts: str) -> dict[str, Any]:
    body = str(issue.get("body", ""))
    number = issue.get("number", index)
    tid = f"terraform-issue-{number}"
    task = str(issue.get("title", "")).strip() or f"Terraform issue {number}"
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": task,
        "steps": [
            {
                "step_number": 1,
                "tool": _tool_for_body(body),
                "input": _input_for_body(body),
                "output": None,
                "error": extract_error(body),
            }
        ],
        "success": False,
        "redacted": False,
        "failure_point": "step_1",
        "failure_class": classify(body),
        "quality_label": "noisy",
        "domain": "devops",
        "severity": "medium",
        "tags": ["reference", "lifecycle", "terraform", "infra"],
        "expected_outcome": "should_extract",
        "expected_outcome_rationale": (
            "Real Terraform failure signature from the provider issue tracker."
        ),
        "expected_outcome_confidence": "medium",
        "source": "terraform-provider-aws-issues",
        "source_repo": _SOURCE_REPO,
    }


_SUCCESS_CASES = (
    "Apply Terraform configuration to create S3 bucket",
    "Plan Terraform configuration with no changes",
    "Destroy Terraform-managed VPC and subnets",
    "Apply Terraform configuration for RDS instance provisioning",
)


def _success(index: int, case: str, ts: str) -> dict[str, Any]:
    tid = f"terraform-success-{index:03d}"
    lowered = case.lower()
    if "destroy" in lowered:
        inp = "terraform destroy"
    elif "plan" in lowered:
        inp = "terraform plan"
    else:
        inp = "terraform apply"
    output_map = {
        "terraform apply": "Apply complete! Resources: 3 added, 0 changed, 0 destroyed.",
        "terraform plan": "No changes. Your infrastructure matches the configuration.",
        "terraform destroy": "Destroy complete! Resources: 3 destroyed.",
    }
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": case,
        "steps": [
            {
                "step_number": 1,
                "tool": "terraform",
                "input": inp,
                "output": output_map.get(
                    inp,
                    "Apply complete! Resources: 1 added, 0 changed, 0 destroyed.",
                ),
                "error": None,
            }
        ],
        "success": True,
        "redacted": False,
        "failure_point": None,
        "failure_class": None,
        "quality_label": "clear",
        "domain": "devops",
        "severity": "low",
        "tags": ["reference", "lifecycle", "terraform", "success"],
        "expected_outcome": "should_silence",
        "expected_outcome_rationale": "Successful Terraform counterpart (#707 balance).",
        "expected_outcome_confidence": "high",
        "source": "terraform-provider-aws-issues",
        "source_repo": _SOURCE_REPO,
    }


def convert_terraform_issues(
    issues: list[dict[str, Any]],
    *,
    limit: int | None = None,
    timestamp: str = _TS,
) -> list[dict[str, Any]]:
    """Return failure (issues) + success reference records."""
    records: list[dict[str, Any]] = []
    for i, issue in enumerate(issues):
        if limit is not None and i >= limit:
            break
        records.append(_failure(issue, i + 1, timestamp))
    for i, case in enumerate(_SUCCESS_CASES, start=1):
        records.append(_success(i, case, timestamp))
    return records


def main(argv: list[str] | None = None) -> None:
    """Convert Terraform issues JSON and write failure + success corpus files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issues", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--success-output", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    issues = json.loads(args.issues.read_text(encoding="utf-8"))
    if isinstance(issues, dict) and "items" in issues:
        issues = issues["items"]
    records = convert_terraform_issues(issues, limit=args.limit)
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / "terraform-issues.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in failures) + "\n", encoding="utf-8")
    print(f"[convert] {len(failures)} failures -> {out}")

    if args.success_output is not None:
        args.success_output.mkdir(parents=True, exist_ok=True)
        success_out = args.success_output / "terraform-successes.jsonl"
        success_out.write_text(
            "\n".join(json.dumps(r) for r in successes) + "\n", encoding="utf-8"
        )
        print(f"[convert] {len(successes)} successes -> {success_out}")


if __name__ == "__main__":
    main()
