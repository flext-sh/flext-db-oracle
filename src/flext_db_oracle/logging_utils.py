"""Logging utilities with fallback for flext-observability.

This module provides a compatibility layer for logging that gracefully
falls back to standard logging when flext-observability is not available.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


def get_logger(name: str) -> Logger:
    """Get logger with fallback to standard logging.

    Tries to use flext-observability's enhanced logging first,
    falls back to standard Python logging if not available.

    Args:
        name: Logger name, typically __name__

    Returns:
        Logger instance

    """
    try:
        from flext_observability.logging import get_logger as flext_get_logger

        return flext_get_logger(name)
    except ImportError:
        # Fallback to standard logging when flext-observability is not available
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
