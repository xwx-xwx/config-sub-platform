import pytest
from app.models.config import ProxyConfig
from app.dedup import deduplicate


def test_dedup_exact_duplicates():
    configs = [
        ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1"),
        ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1"),
    ]
    result = deduplicate(configs)
    assert len(result) == 1


def test_dedup_no_duplicates():
    configs = [
        ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1"),
        ProxyConfig(protocol="vless", host="b.com", port=80, uuid="u2"),
    ]
    result = deduplicate(configs)
    assert len(result) == 2


def test_dedup_host_port_different():
    configs = [
        ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1"),
        ProxyConfig(protocol="vmess", host="a.com", port=80, uuid="u1"),
    ]
    result = deduplicate(configs)
    assert len(result) == 2


def test_dedup_preserves_highest_score():
    configs = [
        ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1", score=10),
        ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1", score=50),
    ]
    result = deduplicate(configs)
    assert len(result) == 1
    assert result[0].score == 50


def test_dedup_handles_password():
    configs = [
        ProxyConfig(protocol="trojan", host="a.com", port=443, password="p1"),
        ProxyConfig(protocol="trojan", host="a.com", port=443, password="p1"),
    ]
    result = deduplicate(configs)
    assert len(result) == 1


def test_normalize_then_dedup():
    from app.normalizers.normalize import normalize_config

    raw = [
        ProxyConfig(protocol="vmess", host=" EXAMPLE.COM ", port=443, uuid="u1"),
        ProxyConfig(protocol="vmess", host="example.com", port=443, uuid="u1"),
    ]
    normalized = [normalize_config(c) for c in raw]
    result = deduplicate(normalized)
    assert len(result) == 1
    assert result[0].host == "example.com"
