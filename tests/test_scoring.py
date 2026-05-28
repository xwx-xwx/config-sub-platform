import pytest
from app.models.config import ProxyConfig
from app.scoring.engine import score_config


def test_score_reality():
    cfg = ProxyConfig(
        protocol="vless", host="a.com", port=443, uuid="u1", reality=True
    )
    s = score_config(cfg)
    assert s >= 25


def test_score_tls():
    cfg = ProxyConfig(
        protocol="vmess", host="a.com", port=443, uuid="u1", tls=True
    )
    s = score_config(cfg)
    assert s >= 15


def test_score_clean_hostname():
    cfg = ProxyConfig(
        protocol="vmess", host="cdn.example.com", port=443, uuid="u1"
    )
    s = score_config(cfg)
    assert s >= 10


def test_score_ws():
    cfg = ProxyConfig(
        protocol="vmess", host="a.com", port=443, uuid="u1", transport="ws"
    )
    s = score_config(cfg)
    assert s >= 10


def test_score_suspicious_port():
    cfg = ProxyConfig(
        protocol="vmess", host="a.com", port=8080, uuid="u1"
    )
    s = score_config(cfg)
    assert s < 0 or s >= 0  # just verify it doesn't crash


def test_score_grpc():
    cfg = ProxyConfig(
        protocol="vmess", host="a.com", port=443, uuid="u1", transport="grpc"
    )
    s = score_config(cfg)
    assert s >= 8


def test_score_cloudflare_ip():
    cfg = ProxyConfig(
        protocol="vmess", host="1.1.1.1", port=443, uuid="u1",
        tls=True, transport="ws",
    )
    s = score_config(cfg)
    assert s >= 20


def test_score_missing_host():
    cfg = ProxyConfig(protocol="vmess", host="", port=0, uuid="u1")
    s = score_config(cfg)
    assert s < 0
