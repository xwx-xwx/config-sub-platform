from __future__ import annotations
from app.models.config import ProxyConfig
from app.filters.reality import is_reality_config
from app.settings import load_settings


def reality_filter(configs: list[ProxyConfig]) -> list[ProxyConfig]:
    settings = load_settings()
    limit = settings.output_limits.get("reality", 100)
    filtered = [c for c in configs if is_reality_config(c)]
    filtered.sort(key=lambda c: c.score, reverse=True)
    return filtered[:limit]
