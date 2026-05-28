from __future__ import annotations
from app.models.config import ProxyConfig

TRANSPORT_ALIASES = {
    "websocket": "ws",
    "ws": "ws",
    "grpc": "grpc",
    "gun": "grpc",
    "tcp": "tcp",
    "kcp": "kcp",
    "quic": "quic",
}


def normalize_config(cfg: ProxyConfig) -> ProxyConfig:
    normalized = cfg.model_copy(deep=True)

    if normalized.host:
        normalized.host = normalized.host.strip().lower()

    if normalized.sni:
        normalized.sni = normalized.sni.strip().lower()

    if normalized.transport:
        normalized.transport = TRANSPORT_ALIASES.get(
            normalized.transport.strip().lower(), normalized.transport.strip().lower()
        )

    if normalized.network:
        normalized.network = TRANSPORT_ALIASES.get(
            normalized.network.strip().lower(), normalized.network.strip().lower()
        )

    if normalized.path:
        normalized.path = normalized.path.strip()

    if normalized.security:
        normalized.security = normalized.security.strip().lower()

    return normalized
