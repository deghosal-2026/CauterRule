from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

TARGET_DIR = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = TARGET_DIR / "field-test" / "v0.1.0" / "performance-baselines.json"
ITERATIONS = 3
THRESHOLD_MS = 500

COMMANDS: dict[str, list[str]] = {
    "cauterule list": ["cauterule", "list"],
    "cauterule health": ["cauterule", "health"],
    "cauterule validate": ["cauterule", "validate"],
    "cauterule inject --task 'git push'": ["cauterule", "inject", "git push"],
}


def measure(label: str, cmd: list[str]) -> dict:
    times: list[float] = []
    for i in range(ITERATIONS):
        start = time.perf_counter()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=TARGET_DIR,
        )
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        status = "OK" if result.returncode == 0 else "FAIL"
        print(f"  [{i+1}/{ITERATIONS}] {label}: {elapsed:.1f}ms  {status}")

    avg = sum(times) / len(times)
    min_t = min(times)
    max_t = max(times)
    passed = max_t < THRESHOLD_MS
    return {
        "command": label,
        "iterations": ITERATIONS,
        "min_ms": round(min_t, 1),
        "avg_ms": round(avg, 1),
        "max_ms": round(max_t, 1),
        "passed": passed,
        "threshold_ms": THRESHOLD_MS,
    }


def main() -> int:
    print(f"Performance baselines — {ITERATIONS} iterations, threshold {THRESHOLD_MS}ms\n")

    results: list[dict] = []
    for label, cmd in COMMANDS.items():
        print(f"> {label}")
        results.append(measure(label, cmd))
        print()

    summary = {
        "tool": "cauterule",
        "version": "0.1.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "iterations": ITERATIONS,
        "threshold_ms": THRESHOLD_MS,
        "results": results,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Saved to {OUTPUT}")

    print()
    all_passed = all(r["passed"] for r in results)
    if all_passed:
        print("All baselines PASSED")
        return 0
    else:
        failed = [r["command"] for r in results if not r["passed"]]
        print(f"FAILED: {', '.join(failed)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())