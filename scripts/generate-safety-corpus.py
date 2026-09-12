"""
Generate expanded safety corpora for v0.2.0 field test.

Usage:
    python scripts/generate-safety-corpus.py

What it does:
    1. Fixes existing 20 success trajectories (remove failure_class, set should_silence)
    2. Generates 30 new clean success trajectories → 50 total
    3. Generates 40 new failures/negative → 50 total
    4. Generates 36 new nearmiss trajectories → 50 total
    5. Backfills expected_outcome via normalize

Requires: pip install cauterule (or be in the repo root with `pip install -e .`)
"""
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

SUCCESSES_DIR = Path("field-test/corpus/curated/successes")
NEGATIVE_DIR = Path("field-test/corpus/curated/failures/negative")
NEARMISS_DIR = Path("field-test/corpus/curated/nearmiss")

TS = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def _write_jsonl(path: Path, traj: dict) -> None:
    path.write_text(json.dumps(traj, separators=(",", ":")) + "\n")


# ── 1. Fix existing success trajectories ──────────────────────────────

def fix_existing_successes() -> int:
    """Strip failure_class/failure_point from existing success files so gate drops them."""
    fixed = 0
    for f in sorted(SUCCESSES_DIR.glob("*.jsonl")):
        data = json.loads(f.read_text().strip())
        changed = False
        if data.get("failure_class"):
            data["failure_class"] = None
            changed = True
        if data.get("failure_point"):
            data["failure_point"] = None
            changed = True
        if data.get("expected_outcome") != "should_silence":
            data["expected_outcome"] = "should_silence"
            data["expected_outcome_rationale"] = "Clean success — no failure pattern to extract"
            changed = True
        for step in data.get("steps", []):
            if step.get("error"):
                step["error"] = None
                changed = True
        if changed:
            _write_jsonl(f, data)
            fixed += 1
    return fixed


# ── 2. Generate new clean success trajectories ────────────────────────

