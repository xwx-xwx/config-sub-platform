from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any, Optional


CACHE_DIR = Path("cache")
CACHE_TTL = 300


class FileCache:
    def __init__(self, name: str, ttl: int = CACHE_TTL) -> None:
        self._path = CACHE_DIR / f"{name}.json"
        self._ttl = ttl
        self._memory: dict[str, Any] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        if self._path.exists():
            try:
                with open(self._path) as f:
                    data = json.load(f)
                    self._memory = data.get("data", {})
                    expires = data.get("expires", 0)
                    if time.time() > expires:
                        self._memory = {}
            except (json.JSONDecodeError, OSError):
                self._memory = {}
        self._loaded = True

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "data": self._memory,
            "expires": time.time() + self._ttl,
        }
        with open(self._path, "w") as f:
            json.dump(data, f)

    def get(self, key: str) -> Optional[Any]:
        self._load()
        return self._memory.get(key)

    def set(self, key: str, value: Any) -> None:
        self._load()
        self._memory[key] = value
        self._save()

    def clear(self) -> None:
        self._memory = {}
        self._loaded = True
        self._save()
