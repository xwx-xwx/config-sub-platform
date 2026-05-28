from __future__ import annotations
import json
from pathlib import Path


def load_telegram_channels(path: str = "config/telegram_channels.txt") -> list[str]:
    p = Path(path)
    if not p.exists():
        return []
    channels = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            if not line.startswith("@"):
                line = "@" + line
            channels.append(line)
    return channels


def load_github_sources(path: str = "config/github_sources.json") -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def load_subscription_sources(path: str = "config/subscription_sources.txt") -> list[str]:
    p = Path(path)
    if not p.exists():
        return []
    urls = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls
