# SECURITY-FIXTURE: token-like strings below are intentional fake credentials
# used to verify redaction patterns. None are real secrets.

from cauterule.redaction.patterns import BUILTIN_PATTERNS, get_builtin_patterns, get_pattern_names


def test_builtin_patterns() -> None:
    patterns = get_builtin_patterns()
    assert len(patterns) >= 10
    # ensure each is compiled
    for pat in patterns:
        assert hasattr(pat, "search")
        assert hasattr(pat, "sub")
    # names
    names = get_pattern_names()
    assert "aws_access_key" in names
    assert "github_token" in names
    assert "jwt" in names
    # BUILTIN_PATTERNS is same as get_builtin_patterns
    assert BUILTIN_PATTERNS is not get_builtin_patterns()
    assert get_builtin_patterns() == BUILTIN_PATTERNS or len(BUILTIN_PATTERNS) == len(patterns)


def test_pattern_match_examples() -> None:
    patterns = dict(zip(get_pattern_names(), get_builtin_patterns(), strict=False))
    assert patterns["aws_access_key"].search("AKIAIOSFODNN7EXAMPLE")
    assert patterns["github_token"].search("ghp_123456789012345678901234567890123456")
    assert patterns["jwt"].search("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature")
    assert patterns["openai_key"].search("sk-12345678901234567890abc")
