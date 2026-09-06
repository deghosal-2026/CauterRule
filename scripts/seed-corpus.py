#!/usr/bin/env python3
"""seed-corpus.py — Seed the field-test corpus from existing test fixtures and golden trajectories.

Usage:
    python scripts/seed-corpus.py                  # Seed from all sources
    python scripts/seed-corpus.py --status         # Show corpus stats
    python scripts/seed-corpus.py --validate       # Validate all trajectories
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CORPUS_DIR = Path("field-test/v0.1.0/corpus")
FIXTURES_DIR = Path("tests/fixtures")
GOLDEN_DIR = CORPUS_DIR / "golden"
VALID_DOMAINS = {"git", "python", "docker", "test", "ci", "deploy", "shell", "env", "workflow", "coding", "devops", "support", "discussion", "environments", "networking", "testing", "generic", "browser", "research", "browser_automation"}
VALID_LABELS = {"clear", "ambiguous", "multi-causal", "misleading", "operator-induced"}
VALID_SOURCES = {"opencode", "ci", "sibling-repos", "corrections", "manual"}


def seed_from_fixtures() -> int:
    """Copy test fixture trajectories into the corpus."""
    src_dir = FIXTURES_DIR / "trajectories"
    dst_dir = CORPUS_DIR / "raw" / "opencode"
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in sorted(src_dir.glob("*.jsonl")):
        traj_id = f"fix-{count+1:03d}-{f.stem}"
        dst_path = dst_dir / f"{traj_id}.jsonl"
        traj = json.loads(f.read_text().strip())
        traj["trajectory_id"] = traj_id
        traj["source"] = "opencode"
        traj["source_repo"] = "CauterRule"
        if "quality_label" not in traj or traj["quality_label"] not in VALID_LABELS:
            traj["quality_label"] = "clear"
        if "severity" not in traj:
            traj["severity"] = "medium"
        if "domain" not in traj:
            guess = _guess_domain(traj)
            traj["domain"] = guess
        if "failure_class" not in traj:
            traj["failure_class"] = f"{traj.get('domain', 'generic')}/failure"
        with open(dst_path, "w") as fh:
            fh.write(json.dumps(traj) + "\n")
        count += 1
    return count


def seed_from_golden() -> int:
    """Copy golden trajectories into the raw corpus as well."""
    dst_dir = CORPUS_DIR / "raw" / "opencode"
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in sorted(GOLDEN_DIR.glob("G-*.jsonl")):
        traj = json.loads(f.read_text().strip())
        traj_id = traj.get("trajectory_id", f"gld-{count+1:03d}")
        traj["source"] = "opencode"
        traj["source_repo"] = "CauterRule"
        dst_path = dst_dir / f"{traj_id}.jsonl"
        if not dst_path.exists():  # Don't overwrite
            with open(dst_path, "w") as fh:
                fh.write(json.dumps(traj) + "\n")
            count += 1
    return count


def create_failure_mode_catalog() -> int:
    """Create additional failure-mode trajectories that complete the catalog."""
    dst_dir = CORPUS_DIR / "raw" / "opencode"
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    scenarios = [
        {
            "trajectory_id": "cat-001-git-merge-conflict",
            "task": "Merge feature branch into main",
            "domain": "git",
            "failure_class": "git/merge",
            "quality_label": "clear",
            "severity": "high",
            "failure_point": "Auto-merging failed; fix conflicts and commit the result",
            "steps": [
                {"step_number": 1, "tool": "git", "input": "git checkout main && git merge feature/login", "output": "Auto-merging src/auth.py", "error": "CONFLICT in src/auth.py", "state": None},
                {"step_number": 2, "tool": "git", "input": "git status", "output": "both modified: src/auth.py", "error": None, "state": None},
            ],
            "tags": ["git", "merge", "conflict"],
            "expected_rule": "when git merge fails with conflicts, resolve each conflict file before committing",
        },
        {
            "trajectory_id": "cat-002-git-detached-head",
            "task": "Commit changes then push",
            "domain": "git",
            "failure_class": "git/detached",
            "quality_label": "clear",
            "severity": "medium",
            "failure_point": "Current branch is HEAD (detached); commits will be lost",
            "steps": [
                {"step_number": 1, "tool": "git", "input": "git checkout v1.0", "output": "HEAD is now at abc1234... Release v1.0", "error": None, "state": None},
                {"step_number": 2, "tool": "git", "input": "git commit -m 'fix critical bug'", "output": "1 file changed", "error": None, "state": None},
                {"step_number": 3, "tool": "git", "input": "git push origin main", "output": None, "error": "Everything up-to-date (missing commits not on a branch)", "state": None},
            ],
            "tags": ["git", "detached-head", "branching"],
            "expected_rule": "when in detached HEAD state, create a branch before committing to avoid losing changes",
        },
        {
            "trajectory_id": "cat-003-docker-compose-down",
            "task": "Rebuild and restart Docker containers",
            "domain": "docker",
            "failure_class": "docker/compose",
            "quality_label": "clear",
            "severity": "high",
            "failure_point": "Port 8000 already in use: container failed to start",
            "steps": [
                {"step_number": 1, "tool": "docker", "input": "docker compose up -d", "output": None, "error": "Error: starting container 'web' port 8000: address already in use", "state": None},
                {"step_number": 2, "tool": "docker", "input": "docker ps", "output": "CONTAINER ID web 0.0.0.0:8000->8000", "error": None, "state": None},
            ],
            "tags": ["docker", "compose", "port-conflict"],
            "expected_rule": "when docker compose fails with port conflict, stop the old container or change the port mapping",
        },
        {
            "trajectory_id": "cat-004-dockerfile-syntax",
            "task": "Build a Docker image for the project",
            "domain": "docker",
            "failure_class": "docker/build",
            "quality_label": "clear",
            "severity": "high",
            "failure_point": "COPY failed: file not found in build context",
            "steps": [
                {"step_number": 1, "tool": "docker", "input": "docker build -t myapp .", "output": None, "error": "COPY failed: file 'requirements.txt' not found in build context", "state": None},
                {"step_number": 2, "tool": "ls", "input": "ls -la", "output": "src/ Dockerfile README.md", "error": None, "state": None},
            ],
            "tags": ["docker", "build", "missing-file"],
            "expected_rule": "when docker build fails with COPY file not found, check the file path is relative to the build context",
        },
        {
            "trajectory_id": "cat-005-python-venv",
            "task": "Install dependencies and run tests",
            "domain": "python",
            "failure_class": "python/venv",
            "quality_label": "clear",
            "severity": "medium",
            "failure_point": "ModuleNotFoundError: No module named 'pytest'",
            "steps": [
                {"step_number": 1, "tool": "python", "input": "pip install -r requirements.txt", "output": "Installing collected packages... Successfully installed...", "error": None, "state": None},
                {"step_number": 2, "tool": "python", "input": "pytest tests/", "output": None, "error": "ModuleNotFoundError: No module named 'pytest'", "state": None},
                {"step_number": 3, "tool": "python", "input": "which python", "output": "/usr/bin/python3", "error": None, "state": None},
                {"step_number": 4, "tool": "python", "input": "which pip", "output": "/usr/local/bin/pip (not in venv)", "error": None, "state": None},
            ],
            "tags": ["python", "venv", "module", "pytest"],
            "expected_rule": "when python ModuleNotFoundError occurs after install, check there is an active virtualenv",
        },
        {
            "trajectory_id": "cat-006-pip-ssl",
            "task": "Install package from private PyPI registry",
            "domain": "python",
            "failure_class": "python/pip",
            "quality_label": "clear",
            "severity": "high",
            "failure_point": "SSL: CERTIFICATE_VERIFY_FAILED",
            "steps": [
                {"step_number": 1, "tool": "python", "input": "pip install my-private-pkg --index-url https://private.pypi.org/simple", "output": None, "error": "CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate", "state": None},
            ],
            "tags": ["python", "pip", "ssl", "certificate"],
            "expected_rule": "when pip install fails with SSL certificate error and target is a private registry, use --trusted-host or add the CA certificate",
        },
        {
            "trajectory_id": "cat-007-deploy-rollback",
            "task": "Rollback a failed deployment",
            "domain": "deploy",
            "failure_class": "deploy/rollback",
            "quality_label": "clear",
            "severity": "high",
            "failure_point": "kubectl rollout undo failed: no rollback revision found",
            "steps": [
                {"step_number": 1, "tool": "kubectl", "input": "kubectl apply -f deploy.yaml", "output": "deployment.apps/myapp created", "error": None, "state": None},
                {"step_number": 2, "tool": "kubectl", "input": "kubectl rollout status deployment/myapp", "output": None, "error": "CrashLoopBackOff: container myapp is crashing", "state": None},
                {"step_number": 3, "tool": "kubectl", "input": "kubectl rollout undo deployment/myapp", "output": None, "error": "error: no rollback revision found for deployment 'myapp'", "state": None},
            ],
            "tags": ["deploy", "kubectl", "rollback", "kubernetes"],
            "expected_rule": "when kubectl rollout undo fails with no revision found, delete and re-create the deployment instead",
        },
        {
            "trajectory_id": "cat-008-env-missing",
            "task": "Run application locally for testing",
            "domain": "env",
            "failure_class": "env/missing",
            "quality_label": "clear",
            "severity": "medium",
            "failure_point": "KeyError: 'DATABASE_URL' environment variable not set",
            "steps": [
                {"step_number": 1, "tool": "python", "input": "python src/app.py", "output": None, "error": "KeyError: 'DATABASE_URL' not set. Ensure all required env vars are configured.", "state": None},
                {"step_number": 2, "tool": "bash", "input": "echo $DATABASE_URL", "output": "(empty)", "error": None, "state": None},
            ],
            "tags": ["env", "configuration", "missing-variable"],
            "expected_rule": "when a Python application fails with KeyError for an environment variable, check the .env file or export the variable",
        },
        {
            "trajectory_id": "cat-009-shell-permission",
            "task": "Execute a deployment script",
            "domain": "shell",
            "failure_class": "shell/permission",
            "quality_label": "clear",
            "severity": "medium",
            "failure_point": "Permission denied: ./deploy.sh",
            "steps": [
                {"step_number": 1, "tool": "bash", "input": "./deploy.sh", "output": None, "error": "bash: ./deploy.sh: Permission denied", "state": None},
                {"step_number": 2, "tool": "bash", "input": "ls -la deploy.sh", "output": "-rw-r--r-- 1 user user 1234 deploy.sh (not executable)", "error": None, "state": None},
            ],
            "tags": ["shell", "permission", "executable"],
            "expected_rule": "when a shell script fails with Permission denied, run chmod +x to make it executable",
        },
        {
            "trajectory_id": "cat-010-workflow-wrong-file",
            "task": "Edit the CI configuration file",
            "domain": "workflow",
            "failure_class": "workflow/wrong-target",
            "quality_label": "clear",
            "severity": "medium",
            "failure_point": "Edited the wrong file: edited README.md instead of ci.yaml",
            "steps": [
                {"step_number": 1, "tool": "editor", "input": "Open README.md and add CI docs", "output": "README.md saved", "error": None, "state": None},
                {"step_number": 2, "tool": "git", "input": "git diff --staged", "output": "diff --git a/README.md b/README.md (wrong file!)", "error": "User intended to edit .github/workflows/ci.yaml", "state": None},
            ],
            "tags": ["workflow", "editing", "targeting"],
            "expected_rule": "when editing a specific configuration file, confirm the file path is correct before making changes",
        },
    ]

    for scenario in scenarios:
        scenario["source"] = "manual"
        scenario["source_repo"] = "CauterRule"
        scenario["redacted"] = False
        scenario["human_correction"] = None
        scenario["notes"] = ""
        if "success" not in scenario:
            scenario["success"] = False
        if "timestamp" not in scenario:
            from datetime import datetime as dt, timezone as tz
            scenario["timestamp"] = dt.now(tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        dst_path = dst_dir / f"{scenario['trajectory_id']}.jsonl"
        with open(dst_path, "w") as fh:
            fh.write(json.dumps(scenario) + "\n")
        count += 1

    return count


def validate_all() -> int:
    """Validate all trajectories in the corpus."""
    errors = 0
    total = 0
    for f in sorted(CORPUS_DIR.rglob("*.jsonl")):
        if ".git" in str(f):
            continue
        total += 1
        try:
            traj = json.loads(f.read_text().strip())
            tid = traj.get("trajectory_id", str(f))
            if traj.get("domain") not in VALID_DOMAINS:
                print(f"  ⚠️  {tid}: invalid domain '{traj.get('domain')}'")
                errors += 1
            if traj.get("quality_label") not in VALID_LABELS:
                print(f"  ⚠️  {tid}: invalid quality_label '{traj.get('quality_label')}'")
                errors += 1
            if not traj.get("steps"):
                print(f"  ⚠️  {tid}: no steps")
                errors += 1
            if not traj.get("task"):
                print(f"  ⚠️  {tid}: no task")
                errors += 1
            if "source" not in traj:
                print(f"  ⚠️  {tid}: no source")
                errors += 1
        except Exception as e:
            print(f"  ❌ {f}: {e}")
            errors += 1
    return errors


def show_status() -> None:
    """Show corpus collection status."""
    print("\n=== Corpus Status ===\n")
    total_raw = 0
    for source in sorted(VALID_SOURCES):
        src_dir = CORPUS_DIR / "raw" / source
        if not src_dir.exists():
            continue
        count = len(list(src_dir.glob("*.jsonl")))
        if count > 0:
            print(f"  raw/{source}/: {count} trajectories")
            total_raw += count

    for category in ["failures", "successes", "nearmiss", "noisy"]:
        cat_dir = CORPUS_DIR / "curated" / category
        if cat_dir.exists():
            count = len(list(cat_dir.rglob("*.jsonl")))
            if count > 0:
                print(f"  curated/{category}/: {count} trajectories")

    golden_count = len(list(GOLDEN_DIR.glob("*.jsonl")))
    print(f"  golden/: {golden_count} trajectories")
    print(f"\n  Total raw: {total_raw}")


def _guess_domain(traj: dict) -> str:
    """Guess domain from trajectory content."""
    task = traj.get("task", "").lower()
    for kw, domain in [("git", "git"), ("docker", "docker"), ("pip", "python"),
                        ("python", "python"), ("test", "test"), ("deploy", "deploy"),
                        ("shell", "shell"), ("kubectl", "deploy"), ("ci", "ci")]:
        if kw in task:
            return domain
    return "generic"


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed and validate field-test corpus")
    parser.add_argument("--status", action="store_true", help="Show corpus stats")
    parser.add_argument("--validate", action="store_true", help="Validate all trajectories")
    args = parser.parse_args()

    if args.status:
        show_status()
        return 0
    if args.validate:
        errors = validate_all()
        if errors:
            print(f"\n❌ {errors} validation errors found")
            return 1
        print("\n✅ All trajectories valid")
        return 0

    # Seed
    print("=== Seeding Corpus ===\n")

    f_count = seed_from_fixtures()
    print(f"  Test fixtures: {f_count} trajectories")

    g_count = seed_from_golden()
    print(f"  Golden set: {g_count} trajectories")

    c_count = create_failure_mode_catalog()
    print(f"  Failure mode catalog: {c_count} trajectories")

    total = f_count + g_count + c_count
    print(f"\n✅ Seeded {total} trajectories")

    # Validate
    errors = validate_all()
    if errors:
        print(f"\n⚠️  {errors} validation errors")
    else:
        print("\n✅ All trajectories valid")

    return 0


if __name__ == "__main__":
    sys.exit(main())