import pytest
from app.models.config import ProxyConfig, ConfigHash


def test_proxy_config_minimal_fields():
    cfg = ProxyConfig(
        protocol="vmess",
        host="example.com",
        port=443,
        uuid="abc-def",
    )
    assert cfg.protocol == "vmess"
    assert cfg.host == "example.com"
    assert cfg.port == 443
    assert cfg.score == 0


def test_config_hash_uniqueness():
    a = ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1")
    b = ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1")
    c = ProxyConfig(protocol="vless", host="b.com", port=80, uuid="u2")
    assert ConfigHash(a) == ConfigHash(b)
    assert ConfigHash(a) != ConfigHash(c)


def test_config_hash_mismatch_on_different_port():
    a = ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1")
    b = ProxyConfig(protocol="vmess", host="a.com", port=80, uuid="u1")
    assert ConfigHash(a) != ConfigHash(b)


def test_dedup_key():
    a = ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1")
    key = a.dedup_key()
    assert key == ("vmess", "a.com", 443, "u1", "", "")