SUCCESS_SCENARIOS = [
    # (id_suffix, task, domain, tool, steps)
    ("git-clone", "Clone a git repository", "git", "git",
     [("git clone https://github.com/user/repo.git", "Cloning into 'repo'... done.")]),
    ("git-pull", "Pull latest changes from remote", "git", "git",
     [("git pull origin main", "Already up to date.")]),
    ("git-status", "Check git repository status", "git", "git",
     [("git status", "nothing to commit, working tree clean")]),
    ("git-log", "View recent git commit history", "git", "git",
     [("git log --oneline -5", "a1b2c3d fix: handle edge case\ne2f3g4h feat: add new endpoint")]),
    ("git-branch", "List git branches", "git", "git",
     [("git branch -a", "* main\n  feature/login\n  remotes/origin/main")]),
    ("python-version", "Check Python version", "python", "bash",
     [("python3 --version", "Python 3.12.4")]),
    ("pip-list", "List installed Python packages", "python", "bash",
     [("pip list --format=columns", "Package    Version\npip        24.0\nsetuptools 68.0")]),
    ("python-syntax", "Check Python file syntax", "python", "bash",
     [("python3 -m py_compile src/main.py", "")]),
    ("pytest-pass", "Run Python tests that pass", "python", "bash",
     [("pytest tests/ -v", "42 passed in 3.2s")]),
    ("flake8-clean", "Run flake8 linting", "python", "bash",
     [("flake8 src/", "")]),
    ("docker-ps", "List running Docker containers", "docker", "bash",
     [("docker ps", "CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES")]),
    ("docker-images", "List Docker images", "docker", "bash",
     [("docker images", "REPOSITORY   TAG       IMAGE ID       CREATED       SIZE\nnginx       latest    abc123def456   2 weeks ago   187MB")]),
    ("docker-pull", "Pull a Docker image", "docker", "bash",
     [("docker pull alpine:latest", "latest: Pulling from library/alpine\nDigest: sha256:abc...\nStatus: Downloaded newer image")]),
    ("docker-rm", "Remove a Docker container", "docker", "bash",
     [("docker rm old-container", "old-container")]),
    ("docker-network-ls", "List Docker networks", "docker", "bash",
     [("docker network ls", "NETWORK ID   NAME      DRIVER   SCOPE\nabc   bridge    bridge   local\ndef   host      host     local")]),
    ("ci-lint", "CI linting stage passes", "ci", "bash",
     [("make lint", "All lint checks passed")]),
    ("ci-build", "CI build stage completes", "ci", "bash",
     [("make build", "Build successful")]),
    ("ci-test", "CI test stage passes", "ci", "bash",
     [("make test", "All tests passed")]),
    ("ci-deploy", "CI deploy stage succeeds", "ci", "bash",
     [("make deploy", "Deployment complete")]),
    ("ci-cache", "CI cache restore succeeds", "ci", "bash",
     [("make restore-cache", "Cache restored from main")]),
    ("shell-ls", "List directory contents", "shell", "bash",
     [("ls -la", "total 42\ndrwxr-xr-x  10 user  staff   320 Sep  7 12:00 .\n-rw-r--r--   1 user  staff  1024 Sep  7 12:00 main.py")]),
    ("shell-cat", "Display file contents", "shell", "bash",
     [("cat README.md", "# Project\n\nThis is a sample project.")]),
    ("shell-mkdir", "Create a directory", "shell", "bash",
     [("mkdir -p /tmp/new-project/src", "")]),
    ("shell-cp", "Copy files", "shell", "bash",
     [("cp -r src/ /tmp/backup/", "")]),
    ("shell-echo", "Print environment info", "shell", "bash",
     [("echo 'Build started at $(date)'", "Build started at Mon Sep 7 12:00:00 UTC 2026")]),
    ("browser-navigate", "Navigate to a web page", "browser_automation", "search",
     [("driver.get('https://example.com')", "page loaded successfully")]),
    ("browser-title", "Get page title", "browser_automation", "search",
     [("driver.title", "Example Domain")]),
    ("browser-screenshot", "Take a screenshot", "browser_automation", "search",
     [("driver.save_screenshot('page.png')", "True")]),
    ("browser-cookies", "Get browser cookies", "browser_automation", "search",
     [("driver.get_cookies()", "[{'name': 'session', 'value': 'abc123'}]")]),
    ("browser-quit", "Close browser session", "browser_automation", "search",
     [("driver.quit()", "")]),
    ("research-api", "Fetch data from public API", "research", "web_fetch",
     [("requests.get('https://api.publicapis.org/entries')", "{\"count\": 1425, \"entries\": [...]}")]),
    ("research-search", "Search web for information", "research", "web_fetch",
     [("search('python async programming')", "Found 10 results")]),
    ("research-download", "Download research paper", "research", "web_fetch",
     [("wget https://arxiv.org/pdf/2301.00001.pdf", "2026-09-07 12:00:00 URL:... Saved [123456]")]),
    ("research-parse", "Parse HTML content", "research", "web_fetch",
     [("BeautifulSoup(html, 'html.parser')", "Parsed 42 elements")]),
    ("research-validate", "Validate data schema", "research", "web_fetch",
     [("jsonschema.validate(data, schema)", "Validation passed")]),
    ("support-ping", "Ping a server", "support", "bash",
     [("ping -c 1 8.8.8.8", "1 packets transmitted, 1 received, 0% packet loss")]),
    ("support-dns", "DNS resolution", "support", "bash",
     [("nslookup example.com", "Server: 8.8.8.8\nAddress: 93.184.216.34")],
    ),
    ("support-curl", "Check HTTP endpoint", "support", "bash",
     [("curl -s -o /dev/null -w '%{http_code}' https://example.com", "200")]),
    ("support-df", "Check disk space", "support", "bash",
     [("df -h /", "Filesystem   Size   Used  Avail Capacity\n/dev/disk1  465Gi  200Gi  265Gi    43%")]),
    ("support-free", "Check memory usage", "support", "bash",
     [("free -h", "Mem:  16Gi  8Gi  8Gi")]),
]


def generate_new_successes(start_id: int = 21) -> int:
    """Generate clean success trajectories. Returns count."""
    count = 0
    for i, (suffix, task, domain, tool, raw_steps) in enumerate(SUCCESS_SCENARIOS):
        sid = start_id + i
        tid = f"S-{sid:03d}-{suffix}"
        steps = [
            {
                "step_number": si + 1,
                "tool": tool,
                "input": cmd,
                "output": out,
                "error": None,
                "state": None,
            }
            for si, (cmd, out) in enumerate(raw_steps)
        ]
        traj = {
            "trajectory_id": tid,
            "id": tid,
            "timestamp": TS,
            "task": task,
            "steps": steps,
            "success": True,
            "failure_point": None,
            "failure_class": None,
            "domain": domain,
            "quality_label": "clear",
            "severity": None,
            "tags": [domain, "success", "synthetic"],
            "expected_rule": "",
            "human_correction": None,
            "source": "synthetic",
            "source_repo": "CauterRule",
            "redacted": False,
            "notes": "",
            "environment": {"os": "unknown", "ci": False},
            "agent_config": {"model": "unknown", "tools": []},
            "expected_outcome": "should_silence",
            "expected_outcome_rationale": "Clean success — no failure pattern to extract",
        }
        p = SUCCESSES_DIR / f"{tid}.jsonl"
        _write_jsonl(p, traj)
        count += 1
    return count


