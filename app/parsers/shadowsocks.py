from __future__ import annotations
from urllib.parse import urlparse
import base64
from typing import Optional

from app.models.config import ProxyConfig


def parse_shadowsocks(link: str) -> Optional[ProxyConfig]:
    try:
        parsed = urlparse(link)
        if parsed.scheme != "ss":
            return None

        if parsed.username and parsed.hostname and parsed.port:
            decoded_user = base64.b64decode(parsed.username + "==", validate=False).decode()
            return ProxyConfig(
                protocol="ss",
                host=parsed.hostname,
                port=parsed.port,
                password=decoded_user,
            )

        if parsed.hostname and not parsed.username:
            netloc = parsed.netloc.split("@")
            if len(netloc) == 2:
                b64_user = netloc[0]
                host_port = netloc[1]
                host, port_str = (host_port.split(":") + ["0"])[:2]
                try:
                    decoded_user = base64.b64decode(b64_user + "==", validate=False).decode()
                    return ProxyConfig(
                        protocol="ss",
                        host=host,
                        port=int(port_str),
                        password=decoded_user,
                    )
                except Exception:
                    pass

        b64_data = (parsed.path.lstrip("/") or parsed.netloc).strip()
        if b64_data:
            decoded = base64.b64decode(b64_data + "==", validate=False).decode()
            if "@" in decoded:
                method_pass, host_port = decoded.rsplit("@", 1)
                host, port_str = (host_port.split(":") + ["0"])[:2]
                return ProxyConfig(
                    protocol="ss",
                    host=host,
                    port=int(port_str),
                    password=method_pass,
                )

        return None
    except (ValueError, AttributeError, IndexError, Exception):
        return None
