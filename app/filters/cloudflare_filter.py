from __future__ import annotations
from app.models.config import ProxyConfig
from app.filters.cloudflare import is_cloudflare_config
from app.settings import load_settings


def cloudflare_filter(configs: list[ProxyConfig]) -> list[ProxyConfig]:
    settings = load_settings()
    limit = settings.output_limits.get("cloudflare", 150)
    filtered = [c for c in configs if is_cloudflare_config(c)]
    filtered.sort(key=lambda c: c.score, reverse=True)
    return filtered[:limit]
