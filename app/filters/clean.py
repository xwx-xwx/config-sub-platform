from __future__ import annotations
import re
from app.models.config import ProxyConfig
from app.settings import load_settings

GARBAGE_HOSTS = re.compile(r"(localhost|0\.0\.0\.0|127\.0\.0\.1|test|example)")


def clean_filter(configs: list[ProxyConfig]) -> list[ProxyConfig]:
    settings = load_settings()
    limit = settings.output_limits.get("clean", 100)

    def is_clean(cfg: ProxyConfig) -> bool:
        if not cfg.host or GARBAGE_HOSTS.search(cfg.host):
            return False
        if cfg.port <= 0 or cfg.port > 65535:
            return False
        if not cfg.uuid and not cfg.password:
            return False
        if cfg.score < 0:
            return False
        return True

    filtered = [c for c in configs if is_clean(c)]
    filtered.sort(key=lambda c: c.score, reverse=True)
    return filtered[:limit]
