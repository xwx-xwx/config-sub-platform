import pytest
from app.models.config import ProxyConfig
from app.normalizers.normalize import normalize_config


def test_normalize_hostname():
    cfg = ProxyConfig(protocol="vmess", host=" Example.COM ", port=443, uuid="u1")
    result = normalize_config(cfg)
    assert result.host == "example.com"


def test_normalize_transport_names():
    cfg = ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1", transport="websocket")
    result = normalize_config(cfg)
    assert result.transport == "ws"


def test_normalize_gun_to_grpc():
    cfg = ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1", transport="gun")
    result = normalize_config(cfg)
    assert result.transport == "grpc"


def test_normalize_keeps_tcp():
    cfg = ProxyConfig(protocol="vmess", host="a.com", port=443, uuid="u1", transport="tcp")
    result = normalize_config(cfg)
    assert result.transport == "tcp"


def test_normalize_forces_lowercase_host():
    cfg = ProxyConfig(protocol="vless", host="EXAMPLE.NET", port=443, uuid="u1")
    result = normalize_config(cfg)
    assert result.host == "example.net"


def test_normalize_no_mutation_of_original():
    cfg = ProxyConfig(protocol="vmess", host=" EXAMPLE.COM ", port=443, uuid="u1")
    original_host = cfg.host
    normalize_config(cfg)
    assert cfg.host == original_host
