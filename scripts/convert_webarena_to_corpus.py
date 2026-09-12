#!/usr/bin/env python3
"""Convert WebArena browser-tool failure reports to a reference corpus (#705).

``web-arena-x/webarena`` (MIT) and ``web-arena-x/visualwebarena`` contain
genuine browser-automation failures: stale-element references,
unexpected-alert / browser-alert, no-such-frame / switch-to-frame,
element-not-found (NoSuchElementException), and page-load / navigation
timeouts.  Each issue becomes a failure reference trajectory under
``corpus/public/browser/`` with a failure class derived from the error
text; a small set of successful-navigation counterparts is emitted for
#707 balance.

Usage:
    python scripts/convert_webarena_to_corpus.py \
        --issues /tmp/webarena.json \
        --output corpus/public/browser \
        --success-output corpus/public/successes \
        --limit 20

    # synthesize without fetching GH issues (uses built-in fixtures):
    python scripts/convert_webarena_to_corpus.py \
        --output corpus/public/browser \
        --success-output corpus/public/successes \
        --limit 20

Fetch samples with gh:
    gh api "search/issues?q=repo:web-arena-x/webarena+browser+type:issue&per_page=20" \
        --jq '[.items[] | {number,title,body}]' > /tmp/webarena.json
    gh api "repos/web-arena-x/webarena/issues?state=all&per_page=20" \
        --jq '[.[] | {number,title,body}]' > /tmp/webarena.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_TS = "2026-09-11T00:00:00+00:00"
_SOURCE_REPO = "web-arena-x/webarena"
_ERROR_RE = re.compile(
    r"error|failed|exception|timeout|timed out|stale|alert|frame|element|"
    r"unable to locate|no such|not found|not attached",
    re.IGNORECASE,
)

# Ordered most specific -> generic.  Every browser alias in matcher.py
# (lines 152-153, 172-173, 218-219) must map to browser/* (see also
# tests/replay/test_browser_alias_coverage.py).
_CLASSIFIERS: tuple[tuple[str, str], ...] = (
    ("staleelementreferenceexception", "browser/stale_element"),
    ("stale element", "browser/stale_element"),
    ("stale element reference", "browser/stale_element"),
    ("element is not attached", "browser/stale_element"),
    ("unexpectedalertopenexception", "browser/unexpected_alert"),
    ("unexpected alert", "browser/unexpected_alert"),
    ("unexpected alert open", "browser/unexpected_alert"),
    ("browser alert", "browser/unexpected_alert"),
    ("alert text", "browser/unexpected_alert"),
    ("alert not handled", "browser/unexpected_alert"),
    ("nosuchframeexception", "browser/no_such_frame"),
    ("no such frame", "browser/no_such_frame"),
    ("frame not found", "browser/no_such_frame"),
    ("switch to frame", "browser/no_such_frame"),
    ("unable to switch to frame", "browser/no_such_frame"),
    ("nosuchelementexception", "browser/element_not_found"),
    ("no such element", "browser/element_not_found"),
    ("element not found", "browser/element_not_found"),
    ("unable to locate element", "browser/element_not_found"),
    ("could not locate element", "browser/element_not_found"),
    ("page load timeout", "browser/timeout"),
    ("navigation timeout", "browser/timeout"),
    ("page load timed out", "browser/timeout"),
    ("timeoutexception", "browser/timeout"),
    ("context deadline exceeded", "browser/timeout"),
    ("timed out", "browser/timeout"),
    ("timeout", "browser/timeout"),
)


def classify(body: str) -> str:
    """Derive a browser failure_class from issue body text."""
    lowered = body.lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", lowered)
    for needle, failure_class in _CLASSIFIERS:
        needle_normalized = re.sub(r"[^a-z0-9]+", " ", needle.lower()).strip()
        if needle_normalized and needle_normalized in normalized:
            return failure_class
        if needle.lower() in lowered:
            return failure_class
    return "browser/issue"


def extract_error(body: str) -> str:
    """Extract the most error-like snippet from an issue body."""
    for block in re.findall(r"```(.*?)```", body, re.DOTALL):
        if _ERROR_RE.search(block):
            return str(block).strip()[:1000]
    for line in body.splitlines():
        if _ERROR_RE.search(line):
            return str(line).strip()[:1000]
    return str(body).strip()[:1000] or "browser error"


def _tool_for_body(_body: str) -> str:
    return "browser"


def _input_for_body(body: str) -> str:
    lowered = body.lower()
    if "stale" in lowered:
        return "click #add-to-cart"
    if "alert" in lowered:
        return "click #confirm"
    if "frame" in lowered:
        return "switch to frame checkout-iframe"
    if "element" in lowered or "locate" in lowered:
        return "click #checkout-btn"
    if "timeout" in lowered or "timed out" in lowered:
        return "navigate https://shop.example.com/search"
    return "browser navigate"


# ---------------------------------------------------------------------------
# Synthetic fixtures (20 realistic failures covering all 5 alias families).
# Used when --issues is absent or when GH fetch is not desired.
# ---------------------------------------------------------------------------
_SYNTHETIC_ISSUES: list[dict[str, Any]] = [
    {
        "number": 7001,
        "title": "StaleElementReference on add-to-cart after DOM update",
        "body": "Steps: click #add-to-cart after search results refresh\n"
        "Error:\n```\nStaleElementReferenceException: stale element reference: "
        "element is not attached to the page document (Session info: chrome=120)\n```",
    },
    {
        "number": 7002,
        "title": "stale element clicking checkout after navigation",
        "body": "```\nStaleElementReferenceException: stale element reference: "
        "element is not attached to the page document (checkout after navigation)\n```",
    },
    {
        "number": 7003,
        "title": "stale element in product list pagination",
        "body": "```\norg.openqa.selenium.StaleElementReferenceException: stale element reference\n"
        "at WebElement.click (product-list:42)\n```\nDOM invalidated after filter applied.",
    },
    {
        "number": 7004,
        "title": "stale element reference on cart quantity update",
        "body": "Action: click quantity input after cart reload\n"
        "Error: stale element reference: element is not attached to the page document",
    },
    # unexpected alert (4)
    {
        "number": 7005,
        "title": "unexpected alert blocks form submit",
        "body": "```\nUnexpectedAlertOpenException: unexpected alert open: "
        "{Alert text : Are you sure you want to leave?} browser alert not handled\n```",
    },
    {
        "number": 7006,
        "title": "browser alert during checkout confirmation",
        "body": "Clicking confirm triggers browser alert: UnexpectedAlertOpenException "
        "unexpected alert open {Alert text : Confirm order?} alert not handled",
    },
    {
        "number": 7007,
        "title": "alert not dismissed before next click",
        "body": "Selenium error: unexpected alert open: Alert text : Session expired. "
        "browser alert must be dismissed before proceeding",
    },
    {
        "number": 7008,
        "title": "unexpected alert on payment page navigation",
        "body": "```\nSelenium.UnexpectedAlertOpenException: unexpected alert open\n"
        "Alert text : Please confirm your payment method\n```",
    },
    # no such frame / switch to frame (4)
    {
        "number": 7009,
        "title": "NoSuchFrameException on checkout iframe",
        "body": "```\nNoSuchFrameException: no such frame: unable to switch to frame "
        "checkout-iframe (no frame with name checkout-iframe)\n```",
    },
    {
        "number": 7010,
        "title": "switch to frame fails for payment frame",
        "body": "WebDriverException: switch to frame failed: frame not found payment-frame. "
        "NoSuchFrameException: no such frame",
    },
    {
        "number": 7011,
        "title": "frame not found when switching to login iframe",
        "body": "Error switching context: no such frame: frame not found login-iframe "
        "switch to frame login-iframe failed",
    },
    {
        "number": 7012,
        "title": "unable to switch to frame on VisualWebArena task",
        "body": "VisualWebArena step 4: unable to switch to frame visual-content-frame\n"
        "NoSuchFrameException: no such frame",
    },
    # element not found (4)
    {
        "number": 7013,
        "title": "NoSuchElementException for checkout button",
        "body": "```\nNoSuchElementException: no such element: Unable to locate element: "
        "{\"method\":\"css selector\",\"selector\":\"#checkout-btn\"} element not found\n```",
    },
    {
        "number": 7014,
        "title": "element not found on search results page",
        "body": "Selenium error: NoSuchElementException: no such element: Unable to locate element "
        "{By.xpath: //button[@id='add-to-cart']} element not found",
    },
    {
        "number": 7015,
        "title": "could not locate element for login form",
        "body": "WebDriverWait timed out: could not locate element #username "
        "NoSuchElementException element not found",
    },
    {
        "number": 7016,
        "title": "unable to locate element hotel-booking date picker",
        "body": "VisualWebArena hotel task: unable to locate element "
        "[data-testid='date-picker'] NoSuchElementException",
    },
    # page-load / navigation timeouts (4)
    {
        "number": 7017,
        "title": "page load timeout on WebArena shopping search",
        "body": "```\nTimeoutException: timeout: page load timeout waiting for "
        "https://shop.example.com/search?q=shoes timed out after 30s\n```",
    },
    {
        "number": 7018,
        "title": "navigation timeout on VisualWebArena map task",
        "body": "TimeoutException: navigation timeout: page load timeout exceeded "
        "waiting for https://maps.example.com timed out",
    },
    {
        "number": 7019,
        "title": "page load timed out after 45s on product page",
        "body": "Selenium timeout: page load timed out after 45000ms "
        "TimeoutException: timeout waiting for document ready",
    },
    {
        "number": 7020,
        "title": "TimeoutException browsing WebArena reddit clone",
        "body": "```\norg.openqa.selenium.TimeoutException: timeout waiting for "
        "element visible: page load timeout\n```\nnavigation to /r/webarena failed",
    },
]


def _failure(issue: dict[str, Any], index: int, ts: str) -> dict[str, Any]:
    body = str(issue.get("body", ""))
    number = issue.get("number", index)
    tid = f"browser-issue-{number}"
    task = str(issue.get("title", "")).strip() or f"WebArena browser issue {number}"
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
        "domain": "web",
        "severity": "medium",
        "tags": ["reference", "browser", "webarena", "visualwebarena"],
        "expected_outcome": "should_extract",
        "expected_outcome_rationale": (
            "Real browser failure signature from WebArena/VisualWebArena."
        ),
        "expected_outcome_confidence": "medium",
        "source": "webarena-issues",
        "source_repo": _SOURCE_REPO,
    }


_SUCCESS_CASES = (
    "Navigate to WebArena shopping site and add item to cart",
    "Click checkout button and complete purchase on WebArena",
    "Switch to checkout iframe and fill payment form",
    "Search products and handle alert dialog on WebArena",
)


def _success(index: int, case: str, ts: str) -> dict[str, Any]:
    tid = f"browser-success-{index:03d}"
    lowered = case.lower()
    if "iframe" in lowered:
        inp = "switch to frame checkout-iframe"
        out = "switched to frame checkout-iframe successfully"
    elif "alert" in lowered:
        inp = "dismiss alert"
        out = "alert dismissed and page ready"
    elif "search" in lowered or "navigate" in lowered:
        inp = "navigate https://shop.example.com"
        out = "page loaded successfully (200 OK)"
    else:
        inp = "click #checkout-btn"
        out = "clicked element #checkout-btn successfully"
    return {
        "trajectory_id": tid,
        "id": tid,
        "timestamp": ts,
        "task": case,
        "steps": [
            {
                "step_number": 1,
                "tool": "browser",
                "input": inp,
                "output": out,
                "error": None,
            }
        ],
        "success": True,
        "redacted": False,
        "failure_point": None,
        "failure_class": None,
        "quality_label": "clear",
        "domain": "web",
        "severity": "low",
        "tags": ["reference", "browser", "success"],
        "expected_outcome": "should_silence",
        "expected_outcome_rationale": "Successful browser counterpart (#707 balance).",
        "expected_outcome_confidence": "high",
        "source": "webarena-issues",
        "source_repo": _SOURCE_REPO,
    }


def convert_webarena_issues(
    issues: list[dict[str, Any]],
    *,
    limit: int | None = None,
    timestamp: str = _TS,
) -> list[dict[str, Any]]:
    """Return failure (issues) + success reference records."""
    records: list[dict[str, Any]] = []
    # If caller passes empty list (synthesize mode), fall back to fixtures.
    source = issues if issues else list(_SYNTHETIC_ISSUES)
    for i, issue in enumerate(source):
        if limit is not None and i >= limit:
            break
        records.append(_failure(issue, i + 1, timestamp))
    for i, case in enumerate(_SUCCESS_CASES, start=1):
        records.append(_success(i, case, timestamp))
    return records


def main(argv: list[str] | None = None) -> None:
    """Convert WebArena issues JSON and write failure + success corpus files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issues", type=Path, required=False, default=None)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--success-output", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    if args.issues is not None:
        raw = json.loads(args.issues.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "items" in raw:
            raw = raw["items"]
        issues: list[dict[str, Any]] = raw if isinstance(raw, list) else []
    else:
        issues = list(_SYNTHETIC_ISSUES)

    records = convert_webarena_issues(issues, limit=args.limit)
    failures = [r for r in records if not r["success"]]
    successes = [r for r in records if r["success"]]

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / "browser-issues.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in failures) + "\n", encoding="utf-8")
    print(f"[convert] {len(failures)} failures -> {out}")

    if args.success_output is not None:
        args.success_output.mkdir(parents=True, exist_ok=True)
        success_out = args.success_output / "browser-successes.jsonl"
        success_out.write_text(
            "\n".join(json.dumps(r) for r in successes) + "\n", encoding="utf-8"
        )
        print(f"[convert] {len(successes)} successes -> {success_out}")


if __name__ == "__main__":
    main()
