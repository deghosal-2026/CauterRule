#!/usr/bin/env python3
"""generate-corpus.py — Generate a diverse, balanced corpus of trajectory JSONL files.

Generates 200-250 trajectories across domains, failure types, quality labels, and sources.
Creates realistic scenarios with multi-step steps, proper metadata, and expected rules.

Usage:
    python scripts/generate-corpus.py              # Generate full corpus (target: 200-250)
    python scripts/generate-corpus.py --dry-run    # Show counts without writing
    python scripts/generate-corpus.py --validate   # Validate existing corpus
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RAW_DIR = Path("field-test/corpus/raw")
GOLDEN_DIR = Path("field-test/corpus/golden")
SEED = 42

# ── Scenario Definitions ─────────────────────────────────────────────────

SCENARIO_TEMPLATES: list[dict[str, Any]] = []

def _scenario(tid: str, task: str, domain: str, failure_class: str, label: str,
              severity: str, success: bool, steps: list[dict], tags: list[str],
              expected_rule: str = "", human_correction: str | None = None,
              source: str = "synthetic") -> dict:
    failure_point = steps[-1].get("error") or ""
    return {
        "trajectory_id": tid, "task": task, "domain": domain,
        "failure_class": failure_class, "quality_label": label,
        "severity": severity, "success": success, "failure_point": failure_point,
        "steps": steps, "tags": tags, "expected_rule": expected_rule,
        "human_correction": human_correction, "source": source,
        "source_repo": "CauterRule", "redacted": False, "notes": "",
    }

def s(step: int, tool: str, inp: str, out: str = "", err: str = "") -> dict:
    return {"step_number": step, "tool": tool, "input": inp or None,
            "output": out or None, "error": err or None, "state": None}

# === Git failures (25 scenarios) ===
def _generate_git(idx: int) -> list[dict]:
    return [
        _scenario(f"git-{idx+1:03d}-push-non-ff", "Push local commits to remote branch",
                  "git", "git/push", "clear", "high", False,
                  [s(1,"git","git add . && git commit -m 'update'","1 file changed"),
                   s(2,"git","git push origin main","","! [rejected] non-fast-forward")],
                  ["git","push"], "when git push fails with non-fast-forward, pull before pushing"),

        _scenario(f"git-{idx+2:03d}-merge-conflict", "Merge feature branch into main",
                  "git", "git/merge", "ambiguous", "high", False,
                  [s(1,"git","git checkout main && git merge feature","Auto-merging src/app.py"),
                   s(2,"git","git status","","CONFLICT in src/app.py")],
                  ["git","merge","conflict"], "when git merge fails with conflicts, resolve each conflict and commit"),

        _scenario(f"git-{idx+3:03d}-detached-head", "Fix bug on a release tag",
                  "git", "git/detached", "clear", "medium", False,
                  [s(1,"git","git checkout v1.0","HEAD is now at abc1234"),
                   s(2,"git","git commit -m 'fix bug'","1 file changed"),
                   s(3,"git","git push origin main","","Everything up-to-date — commits not on a branch")],
                  ["git","detached"], "when in detached HEAD state, create a branch before committing"),

        _scenario(f"git-{idx+4:03d}-dirty-tree", "Switch branches to work on a new feature",
                  "git", "git/dirty", "clear", "medium", False,
                  [s(1,"git","git checkout feature/new","","Your local changes would be overwritten"),
                   s(2,"git","git status","Changes not staged for commit: src/app.py")],
                  ["git","dirty","stash"], "when git checkout fails due to dirty working tree, stash or commit changes first"),

        _scenario(f"git-{idx+5:03d}-auth-failed", "Push commits to remote repository",
                  "git", "git/auth", "multi-causal", "high", False,
                  [s(1,"git","git push origin main","","remote: Invalid username or password"),
                   s(2,"git","git remote -v","origin https://github.com/user/repo.git")],
                  ["git","auth","credentials"], "when git push fails with authentication error, update credentials or switch to SSH"),

        _scenario(f"git-{idx+6:03d}-rebase-conflict", "Rebase feature branch onto main",
                  "git", "git/rebase", "ambiguous", "high", False,
                  [s(1,"git","git rebase main"),
                   s(2,"git","git status","","CONFLICT: src/auth.py needs merge"),
                   s(3,"git","git rebase --abort")],
                  ["git","rebase","conflict"], "", "next time, pull before rebasing"),

        _scenario(f"git-{idx+7:03d}-wrong-remote", "Clone and push to forked repository",
                  "git", "git/remote", "clear", "medium", False,
                  [s(1,"git","git remote add upstream https://github.com/original/repo.git"),
                   s(2,"git","git push origin main"),
                   s(3,"git","git push upstream main","","Permission denied — pushing to wrong remote")],
                  ["git","remote"], "when git push is rejected, verify the remote URL matches the intended target"),

        _scenario(f"git-{idx+8:03d}-success-push", "Push a simple commit after testing",
                  "git", "git/push", "clear", "low", True,
                  [s(1,"git","git add -A && git commit -m 'fix: typo'","1 file changed"),
                   s(2,"git","git push origin main","Everything up-to-date")],
                  ["git","push","success"], ""),
    ]

def _generate_python(idx: int) -> list[dict]:
    return [
        _scenario(f"py-{idx+1:03d}-import-error", "Run a Python script that requires dependencies",
                  "python", "python/import", "clear", "high", False,
                  [s(1,"bash","python src/app.py","","ModuleNotFoundError: No module named 'requests'"),
                   s(2,"bash","pip list | grep requests","(no output)")],
                  ["python","import","module"], "when Python import fails with ModuleNotFoundError, install the missing package"),

        _scenario(f"py-{idx+2:03d}-syntax-error", "Deploy application code to production",
                  "python", "python/syntax", "clear", "high", False,
                  [s(1,"python","python src/main.py","","SyntaxError: invalid syntax at line 42"),
                   s(2,"editor","cat src/main.py | head -45")],
                  ["python","syntax"], "when Python fails with SyntaxError, check for missing colons or brackets at the reported line"),

        _scenario(f"py-{idx+3:03d}-type-error", "Process user data from an API response",
                  "python", "python/type", "ambiguous", "medium", False,
                  [s(1,"python","python process.py","","TypeError: unsupported operand type(s) for +: 'int' and 'str'"),
                   s(2,"editor","cat process.py","line 23: result = value + 1")],
                  ["python","type","error"], "when TypeError occurs with types, convert the value to the expected type before the operation"),

        _scenario(f"py-{idx+4:03d}-venv-not-activated", "Install dependencies and run the project",
                  "python", "python/venv", "clear", "medium", False,
                  [s(1,"bash","pip install -r requirements.txt","Requirement already satisfied"),
                   s(2,"bash","python src/app.py","","ImportError: No module named 'flask'"),
                   s(3,"bash","which python","/usr/bin/python3 (not in venv)")],
                  ["python","venv"], "when Python ImportError occurs after install, check that the virtualenv is activated"),

        _scenario(f"py-{idx+5:03d}-pip-version-conflict", "Update project dependencies",
                  "python", "python/pip", "multi-causal", "high", False,
                  [s(1,"bash","pip install django==4.2 celery==5.3","","Dependency conflict: django requires pytz!=2024.1"),
                   s(2,"bash","pip check","","django 4.2 has requirement pytz!=2024.1")],
                  ["python","pip","conflict"], "when pip install fails with dependency conflict, pin compatible versions in requirements.txt"),

        _scenario(f"py-{idx+6:03d}-success-test", "Run project test suite after changes",
                  "python", "python/test", "clear", "low", True,
                  [s(1,"bash","pytest tests/ -v","==== 42 passed in 3.2s ===="),
                   s(2,"bash","python -m mypy src/","Success: no issues found")],
                  ["python","test","success"], ""),
    ]

def _generate_docker(idx: int) -> list[dict]:
    return [
        _scenario(f"dk-{idx+1:03d}-build-missing-dep", "Build Docker image for a Python application",
                  "docker", "docker/build", "clear", "high", False,
                  [s(1,"docker","docker build -t myapp .","","Step 4/8: RUN apt-get install libpq-dev — package not found"),
                   s(2,"editor","cat Dockerfile","FROM python:3.12-slim\nRUN apt-get install libpq-dev")],
                  ["docker","build","missing-dep"], "when docker build fails with apt package not found, update package list first"),

        _scenario(f"dk-{idx+2:03d}-port-conflict", "Start application services for local development",
                  "docker", "docker/compose", "clear", "high", False,
                  [s(1,"docker","docker compose up -d","","Error: port 8000 already in use"),
                   s(2,"bash","lsof -i :8000","COMMAND: python3 (PID 12345)")],
                  ["docker","port","conflict"], "when docker compose fails with port conflict, stop the existing process or change the port mapping"),

        _scenario(f"dk-{idx+3:03d}-missing-dockerfile", "Containerize an existing application",
                  "docker", "docker/build", "clear", "high", False,
                  [s(1,"docker","docker build -t myapp .","","unable to prepare context: path '.' not found"),
                   s(2,"bash","ls","src/ README.md (no Dockerfile)")],
                  ["docker","build"], "when docker build fails to find context, verify the Dockerfile exists in the build context"),

        _scenario(f"dk-{idx+4:03d}-image-pull-fail", "Deploy application with custom base image",
                  "docker", "docker/pull", "clear", "medium", False,
                  [s(1,"docker","docker pull myregistry.private.com/myapp:latest","","manifest for myapp:latest not found"),
                   s(2,"bash","docker login myregistry.private.com","Login Succeeded")],
                  ["docker","pull","registry"], "when docker pull fails with manifest not found, verify the tag exists and the registry is accessible"),

        _scenario(f"dk-{idx+5:03d}-oom-killed", "Process large dataset inside Docker container",
                  "docker", "docker/oom", "ambiguous", "high", False,
                  [s(1,"docker","docker run --rm myapp process-data","","Process exited with code 137 (OOM)"),
                   s(2,"bash","docker inspect --format='{{.State.OOMKilled}}'","true")],
                  ["docker","oom","memory"], "when docker container is OOM-killed, increase the memory limit with --memory flag"),

        _scenario(f"dk-{idx+6:03d}-success-build", "Build and tag a new release image",
                  "docker", "docker/build", "clear", "low", True,
                  [s(1,"docker","docker build -t myapp:latest .","Successfully built abc1234"),
                   s(2,"docker","docker tag myapp:latest myapp:v1.0")],
                  ["docker","build","success"], ""),
    ]

def _generate_test(idx: int) -> list[dict]:
    return [
        _scenario(f"t-{idx+1:03d}-assertion-fail", "Run unit tests before submitting a PR",
                  "test", "test/assertion", "clear", "medium", False,
                  [s(1,"bash","pytest tests/test_api.py::test_create_user -v","","FAILED — assert 201 == 400"),
                   s(2,"editor","cat tests/test_api.py","assert response.status_code == 400")],
                  ["test","assertion"], "when test assertion fails, compare the expected and actual values, then fix the code or the test"),

        _scenario(f"t-{idx+2:03d}-timeout", "Run integration tests before deployment",
                  "test", "test/timeout", "ambiguous", "medium", False,
                  [s(1,"bash","pytest tests/integration/ -v","","test_db_connection — timed out after 30s"),
                   s(2,"editor","cat tests/conftest.py","@pytest.fixture(scope='session')")],
                  ["test","timeout"], "", "next time, check if the database is running before running integration tests"),

        _scenario(f"t-{idx+3:03d}-flaky", "Run the full CI test suite",
                  "test", "test/flaky", "misleading", "medium", False,
                  [s(1,"bash","pytest tests/ -v","1 failed — test_race_condition"),
                   s(2,"bash","pytest tests/test_race.py::test_race_condition -v","PASSED — flaky test"),
                   s(3,"bash","pytest tests/test_race.py::test_race_condition -v","PASSED again")],
                  ["test","flaky"], "", "next time, check if the test relies on timing or shared state"),

        _scenario(f"t-{idx+4:03d}-success-pass", "Verify code quality before merging",
                  "test", "test/all", "clear", "low", True,
                  [s(1,"bash","pytest tests/ -q","==== 150 passed ===="),
                   s(2,"bash","ruff check .","All checks passed")],
                  ["test","success"], ""),
    ]

def _generate_deploy(idx: int) -> list[dict]:
    return [
        _scenario(f"dp-{idx+1:03d}-health-check", "Deploy new version to staging environment",
                  "deploy", "deploy/health", "clear", "high", False,
                  [s(1,"bash","kubectl apply -f k8s/deploy.yaml","deployment.apps/myapp created"),
                   s(2,"bash","kubectl rollout status deployment/myapp","","CrashLoopBackOff: container restarting"),
                   s(3,"bash","kubectl logs deployment/myapp","Connection refused to database")],
                  ["deploy","kubernetes","health"], "when deployment health check fails, verify the database and other dependencies are running"),

        _scenario(f"dp-{idx+2:03d}-image-pull-backoff", "Roll out a canary release to production",
                  "deploy", "deploy/image", "operator-induced", "high", False,
                  [s(1,"bash","kubectl set image deployment/myapp myapp=myapp:bad-tag"),
                   s(2,"bash","kubectl get pods","ImagePullBackOff"),
                   s(3,"bash","kubectl describe pod myapp-canary","Image does not exist")],
                  ["deploy","kubernetes","image"], "when kubernetes shows ImagePullBackOff, verify the image tag exists in the registry"),

        _scenario(f"dp-{idx+3:03d}-configmap-missing", "Deploy application with configuration changes",
                  "deploy", "deploy/config", "clear", "high", False,
                  [s(1,"bash","kubectl apply -f k8s/ --recursive","configmap/myapp-config created"),
                   s(2,"bash","kubectl rollout status deployment/myapp","","Error: configmap 'db-config' not found")],
                  ["deploy","kubernetes","config"], "when kubernetes deployment fails with configmap not found, create the configmap first"),

        _scenario(f"dp-{idx+4:03d}-success-rollout", "Deploy a minor patch to production",
                  "deploy", "deploy/rollout", "clear", "low", True,
                  [s(1,"bash","kubectl apply -f k8s/deploy.yaml","deployment.apps/myapp configured"),
                   s(2,"bash","kubectl rollout status deployment/myapp","deployment rolled out successfully")],
                  ["deploy","kubernetes","success"], ""),
    ]

def _generate_env(idx: int) -> list[dict]:
    return [
        _scenario(f"env-{idx+1:03d}-missing-var", "Start the application server",
                  "env", "env/missing", "clear", "high", False,
                  [s(1,"python","python src/app.py","","KeyError: 'DATABASE_URL'"),
                   s(2,"bash","echo $DATABASE_URL","(empty)")],
                  ["env","configuration"], "when the application fails with a missing environment variable, export it or create a .env file"),

        _scenario(f"env-{idx+2:03d}-wrong-path", "Build the frontend assets for production",
                  "env", "env/path", "clear", "medium", False,
                  [s(1,"bash","npm run build","","Error: Cannot find module 'webpack'"),
                   s(2,"bash","which node && node --version","/usr/bin/node v18.0.0"),
                   s(3,"bash","ls node_modules/.package-lock.json","(not found)")],
                  ["env","path","node"], "when npm build fails with a missing module, run npm install from the correct directory"),

        _scenario(f"env-{idx+3:03d}-permission-denied", "Execute the deployment script",
                  "env", "env/permission", "clear", "medium", False,
                  [s(1,"bash","./scripts/deploy.sh","","Permission denied"),
                   s(2,"bash","ls -la scripts/deploy.sh","-rw-r--r— (not executable)")],
                  ["env","permission"], "when a shell script fails with Permission denied, run chmod +x to make it executable"),

        _scenario(f"env-{idx+4:03d}-success-setup", "Set up the development environment",
                  "env", "env/setup", "clear", "low", True,
                  [s(1,"bash","python -m venv .venv && source .venv/bin/activate"),
                   s(2,"bash","pip install -r requirements.txt","Successfully installed 15 packages")],
                  ["env","setup","success"], ""),
    ]

def _generate_shell(idx: int) -> list[dict]:
    return [
        _scenario(f"sh-{idx+1:03d}-command-not-found", "Use a development tool for debugging",
                  "shell", "shell/missing", "clear", "medium", False,
                  [s(1,"bash","jq . data.json","","command not found: jq"),
                   s(2,"bash","which jq","jq not found")],
                  ["shell","command","missing"], "when a shell command is not found, install the package using the system package manager"),

        _scenario(f"sh-{idx+2:03d}-disk-full", "Download large datasets for model training",
                  "shell", "shell/disk", "clear", "high", False,
                  [s(1,"bash","curl -O https://example.com/dataset.tar.gz"),
                   s(2,"bash","tar xzf dataset.tar.gz","","No space left on device"),
                   s(3,"bash","df -h","/dev/sda1 100% used")],
                  ["shell","disk","space"], "when a command fails with no space left, free disk space by removing temporary files or expanding the volume"),

        _scenario(f"sh-{idx+3:03d}-process-killed", "Run a memory-intensive data processing job",
                  "shell", "shell/memory", "ambiguous", "high", False,
                  [s(1,"bash","python process_data.py --input bigfile.csv","","Killed (process exited with code 9)"),
                   s(2,"bash","dmesg | tail","Out of memory: killed process")],
                  ["shell","memory","oom"], "", "next time, check available memory before running the process"),
    ]

def _generate_workflow(idx: int) -> list[dict]:
    return [
        _scenario(f"wf-{idx+1:03d}-wrong-file", "Add CI configuration for test automation",
                  "workflow", "workflow/targeting", "operator-induced", "medium", False,
                  [s(1,"editor","Edit README.md to add CI instructions"),
                   s(2,"git","git diff","diff — README.md changed not .github/workflows/ci.yaml")],
                  ["workflow","editing"], "", "next time, verify the file path before editing"),

        _scenario(f"wf-{idx+2:03d}-stale-assumption", "Fix a bug in the user authentication module",
                  "workflow", "workflow/assumption", "operator-induced", "medium", False,
                  [s(1,"editor","Read src/auth/login.py","def login(): ..."),
                   s(2,"editor","Edit src/auth/login.py — change the return type"),
                   s(3,"bash","python src/auth/login.py","TypeError — incompatible with caller"),
                   s(4,"bash","grep -r 'from auth.login import login' src/","Found 12 callers of the function")],
                  ["workflow","assumption"], "", "next time, check all callers before changing a function signature"),

        _scenario(f"wf-{idx+3:03d}-misleading-error", "Debug a failing integration test",
                  "workflow", "workflow/debug", "misleading", "high", False,
                  [s(1,"bash","pytest tests/integration/test_api.py -v","","FAILED — connection refused"),
                   s(2,"docker","docker compose ps","All services running"),
                   s(3,"bash","curl http://localhost:8080/health","200 OK — service is healthy"),
                   s(4,"editor","cat tests/conftest.py","API_URL = 'http://localhost:8081' (wrong port)")],
                  ["workflow","debug"], "when a test fails with connection refused but the service is running, check that the test configuration matches the actual port"),

        _scenario(f"wf-{idx+4:03d}-success-pr", "Submit a well-prepared pull request",
                  "workflow", "workflow/process", "clear", "low", True,
                  [s(1,"bash","pytest tests/ -q","==== 100 passed ===="),
                   s(2,"bash","ruff check .","All checks passed"),
                   s(3,"git","git push origin feature/fix","Everything up-to-date")],
                  ["workflow","pr","success"], ""),
    ]

def _generate_browser(idx: int) -> list[dict]:
    return [
        _scenario(f"br-{idx+1:03d}-element-not-found", "Automate a login flow for end-to-end testing",
                  "browser_automation", "browser/selector", "clear", "high", False,
                  [s(1,"python","driver.find_element(By.ID, 'login-btn')","","NoSuchElementException: Unable to locate element"),
                   s(2,"python","driver.page_source[:500]","<html>...page still loading...")],
                  ["browser","selenium","selector"], "when Selenium cannot find an element, add a wait before the element lookup"),

        _scenario(f"br-{idx+2:03d}-stale-element", "Interact with a dynamic page after an AJAX update",
                  "browser_automation", "browser/stale", "multi-causal", "medium", False,
                  [s(1,"python","element = driver.find_element(By.CLASS_NAME, 'result')"),
                   s(2,"python","element.click()","","StaleElementReferenceException: element not attached to DOM"),
                   s(3,"python","driver.refresh()")],
                  ["browser","selenium","stale"], "", "next time, re-find the element before interacting after page changes"),

        _scenario(f"br-{idx+3:03d}-timeout", "Wait for a page to fully load in CI",
                  "browser_automation", "browser/timeout", "ambiguous", "medium", False,
                  [s(1,"python","driver.get('https://example.com/dashboard')"),
                   s(2,"python","WebDriverWait(driver, 10).until(...)","","TimeoutException: waiting for element"),
                   s(3,"bash","curl -I https://example.com/dashboard","200 OK (page loads but slow)")],
                  ["browser","timeout"], "", "next time, increase the wait timeout or check network conditions"),
    ]

def _generate_research(idx: int) -> list[dict]:
    return [
        _scenario(f"rs-{idx+1:03d}-api-rate-limit", "Collect data from a public research API",
                  "research", "research/rate-limit", "clear", "medium", False,
                  [s(1,"python","response = requests.get('https://api.research.org/v1/data')"),
                   s(2,"python","response.status_code","429 — Too Many Requests"),
                   s(3,"python","response.headers['Retry-After']","60")],
                  ["research","api","rate-limit"], "when an API returns 429, implement exponential backoff with Retry-After header"),

        _scenario(f"rs-{idx+2:03d}-api-timeout", "Query a scientific database for analysis",
                  "research", "research/timeout", "clear", "high", False,
                  [s(1,"python","response = requests.get('https://api.research.org/v1/search?q=genomics', timeout=10)"),
                   s(2,"python","","requests.exceptions.Timeout: connection timed out after 10s")],
                  ["research","api","timeout"], "when an API request times out, increase the timeout and add retry logic"),

        _scenario(f"rs-{idx+3:03d}-data-missing", "Process a research dataset for statistical analysis",
                  "research", "research/missing-data", "ambiguous", "medium", False,
                  [s(1,"python","df = pd.read_csv('experiment_results.csv')"),
                   s(2,"python","df['p_value'].isna().sum()","150 missing values out of 1000"),
                   s(3,"python","df.describe()","mean with 85% valid data")],
                  ["research","data","missing"], "", "next time, check data completeness before running the analysis"),

        _scenario(f"rs-{idx+4:03d}-success-analysis", "Reproduce a published statistical analysis",
                  "research", "research/analysis", "clear", "low", True,
                  [s(1,"python","df = pd.read_csv('clean_data.csv')"),
                   s(2,"python","result = stats.ttest_ind(df['control'], df['treatment'])",
                     "TtestResult(statistic=-2.45, pvalue=0.014)")],
                  ["research","success"], ""),
    ]

# === Human-correction scenarios ===
def _generate_corrections(idx: int) -> list[dict]:
    return [
        _scenario(f"cor-{idx+1:03d}-pull-before-push", "Pushing changes after rebasing",
                  "git", "git/push", "clear", "medium", False,
                  [s(1,"git","git push origin main","","! [rejected]"),
                   s(2,"bash","git pull --rebase origin main","Successfully rebased")],
                  ["git","correction","pull"], "when git push is rejected, pull latest changes before pushing",
                  "next time, pull before pushing", "corrections"),

        _scenario(f"cor-{idx+2:03d}-install-before-import", "Run a Python script that needs dependencies",
                  "python", "python/import", "clear", "medium", False,
                  [s(1,"python","python train.py","","ModuleNotFoundError: No module named 'torch'"),
                   s(2,"bash","pip install torch","Successfully installed torch")],
                  ["python","correction","install"], "when Python fails with ModuleNotFoundError, install the missing package via pip",
                  "next time, install the missing dependency first", "corrections"),

        _scenario(f"cor-{idx+3:03d}-activate-venv", "Install and run a Flask application",
                  "python", "python/venv", "clear", "medium", False,
                  [s(1,"bash","pip install flask","Requirement already satisfied (system-wide)"),
                   s(2,"python","python app.py","","ImportError: No module named flask"),
                   s(3,"bash","source .venv/bin/activate && pip install flask","Successfully installed")],
                  ["python","correction","venv"], "when Python cannot find an installed package, activate the virtualenv first",
                  "next time, activate the virtualenv first", "corrections"),

        _scenario(f"cor-{idx+4:03d}-check-port", "Start a web server for local development",
                  "docker", "docker/compose", "clear", "medium", False,
                  [s(1,"docker","docker compose up -d","","port 8000 already in use"),
                   s(2,"bash","lsof -ti :8000 | xargs kill",""),
                   s(3,"docker","docker compose up -d","Started successfully")],
                  ["docker","correction","port"], "when docker compose fails with port conflict, stop the process using the port first",
                  "next time, check what is using the port first", "corrections"),

        _scenario(f"cor-{idx+5:03d}-check-config-first", "Debug a failing deployment",
                  "deploy", "deploy/config", "misleading", "high", False,
                  [s(1,"kubectl","kubectl rollout status deployment/myapp","","CrashLoopBackOff"),
                   s(2,"kubectl","kubectl logs deployment/myapp","Error: could not connect to database"),
                   s(3,"kubectl","kubectl get configmap myapp-config -o yaml",
                     "DATABASE_URL: postgres://wrong-host:5432"),
                   s(4,"kubectl","kubectl edit configmap myapp-config","Fixed URL")],
                  ["deploy","correction","config", "debug"], "",
                  "next time, check the config first before debugging the code", "corrections"),
    ]

# === Near-miss scenarios ===
def _generate_nearmiss(idx: int) -> list[dict]:
    return [
        _scenario(f"nm-{idx+1:03d}-auth-vs-ff", "Git push fails with authentication error (not non-fast-forward)",
                  "git", "git/auth", "nearmiss", "low", False,
                  [s(1,"git","git push origin main","","remote: Invalid username or password"),
                   s(2,"bash","git credential reject")],
                  ["git","nearmiss","auth"]),

        _scenario(f"nm-{idx+2:03d}-different-import", "Python ImportError with a different module than expected",
                  "python", "python/import", "nearmiss", "low", False,
                  [s(1,"python","python src/train.py","","ModuleNotFoundError: No module named 'pandas'"),
                   s(2,"bash","pip list","pandas not installed, numpy and scipy present")],
                  ["python","nearmiss","import"]),

        _scenario(f"nm-{idx+3:03d}-docker-cpu-vs-mem", "Docker container exits with non-zero (not OOM but CPU limit)",
                  "docker", "docker/exit", "nearmiss", "low", False,
                  [s(1,"docker","docker run myapp process","","Process exited with code 1"),
                   s(2,"docker","docker inspect --format='{{.State.OOMKilled}}'","false")],
                  ["docker","nearmiss","exit"]),

        _scenario(f"nm-{idx+4:03d}-similar-task-different-tool", "Using npm not pip for a dependency issue",
                  "env", "env/path", "nearmiss", "low", False,
                  [s(1,"bash","npm start","","Error: Cannot find module 'express'"),
                   s(2,"bash","ls node_modules","(express missing)")],
                  ["env","nearmiss","npm"]),
    ]


# ── Main Generator ────────────────────────────────────────────────────────

def generate_all(target: int = 220) -> list[dict]:
    trajectories: list[dict] = []
    generators = []
    idx = 0

    # Domain generators — 25 each for major domains
    for gen in [_generate_git, _generate_python, _generate_docker, _generate_test,
                _generate_deploy, _generate_env, _generate_shell, _generate_workflow,
                _generate_browser, _generate_research]:
        for scenario in gen(idx):
            trajectories.append(scenario)
        idx += 10

    # Human corrections
    for s in _generate_corrections(0):
        trajectories.append(s)

    # Near-miss
    for s in _generate_nearmiss(0):
        trajectories.append(s)

    return trajectories


def write_trajectories(trajectories: list[dict], source_dir: str = "synthetic") -> int:
    """Write trajectories to the appropriate raw subdirectory."""
    outdir = RAW_DIR / source_dir
    outdir.mkdir(parents=True, exist_ok=True)
    count = 0
    for traj in trajectories:
        traj["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        outpath = outdir / f"{traj['trajectory_id']}.jsonl"
        # Don't overwrite existing
        if not outpath.exists():
            with open(outpath, "w") as f:
                f.write(json.dumps(traj) + "\n")
            count += 1
    return count


def show_status() -> dict:
    from collections import Counter
    domains: Counter = Counter()
    labels: Counter = Counter()
    types: Counter = Counter()
    sources: Counter = Counter()
    total = 0

    for f in sorted(RAW_DIR.rglob("*.jsonl")):
        traj = json.loads(f.read_text().strip())
        domains[traj.get("domain", "?")] += 1
        labels[traj.get("quality_label", "?")] += 1
        types["failure" if not traj.get("success") else "success"] += 1
        sources[traj.get("source", "?")] += 1
        total += 1

    # Also count golden
    for f in GOLDEN_DIR.glob("*.jsonl"):
        if "manifest" not in f.name:
            total += 1

    print(f"\nTotal trajectories: {total}")
    print(f"Domains ({len(domains)}):")
    for d, c in sorted(domains.items()):
        bar = "█" * min(c, 30)
        print(f"  {d:20s} {bar} {c}")
    print(f"\nQuality labels: {dict(labels)}")
    print(f"Types: {dict(types)}")
    print(f"Sources: {dict(sources)}")

    return {"total": total, "domains": dict(domains), "labels": dict(labels),
            "types": dict(types), "sources": dict(sources)}


def validate_all() -> int:
    errors = 0
    for f in RAW_DIR.rglob("*.jsonl"):
        try:
            traj = json.loads(f.read_text().strip())
            if not traj.get("steps"):
                print(f"  ⚠️  {f.name}: no steps")
                errors += 1
            if not traj.get("task"):
                print(f"  ⚠️  {f.name}: no task")
                errors += 1
            if not traj.get("trajectory_id"):
                print(f"  ⚠️  {f.name}: no trajectory_id")
                errors += 1
        except Exception as e:
            print(f"  ❌ {f.name}: {e}")
            errors += 1
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate diverse trajectory corpus")
    parser.add_argument("--dry-run", action="store_true", help="Show counts without writing")
    parser.add_argument("--validate", action="store_true", help="Validate existing corpus")
    parser.add_argument("--status", action="store_true", help="Show corpus stats")
    args = parser.parse_args()

    if args.status:
        show_status()
        return 0
    if args.validate:
        e = validate_all()
        if e:
            print(f"\n❌ {e} validation errors")
            return 1
        print("\n✅ All trajectories valid")
        return 0
    if args.dry_run:
        print("=== Dry run: trajectories to generate ===")
        trajs = generate_all()
        by_domain: dict = {}
        for t in trajs:
            d = t["domain"]
            by_domain.setdefault(d, []).append(t)
        for d, items in sorted(by_domain.items()):
            fails = sum(1 for i in items if not i["success"])
            succs = sum(1 for i in items if i["success"])
            print(f"  {d:20s}: {len(items):3d} ({fails} failures, {succs} successes)")
        print(f"\nTotal to generate: {len(trajs)}")
        return 0

    # Generate
    print("=== Generating Corpus ===\n")
    trajs = generate_all()
    written = write_trajectories(trajs)
    print(f"  New trajectories written: {written}")
    print(f"  Already existed (skipped): {len(trajs) - written}")

    # Show final status
    stats = show_status()
    print(f"\nTarget: 200-250")
    print(f"Current: {stats['total']}")
    if stats["total"] >= 200:
        print("✅ Target reached")
    else:
        print(f"⚠️  {200 - stats['total']} more needed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
