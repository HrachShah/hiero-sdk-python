"""
Log level module for the Hiero SDK.

This module defines the log levels used throughout the SDK.
"""

from __future__ import annotations

import os
from enum import IntEnum


class LogLevel(IntEnum):
    """Enumeration of log levels."""

    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    DISABLED = 60

    # Old warn method will be depreciated
    WARN = WARNING

    def to_python_level(self) -> int:
        """Convert to Python's logging level.

        Returns:
            int: The Python logging level
        """
        return self.value

    @classmethod
    def from_string(cls, level_str: str) -> LogLevel:
        """Convert a string to a LogLevel.

        Args:
            level_str: The string to convert

        Returns:
            LogLevel: The LogLevel enum value
        """
        if level_str is None:
            return cls.ERROR

        try:
            return cls[level_str.upper()]
        except KeyError as e:
            raise ValueError(f"Invalid log level: {level_str}") from e

    @classmethod
    def from_env(cls) -> LogLevel:
        """
        Get log level from the ``LOG_LEVEL`` environment variable.

        Returns the parsed level when ``LOG_LEVEL`` is set to a recognised
        name (case-insensitive, e.g. ``INFO``, ``debug``). When the
        variable is unset, empty, or set to a name that is not a member
        of :class:`LogLevel`, falls back to :attr:`LogLevel.ERROR` rather
        than raising, so a stray ``LOG_LEVEL`` from another tool in the
        same shell does not break ``Client()`` construction.

        Returns:
            LogLevel: The resolved log level.
        """
        level_str = os.getenv("LOG_LEVEL")
        if not level_str:
            return cls.ERROR
        try:
            return cls.from_string(level_str)
        except ValueError:
            return cls.ERROR
