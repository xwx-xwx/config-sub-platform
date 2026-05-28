from __future__ import annotations
import asyncio
import logging
from typing import TypeVar, Callable, Awaitable

from app.settings import load_settings

T = TypeVar("T")

logger = logging.getLogger("config-collector.retry")


async def async_retry(
    func: Callable[..., Awaitable[T]],
    *args,
    max_retries: int | None = None,
    base_delay: float | None = None,
    max_delay: float | None = None,
    **kwargs,
) -> T:
    settings = load_settings()
    retry_cfg = settings.retry
    max_r = max_retries or retry_cfg.get("max_retries", 3)
    base_d = base_delay or retry_cfg.get("base_delay", 1.0)
    max_d = max_delay or retry_cfg.get("max_delay", 30.0)

    last_exc = None
    for attempt in range(max_r):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exc = e
            if attempt < max_r - 1:
                delay = min(base_d * (2**attempt), max_d)
                logger.warning("Attempt %d failed: %s. Retrying in %.1fs", attempt + 1, e, delay)
                await asyncio.sleep(delay)
    raise last_exc  # type: ignore
