from __future__ import annotations
from app.models.config import ProxyConfig


def is_reality_config(cfg: ProxyConfig) -> bool:
    return bool(cfg.reality) or (cfg.security in ("reality", "xtls"))
