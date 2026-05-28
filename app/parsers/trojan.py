from __future__ import annotations
from urllib.parse import urlparse, parse_qs
from typing import Optional

from app.models.config import ProxyConfig


def parse_trojan(link: str) -> Optional[ProxyConfig]:
    try:
        parsed = urlparse(link)
        if parsed.scheme != "trojan":
            return None
        password = parsed.username or ""
        host = parsed.hostname or ""
        port = parsed.port or 443
        params = parse_qs(parsed.query)
        return ProxyConfig(
            protocol="trojan",
            host=host,
            port=port,
            password=password,
            security=params.get("security", [None])[0],
            tls=params.get("security", [""])[0] in ("tls", "reality"),
            sni=params.get("sni", [None])[0] or host,
            transport=params.get("type", [None])[0] or "tcp",
            reality=params.get("security", [""])[0] == "reality",
        )
    except (ValueError, AttributeError):
        return None
