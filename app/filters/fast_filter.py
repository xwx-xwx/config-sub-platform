from __future__ import annotations
from app.models.config import ProxyConfig
from app.settings import load_settings


def fast_filter(configs: list[ProxyConfig]) -> list[ProxyConfig]:
    settings = load_settings()
    limit = settings.output_limits.get("fast", 50)
    sorted_configs = sorted(configs, key=lambda c: c.score, reverse=True)
    return sorted_configs[:limit]
