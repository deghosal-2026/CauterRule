"""
Reference-corpus expansion for #489 — replay recall fix.

Replay recall is near zero (0.05–0.10) because the reference corpus (~230
curated trajectories) is too small. This script generates 270+ paraphrase
trajectories across 30+ canonical failure classes, each with multiple task
wordings × multiple step-error variants (cross product), all carrying the same
failure_class. Output: corpus/public/reference-expansion/.

Usage:
  python scripts/generate-reference-expansion.py
  python scripts/normalize-corpus.py --path corpus/public/reference-expansion
  pytest tests/corpus/ -q
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from itertools import product
from pathlib import Path

BASE = Path("corpus/public/reference-expansion")
TS = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

# (tool, command, error) step variants — distinct real diagnostics per class.
# tasks: paraphrased descriptions. Variants = tasks x steps (cross product).
CANONICAL: list[dict] = [
    {
        "failure_class": "git/push/non-fast-forward",
        "domain": "git",
        "severity": "medium",
        "expected_rule": "when git push fails with non-fast-forward, pull --rebase before pushing",
        "tasks": [
            "Push local feature branch to remote",
            "Push commits to shared main branch",
            "Push my changes to upstream",
        ],
        "steps": [
            ("bash", "git push origin main", "! [rejected] non-fast-forward"),
            ("bash", "git push", "Updates were rejected because the remote contains work"),
            ("bash", "git push origin HEAD", "failed to push some refs"),
        ],
    },
    {
        "failure_class": "git/merge/conflict",
        "domain": "git",
        "severity": "high",
        "expected_rule": "when git merge fails with conflicts, resolve each conflicted file before committing",
        "tasks": [
            "Merge feature branch into main",
            "Merge my branch into develop",
            "Integrate feature into main",
        ],
        "steps": [
            ("bash", "git merge feature", "CONFLICT in src/auth.py"),
            ("bash", "git merge develop", "Auto-merging failed, fix conflicts"),
            ("bash", "git merge main", "CONFLICT (modify/delete) in config.yaml"),
        ],
    },
    {
        "failure_class": "git/pull/conflict",
        "domain": "git",
        "severity": "medium",
        "expected_rule": "when git pull fails with local changes conflict, stash or commit first",
        "tasks": [
            "Pull latest from origin",
            "Pull remote changes with uncommitted work",
            "Sync local branch with origin",
        ],
        "steps": [
            ("bash", "git pull origin main", "Your local changes would be overwritten"),
            ("bash", "git pull", "untracked files would be overwritten"),
            ("bash", "git pull origin develop", "local changes to src/x.py would be overwritten"),
        ],
    },
    {
        "failure_class": "git/rebase/conflict",
        "domain": "git",
        "severity": "high",
        "expected_rule": "when git rebase fails with conflicts, resolve each conflict and continue the rebase",
        "tasks": ["Rebase onto latest main", "Rebase feature onto develop", "Rebase local commits"],
        "steps": [
            ("bash", "git rebase main", "CONFLICT: Merge conflict in app.py"),
            ("bash", "git rebase origin/main", "could not apply commit — fix conflicts"),
            ("bash", "git rebase --onto", "failed to merge, resolve and run git rebase --continue"),
        ],
    },
    {
        "failure_class": "git/checkout/branch-missing",
        "domain": "git",
        "severity": "low",
        "expected_rule": "when git checkout fails with branch not found, fetch the remote branch first",
        "tasks": [
            "Switch to feature branch",
            "Checkout remote branch",
            "Create and switch to new branch",
        ],
        "steps": [
            ("bash", "git checkout feature/x", "error: pathspec 'feature/x' did not match"),
            ("bash", "git checkout origin/feature", "Remote branch not found"),
            ("bash", "git checkout -b feature", "fatal: a branch named 'feature' already exists"),
        ],
    },
    {
        "failure_class": "git/clone/auth-failed",
        "domain": "git",
        "severity": "medium",
        "expected_rule": "when git clone fails with permission denied, verify SSH key or token access",
        "tasks": [
            "Clone the repo for the project",
            "Clone a private repository",
            "Clone from GitHub",
        ],
        "steps": [
            ("bash", "git clone git@github.com:org/repo.git", "Permission denied (publickey)"),
            ("bash", "git clone https://github.com/org/repo", "fatal: could not read Username"),
            ("bash", "git clone git@github.com:org/repo", "remote: Repository not found"),
        ],
    },
    {
        "failure_class": "python/import/module-not-found",
        "domain": "python",
        "severity": "low",
        "expected_rule": "when python import fails with ModuleNotFoundError, install the missing package",
        "tasks": [
            "Run pytest after adding new dependency",
            "Run script that needs a package",
            "Start the notebook server script",
        ],
        "steps": [
            (
                "bash",
                "python -c 'import requests'",
                "ModuleNotFoundError: No module named 'requests'",
            ),
            ("bash", "python app.py", "ModuleNotFoundError: No module named 'yaml'"),
            ("bash", "python train.py", "ImportError: cannot import name 'foo'"),
        ],
    },
    {
        "failure_class": "python/syntax-error",
        "domain": "python",
        "severity": "medium",
        "expected_rule": "when python fails with SyntaxError, check for missing colons or indentation",
        "tasks": ["Run the migration script", "Run the data pipeline", "Run the flask app"],
        "steps": [
            ("bash", "python migrate.py", "SyntaxError: invalid syntax"),
            ("bash", "python pipeline.py", "SyntaxError: unexpected indent"),
            ("bash", "python app.py", "SyntaxError: ':' expected"),
        ],
    },
    {
        "failure_class": "python/dependency/version-conflict",
        "domain": "python",
        "severity": "high",
        "expected_rule": "when pip install fails with version conflict, pin compatible versions",
        "tasks": [
            "Install project dependencies",
            "Install a new package with pip",
            "Set up the environment",
        ],
        "steps": [
            (
                "bash",
                "pip install -r requirements.txt",
                "dependency resolver could not find a satisfying version",
            ),
            ("bash", "pip install fastapi", "package versions have conflicting dependencies"),
            (
                "bash",
                "pip install -r requirements-dev.txt",
                "Cannot install -r requirements (line 12) because A requires B<2",
            ),
        ],
    },
    {
        "failure_class": "pip/install/permission-denied",
        "domain": "python",
        "severity": "medium",
        "expected_rule": "when pip install fails with permission denied, use a virtualenv or --user flag",
        "tasks": [
            "Install the CLI tool globally",
            "Install package without venv",
            "Upgrade a system package",
        ],
        "steps": [
            ("bash", "pip install my-cli", "PermissionError: [Errno 13] Permission denied"),
            ("bash", "pip install requests", "could not create site-packages: Permission denied"),
            ("bash", "pip install --upgrade pip", "PermissionError: [Errno 13]"),
        ],
    },
    {
        "failure_class": "pytest/no-tests-collected",
        "domain": "testing",
        "severity": "low",
        "expected_rule": "when pytest runs with no tests collected, check test file naming and paths",
        "tasks": ["Run the test suite", "Run a specific test file", "Run tests for a module"],
        "steps": [
            ("bash", "pytest tests/", "no tests ran in 0.01s"),
            ("bash", "pytest test_app.py", "ERROR: file not found"),
            ("bash", "pytest tests/unit", "collected 0 items"),
        ],
    },
    {
        "failure_class": "pytest/assertion-error",
        "domain": "testing",
        "severity": "medium",
        "expected_rule": "when pytest fails an assertion, inspect the actual vs expected and fix the code or test",
        "tasks": ["Run unit tests", "Run the e2e test suite", "Run integration tests"],
        "steps": [
            ("bash", "pytest tests/test_auth.py", "assert 200 == 500"),
            ("bash", "pytest tests/e2e", "AssertionError: 'expected' != 'actual'"),
            ("bash", "pytest tests/integration", "FAILED test_x - assert response.status == 201"),
        ],
    },
    {
        "failure_class": "docker/build/package-not-found",
        "domain": "docker",
        "severity": "high",
        "expected_rule": "when docker build fails with package not found, add apt-get install to Dockerfile",
        "tasks": [
            "Build web service image",
            "Build image with build dependencies",
            "Build app container",
        ],
        "steps": [
            ("bash", "docker build -t svc .", "E: Unable to locate package libpq-dev"),
            ("bash", "docker build .", "gcc: command not found during pip install"),
            (
                "bash",
                "docker build -t app .",
                "RUN apt-get install libffi-dev -> Unable to locate package",
            ),
        ],
    },
    {
        "failure_class": "docker/run/port-conflict",
        "domain": "docker",
        "severity": "medium",
        "expected_rule": "when docker run fails with port in use, stop the conflicting container or change the port",
        "tasks": [
            "Start postgres container",
            "Run web container on 8080",
            "Launch redis container",
        ],
        "steps": [
            (
                "bash",
                "docker run -p 5432:5432 postgres",
                "listen tcp :5432: bind: Address already in use",
            ),
            (
                "bash",
                "docker run -p 8080:80 web",
                "Bind for 0.0.0.0:8080 failed: port is already allocated",
            ),
            ("bash", "docker run -p 6379:6379 redis", "Address already in use"),
        ],
    },
    {
        "failure_class": "docker/build/no-space",
        "domain": "docker",
        "severity": "high",
        "expected_rule": "when docker build fails with no space left, prune old images and build cache",
        "tasks": ["Build CI image", "Build and push image", "Build the deploy image"],
        "steps": [
            ("bash", "docker build .", "No space left on device while extracting /app"),
            ("bash", "docker build -t img .", "failed to solve: no space left on device"),
            ("bash", "docker build .", "write /var/lib/docker: no space left on device"),
        ],
    },
    {
        "failure_class": "docker/compose/service-unhealthy",
        "domain": "docker",
        "severity": "medium",
        "expected_rule": "when docker compose marks a service unhealthy, inspect logs and fix the healthcheck",
        "tasks": [
            "Bring up the stack with compose",
            "Start the compose services",
            "Run compose up in CI",
        ],
        "steps": [
            ("bash", "docker compose up", "Container db is unhealthy"),
            (
                "bash",
                "docker compose -f stack.yml up",
                "dependency failed to start: service unhealthy",
            ),
            ("bash", "docker compose up -d", "waiting for healthy: timeout"),
        ],
    },
    {
        "failure_class": "terraform/plan/error",
        "domain": "devops",
        "severity": "medium",
        "expected_rule": "when terraform plan fails, resolve validation or backend errors before applying",
        "tasks": [
            "Preview infra changes",
            "Run plan for AWS provider",
            "Plan with a variable file",
        ],
        "steps": [
            ("bash", "terraform plan", "Error: Invalid value for 'x' variable"),
            ("bash", "terraform plan -target module.x", "Error: Error loading the configuration"),
            ("bash", "terraform plan -var-file=prod.tfvars", "'var' could not be found"),
        ],
    },
    {
        "failure_class": "terraform/apply/error",
        "domain": "devops",
        "severity": "high",
        "expected_rule": "when terraform apply fails, fix the resource conflict or state and re-apply",
        "tasks": [
            "Apply infra changes",
            "Apply with new resource",
            "Apply to production workspace",
        ],
        "steps": [
            ("bash", "terraform apply -auto-approve", "Error: Invalid terraform state"),
            ("bash", "terraform apply", "Error applying plan"),
            ("bash", "terraform apply", "The remote workspace is locked"),
        ],
    },
    {
        "failure_class": "terraform/init/backend-conflict",
        "domain": "devops",
        "severity": "medium",
        "expected_rule": "when terraform init fails with backend conflict, remove the stale state lock",
        "tasks": [
            "Initialize the terraform backend",
            "Re-init after backend change",
            "Init for a new workspace",
        ],
        "steps": [
            ("bash", "terraform init", "Error: Failed to configure backend"),
            ("bash", "terraform init -reconfigure", "Error: bucket does not exist"),
            ("bash", "terraform init", "state lock: already locked by PID"),
        ],
    },
    {
        "failure_class": "deploy/timeout",
        "domain": "devops",
        "severity": "high",
        "expected_rule": "when deployment times out, check health endpoint and roll back if unhealthy",
        "tasks": [
            "Deploy service to production",
            "Deploy web app via CI",
            "Push new version to prod",
        ],
        "steps": [
            ("bash", "kubectl rollout", "deployment timed out waiting for rollout"),
            ("bash", "aws deploy", "timeout while waiting for the app to become healthy"),
            ("bash", "fly deploy", "Timed out waiting for the release to become ready"),
        ],
    },
    {
        "failure_class": "k8s/deploy/image-not-found",
        "domain": "devops",
        "severity": "medium",
        "expected_rule": "when kubectl deploy fails with image not found, verify the image tag exists and is pushed",
        "tasks": [
            "Deploy a service with kubectl",
            "Apply deployment manifest",
            "Roll out a new pod image",
        ],
        "steps": [
            ("bash", "kubectl apply -f svc.yaml", "container image 'repo/app:latest' not found"),
            ("bash", "kubectl create deployment", "image not found or access denied"),
            ("bash", "kubectl set image", "manifest pull: image not found"),
        ],
    },
    {
        "failure_class": "k8s/pod/crashloop",
        "domain": "devops",
        "severity": "high",
        "expected_rule": "when a pod enters CrashLoopBackOff, inspect logs and fix the startup command",
        "tasks": ["Check pod status", "Restart the failing pod", "Diagnose a crashing service"],
        "steps": [
            ("bash", "kubectl get pods", "app-pod CrashLoopBackOff"),
            ("bash", "kubectl logs app-pod", "Error: required env var missing"),
            ("bash", "kubectl describe pod", "Back-off restarting failed container"),
        ],
    },
    {
        "failure_class": "k8s/ingress/timeout",
        "domain": "devops",
        "severity": "medium",
        "expected_rule": "when ingress times out, verify the backend service is up and the path matches",
        "tasks": [
            "Reach the service through ingress",
            "Test the public endpoint",
            "Curl the ingress host",
        ],
        "steps": [
            ("bash", "curl https://app.example.com", "upstream timed out"),
            ("bash", "kubectl get ingress", "backend service not found"),
            ("bash", "curl -k host", "504 Gateway Time-out"),
        ],
    },
    {
        "failure_class": "shell/command-not-found",
        "domain": "shell",
        "severity": "low",
        "expected_rule": "when a shell command fails with command not found, install the tool or add it to PATH",
        "tasks": ["Run the build tool", "Use the package manager", "Run the test runner"],
        "steps": [
            ("bash", "make build", "make: command not found"),
            ("bash", "yarn install", "zsh: command not found: yarn"),
            ("bash", "pytest", "pytest: command not found"),
        ],
    },
    {
        "failure_class": "shell/permission-denied",
        "domain": "shell",
        "severity": "medium",
        "expected_rule": "when a script fails with permission denied, chmod +x or invoke with the interpreter",
        "tasks": ["Run the deploy script", "Execute the setup script", "Run the init script"],
        "steps": [
            ("bash", "./deploy.sh", "zsh: permission denied: ./deploy.sh"),
            ("bash", "./setup.sh", "bash: ./setup.sh: Permission denied"),
            ("bash", "./init.sh", "Permission denied"),
        ],
    },
    {
        "failure_class": "shell/syntax-error",
        "domain": "shell",
        "severity": "medium",
        "expected_rule": "when a shell script fails with syntax error, check for unmatched quotes or missing 'then'",
        "tasks": ["Run the migration script", "Execute the deploy hook", "Run the build script"],
        "steps": [
            ("bash", "sh migrate.sh", "syntax error near unexpected token"),
            ("bash", "bash deploy.sh", "unexpected end of file"),
            ("bash", "sh build.sh", "syntax error: unterminated string"),
        ],
    },
    {
        "failure_class": "ssh/permission-denied",
        "domain": "shell",
        "severity": "medium",
        "expected_rule": "when ssh fails with permission denied, verify the key has the right permissions and is authorized",
        "tasks": [
            "SSH into the server",
            "Connect to the bastion host",
            "Run a remote command over SSH",
        ],
        "steps": [
            ("bash", "ssh user@host", "Permission denied (publickey)"),
            ("bash", "ssh prod-bastion", "user@prod: Permission denied"),
            ("bash", "ssh user@host 'uptime'", "publickey: permission denied"),
        ],
    },
    {
        "failure_class": "npm/install/fetch-error",
        "domain": "javascript",
        "severity": "medium",
        "expected_rule": "when npm install fails to fetch a package, clear the cache or check the registry URL",
        "tasks": ["Install npm dependencies", "Add a new package", "Rebuild node_modules"],
        "steps": [
            ("bash", "npm install", "fetch failed with status 404"),
            ("bash", "npm install express", "ENOTFOUND registry.npmjs.org"),
            ("bash", "npm ci", "npm ERR! network request failed"),
        ],
    },
    {
        "failure_class": "ci/pipeline/passing-broken",
        "domain": "ci",
        "severity": "high",
        "expected_rule": "when CI passes but the build is broken locally or at runtime, the pipeline is not trustworthy",
        "tasks": ["Merge a PR after CI", "Deploy after green pipeline", "Cut a release after CI"],
        "steps": [
            ("bash", "gh pr merge", "CI green but tests crash on main"),
            ("bash", "ci run", "pipeline passed but server 500s"),
            ("bash", "ci tag", "CI green but release binary is broken"),
        ],
    },
    {
        "failure_class": "ci/cache-stale",
        "domain": "ci",
        "severity": "medium",
        "expected_rule": "when CI fails due to a stale cache, clear the cache and re-run with a fresh one",
        "tasks": ["Rerun failed CI job", "Run CI with cached deps", "Rerun a flaky CI build"],
        "steps": [
            ("bash", "replay failed job", "pip dependency cache is stale"),
            ("bash", "ci rerun", "restored stale build cache -> build breaks"),
            ("bash", "ci run", "stale node_modules cache -> missing new package"),
        ],
    },
    {
        "failure_class": "github/push/protected-branch",
        "domain": "git",
        "severity": "medium",
        "expected_rule": "when git push to a protected branch is rejected, open a PR instead of pushing directly",
        "tasks": ["Push to main directly", "Push a hotfix to main", "Force push to develop"],
        "steps": [
            ("bash", "git push origin main", "protected branch hook declined"),
            ("bash", "git push origin main", "cannot push to a protected branch"),
            (
                "bash",
                "git push --force origin develop",
                "force push to protected branch not allowed",
            ),
        ],
    },
    {
        "failure_class": "pytest/fixtures/error",
        "domain": "testing",
        "severity": "medium",
        "expected_rule": "when pytest fails with a fixture error, check the fixture scope and teardown",
        "tasks": [
            "Run tests that use a shared fixture",
            "Run tests with the db fixture",
            "Run the conftest-dependent tests",
        ],
        "steps": [
            ("bash", "pytest tests/", "ERROR at setup of test_x: fixture 'db' not found"),
            ("bash", "pytest tests/unit", "fixture 'tmp_path' scope mismatch"),
            ("bash", "pytest", "fixture teardown raised an error"),
        ],
    },
]


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    total = 0
    for canon in CANONICAL:
        fc = canon["failure_class"]
        file_key = fc.replace("/", "__")
        records: list[dict] = []
        for i, (task, (tool, cmd, err)) in enumerate(product(canon["tasks"], canon["steps"])):
            records.append(
                {
                    "trajectory_id": f"ref-{file_key}-{i + 1:03d}",
                    "id": f"ref-{file_key}-{i + 1:03d}",
                    "timestamp": TS,
                    "task": task,
                    "steps": [
                        {"step_number": 1, "tool": tool, "input": cmd, "output": None, "error": err}
                    ],
                    "success": False,
                    "failure_point": "step_1",
                    "failure_class": fc,
                    "quality_label": "clear",
                    "domain": canon["domain"],
                    "severity": canon["severity"],
                    "tags": fc.split("/"),
                    "expected_rule": canon["expected_rule"],
                    "source": "reference-expansion",
                    "source_repo": "CauterRule",
                    "redacted": False,
                    "expected_outcome": "should_extract",
                    "expected_outcome_rationale": f"Canonical failure: {fc}",
                    "expected_outcome_confidence": "high",
                }
            )
            total += 1
        path = BASE / f"{file_key}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r) + "\n")
    print(f"Reference expansion: wrote {total} trajectories -> {BASE}")
    print(f"  canonical failure classes: {len(CANONICAL)}")
    print("  next: python scripts/normalize-corpus.py --path corpus/public/reference-expansion")
    print("        pytest tests/corpus/ -q")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
