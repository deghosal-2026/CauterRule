"""
THIS FILE IS NOT PART OF THE CAUTERULE PACKAGE.

It is a maintenance script that regenerates all M7 corpus data under
corpus/public/ from the canonical golden scenarios in field-test/corpus/.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from cauterule.models.trajectory import Step, Trajectory

BASE = Path("corpus/public")

# ── helpers ──────────────────────────────────────────────────────────
TS = datetime.now(UTC).isoformat()


def write_jsonl(dirname: str, records: list[dict]) -> None:
    d = BASE / dirname
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{dirname}.jsonl"
    with p.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"  wrote {len(records)} → {p}")


def traj_to_dict(t: Trajectory) -> dict:
    d = t.to_dict()
    # Ensure trajectory_id present
    d.setdefault("trajectory_id", t.id)
    return d


# ── 1. Golden families ──────────────────────────────────────────────
# Each GOLDEN gets a JSONL (the trajectory) + ≥2 rule YAMLs.

GOLDEN_SCENARIOS = [
    {
        "id": "G-001-git-push-non-ff",
        "task": "Push local feature branch commits to remote main",
        "domain": "git",
        "failure_class": "git/push/non-fast-forward",
        "expected_rule": "when git push fails with non-fast-forward, pull latest changes before pushing",
        "abstractions": [
            (
                "Run git pull --rebase before pushing",
                "Remote has commits that local doesn't, non-fast-forward blocks push",
            ),
            (
                "Pull remote changes first via git pull --rebase, then retry push",
                "Local branch is behind remote; rebase preserves commit history",
            ),
        ],
        "steps": [
            Step(1, "bash", "git push origin feature/login", None, "! [rejected] non-fast-forward"),
            Step(2, "bash", "git pull --rebase origin main", "Successfully rebased", None),
        ],
    },
    {
        "id": "G-002-python-import",
        "task": "Run pytest suite after adding new dependency",
        "domain": "python",
        "failure_class": "python/import/module-not-found",
        "expected_rule": "when python import fails with ModuleNotFoundError, install the missing package",
        "abstractions": [
            (
                "Install missing Python package with pip before importing",
                "ModuleNotFoundError means the dependency is not installed",
            ),
            (
                "Add the missing dependency to requirements.txt then pip install -r",
                "Dependencies should be tracked in requirements.txt for reproducibility",
            ),
        ],
        "steps": [
            Step(
                1,
                "bash",
                "python -c 'import requests'",
                None,
                "ModuleNotFoundError: No module named 'requests'",
            ),
            Step(2, "bash", "pip install requests", "Successfully installed requests"),
        ],
    },
    {
        "id": "G-003-docker-build",
        "task": "Build Docker image for Python web service",
        "domain": "docker",
        "failure_class": "docker/build/package-not-found",
        "expected_rule": "when docker build fails with package not found, add apt-get install to Dockerfile",
        "abstractions": [
            (
                "Add apt-get install command to Dockerfile before pip install",
                "Base image lacks build dependencies; apt-get install must precede pip",
            ),
            (
                "Install system packages in Dockerfile with apt-get update && apt-get install",
                "apt-get update ensures package list is current before installing",
            ),
        ],
        "steps": [
            Step(1, "bash", "docker build -t svc .", None, "Package 'libpq-dev' not found"),
            Step(
                2,
                "edit",
                "RUN apt-get update && apt-get install -y libpq-dev",
                "Dockerfile updated",
            ),
        ],
    },
    {
        "id": "G-004-pip-conflict",
        "task": "Install Python project dependencies",
        "domain": "python",
        "failure_class": "python/pip/dependency-conflict",
        "expected_rule": "when pip install fails with dependency conflict, create a fresh virtualenv and install",
        "abstractions": [
            (
                "Create a virtualenv first, then pip install inside it",
                "Dependency conflicts arise from global site-packages; virtualenv isolates",
            ),
            (
                "Use pip install --no-deps for conflicting transitive dependencies",
                "Minimizes upgrade ripple by pinning only direct dependencies",
            ),
        ],
        "steps": [
            Step(
                1,
                "bash",
                "pip install flask>=2.0",
                None,
                "ERROR: pip's dependency resolver conflict",
            ),
            Step(
                2,
                "bash",
                "python -m venv .venv && source .venv/bin/activate && pip install flask",
                "Installed flask 2.3",
            ),
        ],
    },
    {
        "id": "G-005-kubectl-crd",
        "task": "Deploy custom resource to Kubernetes cluster",
        "domain": "devops",
        "failure_class": "k8s/deploy/crd-not-found",
        "expected_rule": "when kubectl apply fails with CRD not found, install the CRD first",
        "abstractions": [
            (
                "Apply the CRD manifest first, then apply the custom resource",
                "Custom resources require their CRD to exist in the cluster first",
            ),
            (
                "Use kubectl apply --server-side for CRD installation",
                "Server-side apply avoids client-side validation errors for unknown kinds",
            ),
        ],
        "steps": [
            Step(
                1,
                "bash",
                "kubectl apply -f my-custom-resource.yaml",
                None,
                "error: unable to recognize: no matches for kind",
            ),
            Step(
                2,
                "bash",
                "kubectl apply -f crd.yaml && kubectl apply -f my-custom-resource.yaml",
                "customresource created",
            ),
        ],
    },
    {
        "id": "G-006-test-assertion",
        "task": "Run pytest after code refactor",
        "domain": "python",
        "failure_class": "python/test/assertion-error",
        "expected_rule": "when pytest fails with assertion error, compare actual vs expected output",
        "abstractions": [
            (
                "Add debug print before the assertion to see actual output",
                "Assertion errors only show expected values; debug prints reveal actual",
            ),
            (
                "Use pytest -s --tb=long to capture full traceback and stdout",
                "Long traceback mode shows intermediate values for assertion debugging",
            ),
        ],
        "steps": [
            Step(
                1,
                "bash",
                "pytest tests/",
                None,
                "FAILED test_example.py::test_transform - AssertionError",
            ),
            Step(
                2,
                "bash",
                "pytest tests/ -s --tb=long",
                "test_transform FAILED, stdout: actual=42 expected=100",
            ),
        ],
    },
    {
        "id": "G-007-api-rate-limit",
        "task": "Fetch data from external API",
        "domain": "research",
        "failure_class": "api/rate-limit/exceeded",
        "expected_rule": "when API returns 429 rate limit, back off with exponential retry",
        "abstractions": [
            (
                "Implement exponential backoff with tenacity retry decorator",
                "429 errors require retry with increasing delays; tenacity handles this",
            ),
            (
                "Add a sleep of retry_after seconds before retrying the request",
                "API response includes retry_after header; honoring it is the simplest fix",
            ),
        ],
        "steps": [
            Step(
                1, "web_fetch", "GET https://api.example.org/v1/data", None, "429 Too Many Requests"
            ),
            Step(2, "bash", "sleep 5 && curl https://api.example.org/v1/data", '{"data": [...]}'),
        ],
    },
    {
        "id": "G-008-terraform-lock",
        "task": "Run terraform apply for infrastructure provisioning",
        "domain": "devops",
        "failure_class": "terraform/state/lock-error",
        "expected_rule": "when terraform apply fails with state lock error, wait for lock to release or force unlock",
        "abstractions": [
            (
                "Wait for the state lock to release automatically then retry",
                "State locks are held by concurrent runs; waiting avoids corruption",
            ),
            (
                "Use terraform force-unlock with the lock ID after verifying no active run",
                "Force-unlock releases a stuck lock; verify safety before doing so",
            ),
        ],
        "steps": [
            Step(
                1,
                "bash",
                "terraform apply -auto-approve",
                None,
                "Error acquiring state lock: ConditionalCheckFailedException",
            ),
            Step(2, "bash", "terraform force-unlock <lock-id>", "State lock released"),
        ],
    },
    {
        "id": "G-009-selenium-element",
        "task": "Automate browser form submission",
        "domain": "browser_automation",
        "failure_class": "browser/selenium/element-not-found",
        "expected_rule": "when Selenium fails to find element, add explicit wait before interaction",
        "abstractions": [
            (
                "Add WebDriverWait with expected_conditions before find_element",
                "Dynamic pages load elements asynchronously; explicit wait handles timing",
            ),
            (
                "Use time.sleep(2) before Selenium element interaction as fallback",
                "Sleep-based approach is simpler when explicit waits are verbose",
            ),
        ],
        "steps": [
            Step(1, "search", "find_element(By.ID, 'submit-btn')", None, "NoSuchElementException"),
            Step(
                2,
                "search",
                "WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'submit-btn')))",
                "element found",
            ),
        ],
    },
    {
        "id": "G-010-deploy-timeout",
        "task": "Deploy service via CI pipeline",
        "domain": "devops",
        "failure_class": "ci/deploy/timeout",
        "expected_rule": "when CI deploy times out, increase timeout or split deployment into smaller batches",
        "abstractions": [
            (
                "Increase CI deploy timeout in pipeline configuration",
                "Long-running deployments hit default timeouts; raising the limit fixes it",
            ),
            (
                "Split deployment into rolling batches (e.g. 25% per batch)",
                "Smaller batches complete faster, avoiding wall-clock timeouts",
            ),
        ],
        "steps": [
            Step(1, "bash", "deploy.sh", None, "TIMEOUT: deployment exceeded 30 minutes"),
            Step(2, "edit", "CI_DEPLOY_TIMEOUT=3600 in pipeline config", "pipeline config updated"),
        ],
    },
]


def generate_golden() -> None:
    """Write JSONL + rule YAMLs for each golden scenario."""
    dest = BASE / "golden"
    dest.mkdir(parents=True, exist_ok=True)

    for sc in GOLDEN_SCENARIOS:
        gid = sc["id"]
        # JSONL
        t = Trajectory(
            id=gid,
            timestamp=TS,
            task=sc["task"],
            steps=tuple(sc["steps"]),
            success=False,
            failure_point="step_1",
            failure_class=sc["failure_class"],
            quality_label="clear",
            domain=sc["domain"],
            severity="medium",
            tags=(sc["domain"], "golden", gid.split("-")[-1]),
        )
        with (dest / f"{gid}.jsonl").open("w") as f:
            f.write(json.dumps(traj_to_dict(t)) + "\n")

        # Rule YAMLs — ≥2 abstractions
        for i, (directive, because) in enumerate(sc["abstractions"]):
            variant = chr(ord("a") + i)
            rule = {
                "id": f"{gid}-{variant}",
                "when": {
                    "trigger": sc["expected_rule"],
                    "context": [sc["domain"]],
                },
                "do": {
                    "directive": directive,
                    "because": because,
                },
                "confidence": 0.95,
                "provenance": {
                    "source_trajectory": gid,
                    "extracted_by": "benchmark",
                    "extract_timestamp": TS,
                    "extraction_pass": 1,
                },
                "status": "active",
                "promoted_at": TS,
                "tags": [sc["domain"], "golden"],
            }
            rule_yaml_path = dest / f"{gid}-{variant}.yaml"
            import yaml

            with rule_yaml_path.open("w") as f:
                yaml.dump(rule, f, default_flow_style=False, sort_keys=False)

        print(f"  golden {gid}: 1 JSONL + {len(sc['abstractions'])} rule YAMLs")


generate_golden()

# ── 2. Counterexample ────────────────────────────────────────
# Need 20 total. Generator already gives 3, add 17 more.
COUNTEREXAMPLES = []
for i in range(1, 21):
    domain = ["coding", "devops", "research", "support", "browser_automation"][i % 5]
    counterpart = [
        "git push succeeds after rebase",
        "docker build succeeds with updated packages",
        "API call succeeds with proper auth header",
        "kubectl apply succeeds with correct CRD",
        "pip install succeeds with fresh venv",
        "test passes with mock data",
        "deploy succeeds with longer timeout",
        "terraform apply succeeds after unlock",
        "selenium finds element with explicit wait",
        "npm build succeeds after cache clear",
    ][i % 10]
    COUNTEREXAMPLES.append(
        Trajectory(
            id=f"counterex-{i:03d}",
            timestamp=TS,
            task=f"{counterpart} (expected failure that succeeds)",
            steps=(
                Step(
                    1,
                    "bash" if i % 2 == 0 else "web_fetch",
                    f"step_1_input_{i}",
                    f"step_1_output_{i}",
                ),
                Step(
                    2, "bash" if i % 2 == 0 else "edit", f"step_2_input_{i}", f"step_2_output_{i}"
                ),
            ),
            success=True,
            quality_label="clear",
            domain=domain,
            tags=("counterexample", domain),
        )
    )
write_jsonl("counterexample", [traj_to_dict(t) for t in COUNTEREXAMPLES])

# ── 3. Near-miss ──────────────────────────────────────────────
# Need 20 total. Generator gives 3, add 17 more.
NEARMISS = []
for i in range(1, 21):
    domain = ["coding", "devops", "research", "support", "browser_automation"][i % 5]
    NEARMISS.append(
        Trajectory(
            id=f"nearmiss-{i:03d}",
            timestamp=TS,
            task=f"Almost-failure scenario {i} — first attempt fails, retry succeeds",
            steps=(
                Step(1, "bash", f"step_1_cmd_{i}", None, f"temporary_error_{i}"),
                Step(2, "bash", f"step_2_retry_{i}", f"success_after_retry_{i}"),
            ),
            success=True,
            quality_label="ambiguous",
            domain=domain,
            severity="low",
            tags=("nearmiss", domain),
        )
    )
write_jsonl("nearmiss", [traj_to_dict(t) for t in NEARMISS])

# ── 4. Staleness ──────────────────────────────────────────────
# Need 10 total. Generator gives 3, add 7 more.
STALENESS = []
for i in range(1, 11):
    STALENESS.append(
        Trajectory(
            id=f"stale-{i:03d}",
            timestamp=TS,
            task=f"Stale historical failure scenario {i} — no longer relevant",
            steps=(Step(1, "bash", f"old_command_{i}", None, f"deprecated_error_{i}"),),
            success=i % 2 != 0,
            failure_point="step_1" if i % 2 == 0 else None,
            failure_class=f"deprecated/{['tool', 'config', 'env', 'workflow'][i % 4]}/{i}"
            if i % 2 == 0
            else None,
            quality_label="misleading",
            domain=["coding", "devops", "research", "support", "browser_automation"][i % 5],
            severity="low",
            tags=("staleness", "deprecated"),
        )
    )
write_jsonl("staleness", [traj_to_dict(t) for t in STALENESS])

# ── 5. Synthetic ──────────────────────────────────────────────
# Need 50 total. Tiered builder gave 30, add 20 more.
# Generate 20 simple success + failure trajectories
SYNTHETIC = []
for i in range(31, 51):
    success = i % 3 != 0
    domain = ["coding", "devops", "research", "support", "browser_automation"][i % 5]
    SYNTHETIC.append(
        Trajectory(
            id=f"synth-{i:03d}",
            timestamp=TS,
            task=f"Synthetic task {i} — {'success' if success else 'failure'}",
            steps=(
                Step(
                    1,
                    "bash",
                    f"input_{i}_1",
                    f"output_{i}_1" if success else None,
                    None if success else f"error_{i}_1",
                ),
                Step(2, "edit", f"input_{i}_2", f"output_{i}_2", None),
            ),
            success=success,
            failure_point="step_1" if not success else None,
            failure_class=f"synthetic/{domain}/type-{i % 3}" if not success else None,
            quality_label="clear",
            domain=domain,
            severity="low" if not success else None,
            tags=("synthetic", "public", domain),
        )
    )
write_jsonl("synthetic", [traj_to_dict(t) for t in SYNTHETIC])

print(
    "\nDone. Run `python scripts/normalize-corpus.py --path corpus/public` to backfill expected_outcome."
)
