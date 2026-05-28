from __future__ import annotations
from app.models.config import ProxyConfig
from app.scoring.engine import _is_cloudflare_ip


def is_cloudflare_config(cfg: ProxyConfig) -> bool:
    return _is_cloudflare_ip(cfg.host) or (
        cfg.transport in ("ws", "grpc")
        and cfg.tls
        and "cloudflare" in cfg.host.lower()
    )