# ── 3. Generate failures/negative trajectories ────────────────────────

NEGATIVE_SCENARIOS = [
    # (suffix, task, domain, raw_steps, tags)
    ("user-opinion", "User expresses opinion about code style", "coding",
     [("bash", "echo 'I prefer tabs over spaces'", "tabs are better for alignment")],
     ["opinion", "style", "discussion"]),
    ("cosmetic-warning", "Compiler warning about unused variable", "coding",
     [("bash", "gcc -c main.c", "main.c:12: warning: unused variable 'x'")],
     ["cosmetic", "warning", "compiler"]),
    ("normal-log", "Normal application log output", "devops",
     [("bash", "journalctl -u myapp --since '1 hour ago'", "INFO: Server started on port 8080\nINFO: Health check OK")],
     ["log", "info", "normal"]),
    ("env-info", "Print environment variables", "support",
     [("bash", "echo $PATH", "/usr/local/bin:/usr/bin:/bin")],
     ["env", "info", "diagnostic"]),
    ("feature-request", "User requests a new feature", "support",
     [("bash", "echo 'Can we add dark mode?'", "Feature request logged")],
     ["feature-request", "discussion"]),
    ("config-correct", "Configuration file is correct", "devops",
     [("bash", "cat config.yaml", "port: 8080\nhost: 0.0.0.0\ndebug: false")],
     ["config", "correct", "normal"]),
    ("help-command", "User runs --help", "support",
     [("bash", "cauterule --help", "Usage: cauterule [OPTIONS] COMMAND")],
     ["help", "info", "normal"]),
    ("version-check", "Check installed version", "support",
     [("bash", "cauterule --version", "cauterule 0.2.0")],
     ["version", "info", "normal"]),
    ("dry-run", "Dry run a command", "devops",
     [("bash", "terraform plan", "No changes. Infrastructure is up to date.")],
     ["dry-run", "plan", "noop"]),
    ("syntax-check", "Syntax check passes", "coding",
     [("bash", "python3 -m py_compile script.py", "")],
     ["syntax", "check", "pass"]),
    ("test-pass", "Tests pass on first run", "python",
     [("bash", "pytest tests/ -v", "42 passed in 3.2s")],
     ["test", "pass", "success"]),
    ("build-pass", "Build succeeds", "devops",
     [("bash", "make build", "Build successful")],
     ["build", "pass", "success"]),
    ("deploy-dry", "Deployment dry-run succeeds", "devops",
     [("bash", "make deploy-dry-run", "Dry run: would deploy 3 services")],
     ["deploy", "dry-run", "success"]),
    ("cache-hit", "Cache hit during build", "devops",
     [("bash", "make build", "CACHE: Using cached layer for pip install")],
     ["cache", "build", "success"]),
    ("auth-success", "Authentication succeeds", "devops",
     [("bash", "aws sts get-caller-identity", "{\"UserId\": \"AIDA...\", \"Account\": \"123456\"}")],
     ["auth", "success", "iam"]),
    ("permission-check", "Permission check passes", "devops",
     [("bash", "kubectl auth can-i create deployments", "yes")],
     ["permission", "rbac", "success"]),
    ("health-check", "Health check passes", "devops",
     [("bash", "curl -f http://localhost:8080/health", "OK")],
     ["health", "monitoring", "success"]),
    ("backup-ok", "Backup completes successfully", "devops",
     [("bash", "pg_dump mydb > backup.sql", "")],
     ["backup", "database", "success"]),
    ("migration-check", "Check database migration status", "devops",
     [("bash", "alembic current", "heads: abc123 (head)")],
     ["migration", "database", "success"]),
    ("npm-audit", "npm audit finds no vulnerabilities", "javascript",
     [("bash", "npm audit", "found 0 vulnerabilities")],
     ["npm", "audit", "secure"]),
    ("dependency-check", "Dependency check passes", "python",
     [("bash", "pip-audit", "No known vulnerabilities found")],
     ["dependency", "audit", "secure"]),
    ("secret-scan", "Secret scan finds nothing", "devops",
     [("bash", "trufflehog filesystem .", "No secrets found")],
     ["secret", "scan", "secure"]),
    ("format-check", "Code formatting check passes", "coding",
     [("bash", "black --check src/", "All files already formatted")],
     ["format", "lint", "pass"]),
    ("type-check", "Type checking passes", "python",
     [("bash", "mypy src/", "Success: no issues found")],
     ["type", "check", "pass"]),
    ("import-check", "Import check passes", "python",
     [("bash", "python3 -c 'import requests'", "")],
     ["import", "check", "pass"]),
    ("network-ok", "Network connectivity check", "support",
     [("bash", "curl -s -o /dev/null -w '%{http_code}' https://api.github.com", "200")],
     ["network", "connectivity", "success"]),
    ("ssl-ok", "SSL certificate check passes", "support",
     [("bash", "openssl s_client -connect example.com:443 -servername example.com < /dev/null 2>/dev/null", "CONNECTED(00000003)")],
     ["ssl", "certificate", "success"]),
    ("dns-ok", "DNS resolution check", "support",
     [("bash", "dig +short example.com", "93.184.216.34")],
     ["dns", "resolution", "success"]),
    ("latency-ok", "Latency check passes", "support",
     [("bash", "ping -c 3 8.8.8.8", "rtt min/avg/max/mdev = 10.2/12.5/15.1/2.0 ms")],
     ["latency", "network", "success"]),
    ("disk-ok", "Disk space check passes", "support",
     [("bash", "df -h / | tail -1", "/dev/sda1  100G   50G   50G  50% /")],
     ["disk", "storage", "success"]),
    # Shell negatives
    ("shell-echo-version", "Echo shell version info", "shell",
     [("bash", "echo $SHELL", "/bin/zsh")],
     ["shell", "version", "info"]),
    ("shell-which", "Check which tool is installed", "shell",
     [("bash", "which python3", "/usr/local/bin/python3")],
     ["shell", "which", "tool"]),
    ("shell-env-ls", "List environment variables", "shell",
     [("bash", "env | head -5", "HOME=/Users/user\nSHELL=/bin/zsh\nPATH=/usr/local/bin:/usr/bin")],
     ["shell", "env", "diagnostic"]),
    ("shell-date", "Print current date", "shell",
     [("bash", "date", "Mon Sep 7 12:00:00 UTC 2026")],
     ["shell", "date", "info"]),
    ("shell-pwd", "Print working directory", "shell",
     [("bash", "pwd", "/Users/user/project")],
     ["shell", "pwd", "info"]),
    # Research negatives
    ("research-schema", "Validate JSON schema", "research",
     [("web_fetch", "jsonschema.validate(data, schema)", "Validation passed")],
     ["research", "schema", "validation"]),
    ("research-parse-xml", "Parse an XML file", "research",
     [("web_fetch", "xml.etree.ElementTree.parse('data.xml')", "<Element 'root' at 0x...>")],
     ["research", "xml", "parse"]),
    ("research-csv", "Read CSV data", "research",
     [("bash", "python3 -c \"import csv; open('data.csv')\"", "")],
     ["research", "csv", "data"]),
    ("research-text", "Process text file", "research",
     [("bash", "wc -l report.txt", "150 report.txt")],
     ["research", "text", "processing"]),
    ("research-log", "Read and summarize a log file", "research",
     [("bash", "tail -10 application.log", "INFO: Application started\nINFO: Processing request\nINFO: Request complete")],
     ["research", "log", "analysis"]),
    # More docker negatives
    ("docker-pull-public", "Pull public Docker image", "docker",
     [("bash", "docker pull nginx:latest", "latest: Pulling from library/nginx\nDigest: sha256:abc...\nStatus: Image is up to date")],
     ["docker", "pull", "success"]),
    ("docker-run", "Run a Docker container", "docker",
     [("bash", "docker run -d --name web nginx:alpine", "abc123def456")],
     ["docker", "run", "success"]),
    ("docker-build-cached", "Docker build with cache hit", "docker",
     [("bash", "docker build -t myapp .", "=> CACHED [build 1/3]")],
     ["docker", "build", "cached"]),
    ("docker-compose-up", "Docker Compose starts services", "docker",
     [("bash", "docker compose up -d", "Container web  Started\nContainer db   Started")],
     ["docker", "compose", "success"]),
    ("docker-exec", "Execute command in container", "docker",
     [("bash", "docker exec web ls /app", "main.py\nconfig.yaml")],
     ["docker", "exec", "success"]),
    # More browser negatives
    ("browser-page-load", "Browser loads a page successfully", "browser_automation",
     [("search", "driver.get('https://example.com')", "Page loaded: 200 OK")],
     ["browser", "page", "load"]),
    ("browser-find-element", "Browser finds an element", "browser_automation",
     [("search", "driver.find_element(By.ID, 'main')", "<Element 'div' id='main'>")],
     ["browser", "element", "found"]),
    ("browser-click", "Browser clicks an element", "browser_automation",
     [("search", "element.click()", "")],
     ["browser", "click", "success"]),
    ("browser-type", "Browser types into input field", "browser_automation",
     [("search", "input.send_keys('hello')", "")],
     ["browser", "input", "success"]),
    ("browser-wait", "Browser waits for element", "browser_automation",
     [("search", "WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'done')))", "<Element 'div' id='done'>")],
     ["browser", "wait", "success"]),
]


