"""Async utility helpers for flext_db_oracle.

This module provides utilities for bridging async and sync contexts.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from typing import TYPE_CHECKING, TypeVar, cast

if TYPE_CHECKING:
    from collections.abc import Awaitable, Coroutine

T = TypeVar("T")


def flext_db_oracle_run_async_in_sync_context[T](awaitable: Awaitable[T]) -> T:
    """Run async function in sync context.

    This utility function allows calling async functions from sync code
    by managing the async event loop.

    Args:
        awaitable: The async function or coroutine to execute.

    Returns:
        The result of the async function.

    Raises:
        RuntimeError: If there's an issue with the event loop.

    """
    try:
        # Try to get existing event loop
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, create and run one
        coro = cast("Coroutine[object, object, T]", awaitable)
        return asyncio.run(coro)
    else:
        # We're already in an async context, this shouldn't happen
        # in a sync context, but handle it gracefully
        coro = cast("Coroutine[object, object, T]", awaitable)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future: concurrent.futures.Future[T] = executor.submit(asyncio.run, coro)
            return future.result()
