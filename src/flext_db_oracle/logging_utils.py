"""Logging utilities with fallback for flext-observability.

This module provides a compatibility layer for logging that gracefully
falls back to standard logging when flext-observability is not available.
"""

from __future__ import annotations

import logging
from logging import Logger
from typing import cast


def flext_db_oracle_get_logger(name: str) -> Logger:
    """Get logger with fallback to standard logging.

    Tries to use flext-observability's enhanced logging first,
    falls back to standard Python logging if not available.

    Args:
        name: Logger name, typically __name__

    Returns:
        Logger instance

    """
    try:
        from flext_observability.logging import (  # type: ignore[import-untyped]
            get_logger as flext_get_logger,
        )

        return cast("Logger", flext_get_logger(name))
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


# Backward compatibility alias
get_logger = flext_db_oracle_get_logger