def generate_new_negatives(start_id: int = 51) -> int:
    """Generate failures/negative trajectories. Returns count."""
    count = 0
    for i, (suffix, task, domain, raw_steps, tags) in enumerate(NEGATIVE_SCENARIOS):
        sid = start_id + i
        tid = f"N-{sid:03d}-{suffix}"
        steps = [
            {
                "step_number": si + 1,
                "tool": tool,
                "input": cmd,
                "output": out,
                "error": None,
                "state": None,
            }
            for si, (tool, cmd, out) in enumerate(raw_steps)
        ]
        traj = {
            "trajectory_id": tid,
            "id": tid,
            "timestamp": TS,
            "task": task,
            "steps": steps,
            "success": True,
            "failure_point": None,
            "failure_class": None,
            "domain": domain,
            "quality_label": "clear",
            "severity": None,
            "tags": tags,
            "expected_rule": "",
            "human_correction": None,
            "source": "synthetic",
            "source_repo": "CauterRule",
            "redacted": False,
            "notes": "",
            "environment": {"os": "unknown", "ci": False},
            "agent_config": {"model": "unknown", "tools": []},
            "expected_outcome": "should_silence",
            "expected_outcome_rationale": "Clean success — no failure pattern to extract",
        }
        p = NEGATIVE_DIR / f"{tid}.jsonl"
        _write_jsonl(p, traj)
        count += 1
    return count


