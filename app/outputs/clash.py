from __future__ import annotations
from typing import Optional

import yaml

from app.models.config import ProxyConfig


def generate_clash_config(name: str, configs: list[ProxyConfig]) -> Optional[str]:
    if not configs:
        return None

    proxies = []
    for i, cfg in enumerate(configs):
        proxy: dict = {
            "name": f"{cfg.protocol}-{i+1:03d}",
            "type": cfg.protocol,
            "server": cfg.host,
            "port": cfg.port,
        }
        if cfg.uuid:
            proxy["uuid"] = cfg.uuid
        if cfg.password:
            proxy["password"] = cfg.password
        if cfg.tls:
            proxy["tls"] = True
        if cfg.sni:
            proxy["sni"] = cfg.sni
        if cfg.transport == "ws":
            proxy["network"] = "ws"
            if cfg.path:
                proxy["ws-opts"] = {"path": cfg.path}
        proxies.append(proxy)

    clash_cfg = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": True,
        "mode": "Rule",
        "log-level": "info",
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": "Proxy",
                "type": "select",
                "proxies": [p["name"] for p in proxies],
            }
        ],
    }
    return yaml.dump(clash_cfg, default_flow_style=False, allow_unicode=True)
