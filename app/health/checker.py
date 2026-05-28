from __future__ import annotations
import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Optional

from app.models.config import ProxyConfig

logger = logging.getLogger("config-collector.health")


@dataclass
class HealthResult:
    alive: bool
    latency_ms: float = 0.0
    error: Optional[str] = None


async def check_tcp(host: str, port: int, timeout: float = 3.0) -> HealthResult:
    start = time.monotonic()
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        elapsed = (time.monotonic() - start) * 1000
        writer.close()
        await writer.wait_closed()
        return HealthResult(alive=True, latency_ms=round(elapsed, 1))
    except (asyncio.TimeoutError, OSError, ConnectionError) as e:
        elapsed = (time.monotonic() - start) * 1000
        return HealthResult(
            alive=False, latency_ms=round(elapsed, 1), error=str(e)
        )


async def check_config(cfg: ProxyConfig, timeout: float = 3.0) -> HealthResult:
    return await check_tcp(cfg.host, cfg.port, timeout=timeout)
