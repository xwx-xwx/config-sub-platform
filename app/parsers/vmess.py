from __future__ import annotations
import json
import base64
from typing import Optional

from app.models.config import ProxyConfig


def parse_vmess(link: str) -> Optional[ProxyConfig]:
    try:
        b64_part = link.removeprefix("vmess://")
        decoded = base64.b64decode(b64_part + "==", validate=False)
        data = json.loads(decoded)
    except (json.JSONDecodeError, ValueError, Exception):
        return None

    try:
        return ProxyConfig(
            protocol="vmess",
            host=data.get("add", ""),
            port=int(data.get("port", 0)),
            uuid=data.get("id", ""),
            security=data.get("security"),
            transport=data.get("net", "tcp"),
            tls=data.get("tls") == "tls",
            sni=data.get("sni") or data.get("host"),
            path=data.get("path"),
            network=data.get("net"),
        )
    except (ValueError, TypeError):
        return None
