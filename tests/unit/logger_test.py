from __future__ import annotations

import os

import pytest

from src.hiero_sdk_python.logger.log_level import LogLevel
from src.hiero_sdk_python.logger.logger import Logger


pytestmark = pytest.mark.unit


def test_set_level():
    """Test that changing log level affects what will be logged."""
    logger = Logger(LogLevel.DEBUG, "test_logger")
    logger.set_level(LogLevel.ERROR)
    assert logger.level == LogLevel.ERROR


def test_get_level():
    """Test getting the current log level."""
    logger = Logger(level=LogLevel.DEBUG)
    assert logger.get_level() == LogLevel.DEBUG

    logger.set_level(LogLevel.ERROR)
    assert logger.get_level() == LogLevel.ERROR


def test_logger_creation():
    logger = Logger(LogLevel.DEBUG, "test_logger")
    assert logger.name == "test_logger"
    assert logger.level == LogLevel.DEBUG


def test_logger_creation_from_env():
    os.environ["LOG_LEVEL"] = "CRITICAL"
    logger = Logger(LogLevel.from_env())
    assert logger.level == LogLevel.CRITICAL


def test_logger_output(capsys):
    """Test that logger outputs the expected messages to stdout.

    This test uses pytest's capsys fixture to capture the actual log output,
    allowing verification of the exact content written to stdout by the logger.
    """
    # Create a logger that logs to the captured stdout with UNIQUE name
    logger = Logger(LogLevel.TRACE, "test_logger_output")

    # Log messages at different levels with key-value pairs
    logger.trace("trace message", "traceKey", "traceValue")
    logger.debug("debug message", "debugKey", "debugValue")
    logger.info("info message", "infoKey", "infoValue")
    logger.warning("warning message", "warningKey", "warningValue")
    logger.error("error message", "errorKey", "errorValue")

    # Get the captured output
    captured = capsys.readouterr()

    # Verify that each message appears in the output
    assert "trace message: traceKey = traceValue" in captured.out
    assert "debug message: debugKey = debugValue" in captured.out
    assert "info message: infoKey = infoValue" in captured.out
    assert "warning message: warningKey = warningValue" in captured.out
    assert "error message: errorKey = errorValue" in captured.out
    # Test silent mode
    logger.set_silent(True)
    logger.error("this should not appear")
    captured = capsys.readouterr()
    assert captured.out == ""

    # Test re-enabling logging
    logger.set_silent(False)
    logger.info("this should appear")
    captured = capsys.readouterr()
    assert "this should appear" in captured.out


def test_logger_respects_level(capsys):
    """Test that logger only outputs messages at or above its level.

    Uses pytest's capsys fixture to verify that log filtering works correctly
    by examining which messages actually appear in the captured output based on
    the configured log level.
    """
    # Create a logger that logs to the captured stdout with UNIQUE name
    logger = Logger(LogLevel.INFO, "test_logger_respects_level")

    # These should not be logged
    logger.trace("trace message")
    logger.debug("debug message")

    # These should be logged
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")

    # Get the captured output
    captured = capsys.readouterr()
    logger.info(captured.out)

    # Check that appropriate messages were logged or not logged
    assert "trace message" not in captured.out
    assert "debug message" not in captured.out
    assert "info message" in captured.out
    assert "warning message" in captured.out
    assert "error message" in captured.out

def test_from_env_unset_returns_error(monkeypatch):
    """from_env returns ERROR when LOG_LEVEL is not set."""
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    assert LogLevel.from_env() == LogLevel.ERROR


def test_from_env_empty_returns_error(monkeypatch):
    """from_env returns ERROR when LOG_LEVEL is set to an empty string."""
    monkeypatch.setenv("LOG_LEVEL", "")
    assert LogLevel.from_env() == LogLevel.ERROR


def test_from_env_invalid_returns_error(monkeypatch):
    """from_env returns ERROR (does not raise) when LOG_LEVEL is invalid.
    
    Client.__init__ calls LogLevel.from_env() during construction. Before
    this fix, a typo in the user's shell environment (LOG_LEVEL=foo)
    raised ValueError out of Client.__init__, blocking instantiation for
    any code path that needed a Client. The fix logs a warning and falls
    back to ERROR so the SDK remains usable while the user notices and
    corrects their environment variable.
    """
    monkeypatch.setenv("LOG_LEVEL", "foo")
    assert LogLevel.from_env() == LogLevel.ERROR


def test_from_env_valid_returns_level(monkeypatch):
    """from_env returns the matching level for a valid LOG_LEVEL value."""
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    assert LogLevel.from_env() == LogLevel.WARNING


def test_from_env_valid_lowercase_returns_level(monkeypatch):
    """from_env lowercases names so 'warning' and 'WARNING' both work."""
    monkeypatch.setenv("LOG_LEVEL", "warning")
    assert LogLevel.from_env() == LogLevel.WARNING
