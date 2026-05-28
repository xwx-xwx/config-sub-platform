from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class ProxyConfig(BaseModel):
    protocol: str
    host: str
    port: int
    uuid: Optional[str] = None
    password: Optional[str] = None
    security: Optional[str] = None
    transport: Optional[str] = None
    tls: Optional[bool] = None
    sni: Optional[str] = None
    path: Optional[str] = None
    network: Optional[str] = None
    fp: Optional[str] = None
    reality: Optional[bool] = None
    source: Optional[str] = None
    raw: Optional[str] = None
    score: int = 0

    def dedup_key(self) -> tuple:
        return (
            self.protocol,
            self.host,
            self.port,
            self.uuid or self.password or "",
            self.transport or "",
            self.security or "",
        )


class ConfigHash:
    def __init__(self, config: ProxyConfig) -> None:
        self._key = config.dedup_key()

    def __hash__(self) -> int:
        return hash(self._key)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConfigHash):
            return NotImplemented
        return self._key == other._key
