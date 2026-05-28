from __future__ import annotations
from app.models.config import ProxyConfig
from app.settings import load_settings


def mobile_filter(configs: list[ProxyConfig]) -> list[ProxyConfig]:
    settings = load_settings()
    limit = settings.output_limits.get("mobile", 100)

    def mobile_score(cfg: ProxyConfig) -> int:
        s = 0
        if cfg.transport == "ws":
            s += 20
        if cfg.tls:
            s += 10
        if "cloudflare" in cfg.host.lower():
            s += 15
        return s + cfg.score

    sorted_configs = sorted(configs, key=mobile_score, reverse=True)
    return sorted_configs[:limit]
