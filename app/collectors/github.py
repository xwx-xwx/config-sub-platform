from __future__ import annotations
import logging
from typing import Any

import httpx

from app.utils.retry import async_retry
from app.utils.cache import FileCache

logger = logging.getLogger("config-collector.github")
cache = FileCache("github_sources", ttl=300)


async def collect_from_github(sources: list[dict[str, Any]]) -> list[str]:
    collected: list[str] = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        for source in sources:
            url = source.get("url", "")
            name = source.get("name", url)

            cached = cache.get(url)
            if cached is not None:
                collected.extend(cached)
                continue

            try:
                response = await async_retry(
                    client.get,
                    url,
                    max_retries=2,
                )
                response.raise_for_status()
                text = response.text
                cache.set(url, [text])
                collected.append(text)
                logger.info("Collected %d bytes from %s", len(text), name)
            except Exception as e:
                logger.error("Failed to fetch %s: %s", name, e)
    return collected