# ── 4. Generate nearmiss trajectories ─────────────────────────────────

NEARMISS_SCENARIOS = [
    # (suffix, task, domain, raw_steps, failure_class, tags)
    ("git-push-retry", "Git push fails, retry succeeds", "git",
     [("bash", "git push origin feature", "! [rejected] non-fast-forward"),
      ("bash", "git pull --rebase && git push", "Everything up-to-date")],
     "git/push/temporary", ["git", "push", "retry", "nearmiss"]),
    ("docker-build-retry", "Docker build fails, retry succeeds", "docker",
     [("bash", "docker build -t myapp .", "ERROR: failed to solve: timeout"),
      ("bash", "docker build --network=host -t myapp .", "Successfully built abc123")],
     "docker/build/timeout", ["docker", "build", "retry", "nearmiss"]),
    ("pip-install-retry", "pip install fails, retry works", "python",
     [("bash", "pip install requests", "ERROR: Could not install packages due to OSError: [Errno 28] No space left on device"),
      ("bash", "pip install requests --no-cache-dir", "Successfully installed requests")],
     "python/pip/disk-full", ["python", "pip", "retry", "nearmiss"]),
    ("test-retry", "Test fails, rerun passes", "python",
     [("bash", "pytest tests/test_flaky.py", "FAILED tests/test_flaky.py::test_something - AssertionError"),
      ("bash", "pytest tests/test_flaky.py --flaky-reruns=1", "PASSED (1 rerun)")],
     "test/flaky/retry", ["test", "flaky", "retry", "nearmiss"]),
    ("npm-install-retry", "npm install fails, retry succeeds", "javascript",
     [("bash", "npm install", "npm ERR! network timeout"),
      ("bash", "npm install --prefer-offline", "added 42 packages")],
     "npm/install/network", ["npm", "install", "retry", "nearmiss"]),
    ("kubectl-apply-retry", "kubectl apply fails, retry succeeds", "devops",
     [("bash", "kubectl apply -f deploy.yaml", "error: unable to recognize: no matches for kind"),
      ("bash", "kubectl apply --server-side -f deploy.yaml", "deployment.apps/myapp created")],
     "k8s/apply/temporary", ["kubectl", "apply", "retry", "nearmiss"]),
    ("terraform-plan-retry", "terraform plan fails, retry succeeds", "devops",
     [("bash", "terraform plan", "Error: Error acquiring state lock"),
      ("bash", "terraform plan -lock-timeout=30s", "No changes. Infrastructure is up to date.")],
     "terraform/state/lock", ["terraform", "lock", "retry", "nearmiss"]),
    ("api-timeout-retry", "API call times out, retry succeeds", "research",
     [("web_fetch", "GET https://api.example.com/data", "504 Gateway Timeout"),
      ("web_fetch", "GET https://api.example.com/data (retry after 1s)", "{\"data\": [1, 2, 3]}")],
     "api/timeout/transient", ["api", "timeout", "retry", "nearmiss"]),
    ("browser-stale-retry", "Browser stale element, re-find succeeds", "browser_automation",
     [("search", "element.click()", "StaleElementReferenceException"),
      ("search", "element = driver.find_element(By.ID, 'btn'); element.click()", "")],
     "browser/selenium/stale", ["browser", "selenium", "stale", "nearmiss"]),
    ("deploy-timeout-retry", "Deploy times out, retry succeeds", "devops",
     [("bash", "kubectl rollout status deployment/myapp", "error: deployment roll out timed out"),
      ("bash", "kubectl rollout restart deployment/myapp && kubectl rollout status deployment/myapp", "deployment \"myapp\" successfully rolled out")],
     "ci/deploy/timeout", ["deploy", "timeout", "retry", "nearmiss"]),
    ("git-merge-retry", "Git merge conflict, resolved and merged", "git",
     [("git", "git merge feature/login", "Auto-merging src/auth.py\nCONFLICT in src/auth.py"),
      ("git", "git add src/auth.py && git commit -m 'resolve merge conflict'", "[main abc123] resolve merge conflict")],
     "git/merge/conflict", ["git", "merge", "conflict", "nearmiss"]),
    ("docker-compose-retry", "Docker compose fails, retry succeeds", "docker",
     [("bash", "docker compose up -d", "Error: container port already allocated"),
      ("bash", "docker compose down && docker compose up -d", "Container web  Started\nContainer db   Started")],
     "docker/compose/port", ["docker", "compose", "port", "nearmiss"]),
    ("pip-conflict-retry", "pip dependency conflict, resolved with workaround", "python",
     [("bash", "pip install flask==2.0", "ERROR: pip's dependency resolver conflict"),
      ("bash", "pip install flask==2.0 --no-deps", "Successfully installed flask")],
     "python/pip/conflict", ["python", "pip", "conflict", "nearmiss"]),
    ("ssh-connect-retry", "SSH connection fails, retry succeeds", "devops",
     [("bash", "ssh user@server", "ssh: connect to host server port 22: Connection refused"),
      ("bash", "sleep 5 && ssh user@server", "Last login: Mon Sep 7 11:00:00")],
     "ssh/connect/refused", ["ssh", "connect", "retry", "nearmiss"]),
    ("database-connect-retry", "Database connection fails, retry succeeds", "devops",
     [("bash", "psql -h localhost -U user mydb", "psql: error: connection refused"),
      ("bash", "sleep 3 && psql -h localhost -U user mydb", "psql (16.0)\nType 'help' for help.")],
     "database/connect/refused", ["database", "connect", "retry", "nearmiss"]),
    ("certificate-retry", "SSL cert error, retry works", "research",
     [("web_fetch", "curl https://internal.example.com", "curl: (60) SSL certificate problem"),
      ("web_fetch", "curl -k https://internal.example.com", "{\"status\": \"ok\"}")],
     "ssl/certificate/verify", ["ssl", "certificate", "verify", "nearmiss"]),
    ("rate-limit-retry", "API rate limited, retry after wait", "research",
     [("web_fetch", "GET https://api.github.com/search/code", "403 rate limit exceeded"),
      ("web_fetch", "sleep 60 && GET https://api.github.com/search/code", "{\"items\": []}")],
     "api/rate-limit/exceeded", ["api", "rate-limit", "retry", "nearmiss"]),
    ("docker-pull-retry", "Docker pull fails, retry succeeds", "docker",
     [("bash", "docker pull myregistry.com/myapp:latest", "Error response from daemon: pull access denied"),
      ("bash", "docker login myregistry.com && docker pull myregistry.com/myapp:latest", "latest: Pulling from myapp\nDigest: sha256:def")],
     "docker/pull/auth", ["docker", "pull", "auth", "nearmiss"]),
    ("browser-navigate-retry", "Browser navigation times out, retry succeeds", "browser_automation",
     [("search", "driver.get('https://slow.example.com')", "TimeoutException: page load timed out"),
      ("search", "driver.set_page_load_timeout(60); driver.get('https://slow.example.com')", "Page loaded")],
     "browser/navigation/timeout", ["browser", "navigation", "timeout", "nearmiss"]),
    ("pytest-assertion-retry", "Test assertion fails, fix and retry", "python",
     [("bash", "pytest tests/", "FAILED test_example.py::test_compare - AssertionError: assert 42 == 100"),
      ("bash", "pytest tests/", "PASSED (1 passed)")],
     "python/test/assertion", ["test", "assertion", "retry", "nearmiss"]),
    ("ci-cache-miss", "CI cache miss, rebuild succeeds", "ci",
     [("bash", "make restore-cache", "CACHE: No cache found for key main-abc123"),
      ("bash", "make build", "Build successful (no cache)")],
     "ci/cache/miss", ["ci", "cache", "miss", "nearmiss"]),
    ("ci-timeout", "CI job times out, rerun works", "ci",
     [("bash", "make test", "TIMEOUT: job exceeded 30 minutes"),
      ("bash", "make test --timeout=60", "All tests passed (45 min)")],
     "ci/test/timeout", ["ci", "test", "timeout", "nearmiss"]),
    ("browser-alert", "Browser alert appears, handled", "browser_automation",
     [("search", "element.click()", "UnexpectedAlertPresentException: Alert text: Are you sure?"),
      ("search", "Alert(driver).accept(); element.click()", "")],
     "browser/alert/unexpected", ["browser", "alert", "nearmiss"]),
    ("docker-oom", "Container OOM, restarts with more memory", "docker",
     [("bash", "docker run -m 128m myapp", "Process exited with code 137 (OOM)"),
      ("bash", "docker run -m 512m myapp", "Service started successfully")],
     "docker/oom/kill", ["docker", "oom", "memory", "nearmiss"]),
    ("kubectl-rollback", "Deploy fails, rollback succeeds", "devops",
     [("bash", "kubectl apply -f deploy.yaml", "deployment.apps/myapp created"),
      ("bash", "kubectl rollout status deployment/myapp", "error: deployment roll out timed out"),
      ("bash", "kubectl rollout undo deployment/myapp", "deployment rolled back")],
     "k8s/deploy/rollback", ["kubectl", "deploy", "rollback", "nearmiss"]),
    ("terraform-apply-retry", "Terraform apply fails, retry succeeds", "devops",
     [("bash", "terraform apply -auto-approve", "Error: error creating resource: conflict"),
      ("bash", "terraform apply -auto-approve", "Apply complete! Resources: 1 added, 0 changed")],
     "terraform/apply/conflict", ["terraform", "apply", "conflict", "nearmiss"]),
    ("shell-command-retry", "Shell command fails, retry succeeds", "shell",
     [("bash", "rm -rf /tmp/lock", "rm: /tmp/lock: Permission denied"),
      ("bash", "sudo rm -rf /tmp/lock", "")],
     "shell/permission/denied", ["shell", "permission", "retry", "nearmiss"]),
    ("pip-install-version", "pip install wrong version, correct version works", "python",
     [("bash", "pip install flask==1.0", "ERROR: Could not find a version that satisfies"),
      ("bash", "pip install flask==2.3", "Successfully installed flask")],
     "python/pip/version", ["python", "pip", "version", "nearmiss"]),
    ("npm-build-fail", "npm build fails, retry works", "javascript",
     [("bash", "npm run build", "ERROR: Build failed with 2 errors"),
      ("bash", "npm cache clean --force && npm run build", "Build succeeded")],
     "npm/build/fail", ["npm", "build", "cache", "nearmiss"]),
    ("git-commit-hook", "Git commit hook fails, bypass works", "git",
     [("git", "git commit -m 'fix bug'", "pre-commit hook failed: lint error"),
      ("git", "git commit -m 'fix bug' --no-verify", "[main def456] fix bug, 1 file changed")],
     "git/commit/hook", ["git", "commit", "hook", "nearmiss"]),
    ("browser-frame", "Browser frame switch fails, retry works", "browser_automation",
     [("search", "driver.switch_to.frame('nonexistent')", "NoSuchFrameException"),
      ("search", "driver.switch_to.default_content(); driver.switch_to.frame('main-frame')", "")],
     "browser/frame/switch", ["browser", "frame", "switch", "nearmiss"]),
    ("docker-volume", "Docker volume mount fails, retry works", "docker",
     [("bash", "docker run -v /host/path:/container/path myapp", "docker: invalid mount config"),
      ("bash", "docker run -v /host/existing:/container/path myapp", "Container started")],
     "docker/volume/mount", ["docker", "volume", "mount", "nearmiss"]),
    ("api-500-retry", "API returns 500, retry succeeds", "research",
     [("web_fetch", "POST https://api.example.com/order", "500 Internal Server Error"),
      ("web_fetch", "POST https://api.example.com/order (retry)", "201 Created")],
     "api/server/error", ["api", "500", "retry", "nearmiss"]),
    ("dns-resolution-retry", "DNS resolution fails, retry succeeds", "support",
     [("bash", "nslookup myservice.local", "server can't find myservice.local: NXDOMAIN"),
      ("bash", "nslookup myservice.local.", "Address: 10.0.0.42")],
     "dns/resolution/nxdomain", ["dns", "resolution", "retry", "nearmiss"]),
    ("network-flaky", "Network flaky, retry succeeds", "support",
     [("bash", "curl -s https://api.example.com", "curl: (7) Failed to connect"),
      ("bash", "curl -s --retry 3 https://api.example.com", "{\"status\": \"ok\"}")],
     "network/flaky/connect", ["network", "flaky", "retry", "nearmiss"]),
    ("support-connection", "Connection to support portal fails, retry succeeds", "support",
     [("bash", "curl https://support.example.com/ticket", "curl: (28) Connection timed out"),
      ("bash", "curl https://support.example.com/ticket --connect-timeout 60", "{\"ticket\": 12345}")],
     "support/connection/timeout", ["support", "connection", "timeout", "nearmiss"]),
]


