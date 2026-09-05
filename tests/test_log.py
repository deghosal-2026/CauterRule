import io
import json
import logging
import sys
from typing import Any

import pytest

from cauterule.log import JSONFormatter, get_logger, setup_logging


def _raise_value_error() -> None:
    raise ValueError("boom")


def test_json_formatter_basic_fields() -> None:
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="cauterule.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    output = formatter.format(record)
    data = json.loads(output)
    assert data["level"] == "INFO"
    assert data["logger"] == "cauterule.test"
    assert data["message"] == "hello world"
    assert "timestamp" in data
    assert data["timestamp"].endswith("+00:00")


def test_json_formatter_extra_fields() -> None:
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="cauterule.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="rule promoted",
        args=(),
        exc_info=None,
    )
    record.__dict__["rule_id"] = "R-001"
    record.__dict__["confidence"] = 0.85
    output = formatter.format(record)
    data = json.loads(output)
    assert data["rule_id"] == "R-001"
    assert data["confidence"] == 0.85


def test_json_formatter_non_serializable_coerced() -> None:
    formatter = JSONFormatter()

    class NotSerializable:
        def __str__(self) -> str:
            return "ns-repr"

    record = logging.LogRecord(
        name="cauterule.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="msg",
        args=(),
        exc_info=None,
    )
    record.__dict__["obj"] = NotSerializable()
    data = json.loads(formatter.format(record))
    assert data["obj"] == "ns-repr"


def test_json_formatter_exc_info() -> None:
    formatter = JSONFormatter()
    exc_info: tuple[type[BaseException], BaseException, Any] | tuple[None, None, None]
    try:
        _raise_value_error()
    except ValueError:
        exc_info = sys.exc_info()
    else:
        exc_info = (None, None, None)

    record = logging.LogRecord(
        name="cauterule.test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=10,
        msg="failed",
        args=(),
        exc_info=exc_info,
    )
    data = json.loads(formatter.format(record))
    assert "exc_info" in data
    assert "ValueError: boom" in data["exc_info"]


def test_json_formatter_filters_standard_fields() -> None:
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="cauterule.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="hi",
        args=(),
        exc_info=None,
    )
    # Internal attributes should not leak.
    data = json.loads(formatter.format(record))
    assert "pathname" not in data
    assert "lineno" not in data
    assert "args" not in data


def test_json_formatter_private_keys_filtered() -> None:
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="cauterule.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="hi",
        args=(),
        exc_info=None,
    )
    record.__dict__["_private"] = "secret"
    data = json.loads(formatter.format(record))
    assert "_private" not in data


def test_setup_logging_json_format() -> None:
    stream = io.StringIO()
    setup_logging(level="INFO", json_format=True, stream=stream)
    logger = get_logger("cauterule.test.json")
    logger.info("hello json")
    line = stream.getvalue().strip()
    assert line
    data = json.loads(line)
    assert data["message"] == "hello json"
    assert data["level"] == "INFO"
    # Cleanup
    logging.getLogger().handlers.clear()


def test_setup_logging_plain_format() -> None:
    stream = io.StringIO()
    setup_logging(level="INFO", json_format=False, stream=stream)
    logger = get_logger("cauterule.test.plain")
    logger.info("hello plain")
    line = stream.getvalue().strip()
    assert "hello plain" in line
    assert "INFO" in line
    logging.getLogger().handlers.clear()


def test_setup_logging_levels() -> None:
    for level_str, expected in [
        ("DEBUG", logging.DEBUG),
        ("info", logging.INFO),
        ("WARNING", logging.WARNING),
        ("WARN", logging.WARNING),
        ("error", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
    ]:
        stream = io.StringIO()
        setup_logging(level=level_str, stream=stream)
        assert logging.getLogger().level == expected
        logging.getLogger().handlers.clear()

    # int passthrough
    stream2 = io.StringIO()
    setup_logging(level=logging.DEBUG, stream=stream2)
    assert logging.getLogger().level == logging.DEBUG
    logging.getLogger().handlers.clear()


def test_setup_logging_invalid_level() -> None:
    stream = io.StringIO()
    with pytest.raises(ValueError, match="Unknown log level"):
        setup_logging(level="VERBOSE", stream=stream)
    logging.getLogger().handlers.clear()


def test_setup_logging_clears_previous_handlers() -> None:
    stream1 = io.StringIO()
    setup_logging(level="INFO", stream=stream1)
    assert len(logging.getLogger().handlers) == 1
    stream2 = io.StringIO()
    setup_logging(level="INFO", stream=stream2)
    assert len(logging.getLogger().handlers) == 1
    logging.getLogger().handlers.clear()


def test_setup_logging_default_stream() -> None:
    # Should default to sys.stderr without error.
    setup_logging(level="INFO")
    assert len(logging.getLogger().handlers) == 1
    logging.getLogger().handlers.clear()


def test_get_logger() -> None:
    logger = get_logger("cauterule.test.get")
    assert logger.name == "cauterule.test.get"
    assert isinstance(logger, logging.Logger)


def test_version_import() -> None:
    import cauterule

    assert isinstance(cauterule.__version__, str)
    assert len(cauterule.__version__) > 0
