from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


class Settings:
    def __init__(self, data: dict[str, Any]) -> None:
        self.output_limits: dict[str, int] = data.get("output_limits", {})
        self.timeouts: dict[str, float] = data.get("timeouts", {})
        self.health: dict[str, Any] = data.get("health", {})
        self.sources: dict[str, bool] = data.get("sources", {})
        self.retry: dict[str, Any] = data.get("retry", {})
        self.logging: dict[str, str] = data.get("logging", {})
        self.output: dict[str, bool] = data.get("output", {})

    @classmethod
    def from_file(cls, path: str | Path) -> Settings:
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(data or {})


@lru_cache(maxsize=1)
def load_settings(path: str = "config/settings.yaml") -> Settings:
    return Settings.from_file(path)