def generate_new_nearmiss(start_id: int = 15) -> int:
    """Generate nearmiss trajectories. Returns count."""
    count = 0
    for i, (suffix, task, domain, raw_steps, failure_class, tags) in enumerate(NEARMISS_SCENARIOS):
        sid = start_id + i
        tid = f"NM-{sid:03d}-{suffix}"
        steps = []
        for si, (tool, cmd, out) in enumerate(raw_steps):
            is_error = si == 0 and out and any(x in out for x in ["error", "ERROR", "Error", "failed", "FAILED", "TIMEOUT", "rejected", "CONFLICT", "refused", "denied", "OOM", "exception", "timeout", "NXDOMAIN", "500", "504", "403"])
            step = {
                "step_number": si + 1,
                "tool": tool,
                "input": cmd,
                "output": out if not is_error else None,
                "error": out if is_error else None,
                "state": None,
            }
            steps.append(step)
        traj = {
            "trajectory_id": tid,
            "id": tid,
            "timestamp": TS,
            "task": task,
            "steps": steps,
            "success": True,
            "failure_point": "step_1",
            "failure_class": failure_class,
            "domain": domain,
            "quality_label": "ambiguous",
            "severity": "low",
            "tags": tags,
            "expected_rule": "",
            "human_correction": None,
            "source": "synthetic",
            "source_repo": "CauterRule",
            "redacted": False,
            "notes": "",
            "environment": {"os": "unknown", "ci": False},
            "agent_config": {"model": "unknown", "tools": []},
            "expected_outcome": "should_reject",
            "expected_outcome_rationale": "Ambiguous — retry after first failure succeeded; no rule needed",
        }
        p = NEARMISS_DIR / f"{tid}.jsonl"
        _write_jsonl(p, traj)
        count += 1
    return count


