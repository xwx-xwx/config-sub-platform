from __future__ import annotations
import ipaddress
import socket

from app.models.config import ProxyConfig

CLOUDFLARE_RANGES = [
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22",
    "104.16.0.0/12",
    "108.162.192.0/18",
    "131.0.72.0/22",
    "141.101.64.0/18",
    "162.158.0.0/15",
    "172.64.0.0/13",
    "173.245.48.0/20",
    "188.114.96.0/20",
    "190.93.240.0/20",
    "197.234.240.0/22",
    "198.41.128.0/17",
    "1.0.0.0/24",
    "1.1.1.0/24",
]

CLOUDFLARE_NETWORKS = [ipaddress.ip_network(r) for r in CLOUDFLARE_RANGES]

SUSPICIOUS_PORTS = {25, 110, 143, 465, 587, 993, 995, 3306, 5432, 6379, 27017}

CLEAN_HOSTNAME_PATTERNS = [
    "cdn", "proxy", "speed", "download", "api", "edge",
    "static", "media", "cloud", "server", "node", "v2ray",
]


def _is_cloudflare_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host))
        return any(ip in network for network in CLOUDFLARE_NETWORKS)
    except (socket.gaierror, ValueError):
        return False


def _is_clean_hostname(host: str) -> bool:
    host_lower = host.lower()
    return any(p in host_lower for p in CLEAN_HOSTNAME_PATTERNS)


def score_config(cfg: ProxyConfig) -> int:
    score = 0

    if not cfg.host or not cfg.port:
        return -100

    if cfg.reality:
        score += 25

    if _is_cloudflare_ip(cfg.host) or "cloudflare" in cfg.host.lower():
        score += 20

    if cfg.tls:
        score += 15

    if _is_clean_hostname(cfg.host):
        score += 10

    if cfg.transport == "ws":
        score += 10
    elif cfg.transport == "grpc":
        score += 8

    try:
        ip = ipaddress.ip_address(socket.gethostbyname(cfg.host))
        if ip.version == 4:
            score += 5
    except (socket.gaierror, ValueError):
        pass

    if cfg.port in SUSPICIOUS_PORTS:
        score -= 10

    return score
