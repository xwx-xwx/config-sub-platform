from __future__ import annotations
import re

LINK_PATTERN = re.compile(
    r"(vmess://[A-Za-z0-9+/=_-]+|vless://[^\s<>\"']+|trojan://[^\s<>\"']+|ss://[^\s<>\"']+)"
)


def extract_links_from_text(text: str) -> list[str]:
    return LINK_PATTERN.findall(text)


def extract_links(sources: list[str]) -> list[str]:
    links: list[str] = []
    for source in sources:
        links.extend(extract_links_from_text(source))
    return links
