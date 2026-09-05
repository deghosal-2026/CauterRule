from cauterule.config import Config, RedactionConfig
from cauterule.redaction.config import get_all_patterns, get_custom_patterns


def test_get_custom_patterns_none() -> None:
    assert get_custom_patterns(None) == ()
    assert get_all_patterns(None) == []


def test_get_custom_patterns_empty() -> None:
    cfg = Config(redaction=RedactionConfig(patterns=()))
    assert get_custom_patterns(cfg) == ()
    assert get_all_patterns(cfg) == []


def test_get_custom_patterns_with_values() -> None:
    cfg = Config(redaction=RedactionConfig(patterns=("my_secret.*", "custom_\\d+")))
    assert get_custom_patterns(cfg) == ("my_secret.*", "custom_\\d+")
    assert get_all_patterns(cfg) == ["my_secret.*", "custom_\\d+"]


def test_custom_patterns_integration() -> None:
    from cauterule.redaction.engine import redact_text

    cfg = Config(redaction=RedactionConfig(patterns=("CUSTOM_SECRET_\\d+",)))
    patterns = get_custom_patterns(cfg)
    assert redact_text("CUSTOM_SECRET_123", extra_patterns=list(patterns)) == "[REDACTED]"
