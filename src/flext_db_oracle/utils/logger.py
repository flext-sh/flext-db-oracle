"""Logging utilities for Oracle database operations."""

from __future__ import annotations

import logging
import sys


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name. If None, uses the calling module name.

    Returns:
        Configured logger instance.

    """
    if name is None:
        name = __name__

    logger = logging.getLogger(name)

    # Configure logger if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def configure_logging(level: str = "INFO", format_string: str | None = None) -> None:
    """Configure logging for the entire package.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format_string: Custom format string for log messages.

    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
