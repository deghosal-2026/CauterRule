"""Unsafe-directive coverage for destructive branch edits (#762 hardening).

The replay path cannot tell a destructive directive from a correct one, so the
linter must catch destructive-but-unlisted advice. Growing the blocklist
indefinitely is not the strategy; these pin the specific gap called out in
#762.
"""

from __future__ import annotations

from cauterule.linter.unsafe import check_unsafe


def test_delete_and_recreate_branch_is_caught() -> None:
    assert check_unsafe("delete the remote branch and recreate it from scratch") != []


def test_remove_branch_is_caught() -> None:
    assert check_unsafe("remove the branch and start over") != []


def test_nonsense_directive_is_clean() -> None:
    assert check_unsafe("water the office plants") == []


def test_benign_branch_advice_is_clean() -> None:
    # Talking about a branch is not itself destructive.
    assert check_unsafe("create a new branch before making changes") == []
    assert check_unsafe("switch to the branch and pull") == []
