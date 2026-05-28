from __future__ import annotations
from urllib.parse import urlparse, parse_qs
from typing import Optional

from app.models.config import ProxyConfig


def parse_vless(link: str) -> Optional[ProxyConfig]:
    try:
        parsed = urlparse(link)
        if parsed.scheme != "vless":
            return None
        host_port = parsed.netloc.split("@")[-1] if "@" in parsed.netloc else parsed.netloc
        user_info = parsed.netloc.split("@")[0] if "@" in parsed.netloc else ""
        host, port = (host_port.split(":") + ["0"])[:2]
        params = parse_qs(parsed.query)
        return ProxyConfig(
            protocol="vless",
            host=host,
            port=int(port),
            uuid=user_info,
            security=params.get("security", [None])[0],
            transport=params.get("type", [None])[0] or "tcp",
            tls=params.get("security", [""])[0] in ("tls", "reality", "xtls"),
            sni=params.get("sni", [None])[0],
            path=params.get("path", [None])[0],
            network=params.get("type", [None])[0],
            fp=params.get("fp", [None])[0],
            reality=params.get("security", [""])[0] in ("reality", "xtls"),
        )
    except (ValueError, IndexError):
        return None
