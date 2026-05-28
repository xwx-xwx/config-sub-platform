from __future__ import annotations
from app.models.config import ProxyConfig, ConfigHash


def deduplicate(configs: list[ProxyConfig]) -> list[ProxyConfig]:
    seen: dict[int, ProxyConfig] = {}
    for cfg in configs:
        key = hash(ConfigHash(cfg))
        if key not in seen or cfg.score > seen[key].score:
            seen[key] = cfg
    return list(seen.values())
