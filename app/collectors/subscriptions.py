from __future__ import annotations
import base64
import logging
from typing import Optional

import httpx

from app.utils.retry import async_retry
from app.utils.cache import FileCache

logger = logging.getLogger("config-collector.subscriptions")
cache = FileCache("subscription_urls", ttl=300)


def try_decode_base64(text: str) -> Optional[str]:
    try:
        decoded = base64.b64decode(text.strip() + "==", validate=False)
        result = decoded.decode("utf-8", errors="replace")
        if "://" in result:
            return result
    except Exception:
        pass
    return None


async def collect_from_subscriptions(urls: list[str]) -> list[str]:
    collected: list[str] = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        for url in urls:
            if not url.strip() or url.startswith("#"):
                continue
            url = url.strip()

            cached = cache.get(url)
            if cached is not None:
                collected.extend(cached)
                continue

            try:
                response = await async_retry(client.get, url, max_retries=2)
                response.raise_for_status()
                text = response.text

                configs: list[str] = []
                decoded = try_decode_base64(text)
                if decoded:
                    for line in decoded.splitlines():
                        line = line.strip()
                        if "://" in line:
                            configs.append(line)
                else:
                    for line in text.splitlines():
                        line = line.strip()
                        if "://" in line:
                            configs.append(line)

                cache.set(url, configs)
                collected.extend(configs)
                logger.info("Collected %d configs from %s", len(configs), url)
            except Exception as e:
                logger.error("Failed to fetch subscription %s: %s", url, e)
    return collected