# ── Main ──────────────────────────────────────────────────────────────

def main() -> int:
    SUCCESSES_DIR.mkdir(parents=True, exist_ok=True)
    NEGATIVE_DIR.mkdir(parents=True, exist_ok=True)
    NEARMISS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Fix existing successes
    n_fixed = fix_existing_successes()
    print(f"Fixed existing successes: {n_fixed}")

    # 2. Generate new successes
    n_new_success = generate_new_successes()
    n_total_success = len(list(SUCCESSES_DIR.glob("*.jsonl")))
    print(f"Generated new successes: {n_new_success} → total: {n_total_success}")

    # 3. Generate new negatives
    n_new_negative = generate_new_negatives()
    n_total_negative = len(list(NEGATIVE_DIR.glob("*.jsonl")))
    print(f"Generated new negatives: {n_new_negative} → total: {n_total_negative}")

    # 4. Generate new nearmiss
    n_new_nearmiss = generate_new_nearmiss()
    n_total_nearmiss = len(list(NEARMISS_DIR.glob("*.jsonl")))
    print(f"Generated new nearmiss: {n_new_nearmiss} → total: {n_total_nearmiss}")

    # 5. Run normalize to backfill expected_outcome
    import subprocess
    print("\nNormalizing...")
    for path in ["field-test/corpus/curated/successes", "field-test/corpus/curated/failures/negative", "field-test/corpus/curated/nearmiss"]:
        r = subprocess.run([sys.executable, "scripts/normalize-corpus.py", "--path", path], capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode != 0:
            print(f"  [error] {r.stderr.strip()}")

    # Verify
    from cauterule.corpus.validation import validate_corpus_sizes
    counts = {
        "successes": n_total_success,
        "failures/negative": n_total_negative,
        "nearmiss": n_total_nearmiss,
    }
    warnings = validate_corpus_sizes(counts)
    if warnings:
        print(f"\nWarnings: {warnings}")
    else:
        print(f"\nAll safety corpora meet minimum sizes: {counts}")

    return 0 if not warnings else 1


if __name__ == "__main__":
    sys.exit(main())
