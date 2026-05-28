import pytest
import json
import base64
from app.parsers import parse_link
from app.parsers.vmess import parse_vmess
from app.parsers.vless import parse_vless
from app.parsers.trojan import parse_trojan
from app.parsers.shadowsocks import parse_shadowsocks


def test_parse_vmess():
    raw = base64.b64encode(
        json.dumps(
            {
                "add": "example.com",
                "port": 443,
                "id": "uuid-here",
                "aid": 0,
                "net": "ws",
                "type": "none",
                "tls": "tls",
                "host": "example.com",
                "path": "/ws",
            }
        ).encode()
    ).decode()
    cfg = parse_vmess(f"vmess://{raw}")
    assert cfg is not None
    assert cfg.protocol == "vmess"
    assert cfg.host == "example.com"
    assert cfg.port == 443
    assert cfg.uuid == "uuid-here"
    assert cfg.transport == "ws"
    assert cfg.tls is True
    assert cfg.path == "/ws"


def test_parse_vmess_invalid():
    assert parse_vmess("vmess://invalid-base64!!!") is None


def test_parse_vless():
    cfg = parse_vless(
        "vless://uuid@example.com:443?security=tls&type=tcp&headerType=none"
    )
    assert cfg is not None
    assert cfg.protocol == "vless"
    assert cfg.host == "example.com"
    assert cfg.port == 443
    assert cfg.uuid == "uuid"
    assert cfg.tls is True


def test_parse_vless_reality():
    cfg = parse_vless(
        "vless://uuid@example.com:443?security=reality&type=tcp&fp=chrome&sni=example.com"
    )
    assert cfg is not None
    assert cfg.reality is True
    assert cfg.fp == "chrome"
    assert cfg.sni == "example.com"


def test_parse_trojan():
    cfg = parse_trojan("trojan://pass@example.com:443?security=tls&sni=example.com")
    assert cfg is not None
    assert cfg.protocol == "trojan"
    assert cfg.password == "pass"
    assert cfg.host == "example.com"
    assert cfg.port == 443
    assert cfg.tls is True


def test_parse_shadowsocks():
    cfg = parse_shadowsocks(
        "ss://YWVzLTI1Ni1nY206dGVzdEBleGFtcGxlLmNvbTo4MDgw"
    )
    assert cfg is not None
    assert cfg.protocol == "ss"
    assert cfg.host == "example.com"
    assert cfg.port == 8080


def test_parse_shadowsocks_standard_format():
    cfg = parse_shadowsocks("ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ@example.com:443")
    assert cfg is not None
    assert cfg.protocol == "ss"
    assert cfg.host == "example.com"
    assert cfg.port == 443


def test_parse_link_dispatcher():
    cfg = parse_link("vless://uuid@a.com:443")
    assert cfg is not None
    assert cfg.protocol == "vless"

    cfg2 = parse_link("vmess://" + base64.b64encode(json.dumps({"add": "a.com", "port": 443, "id": "u"}).encode()).decode())
    assert cfg2 is not None
    assert cfg2.protocol == "vmess"

    assert parse_link("unknown://foo") is None
    assert parse_link("") is None
