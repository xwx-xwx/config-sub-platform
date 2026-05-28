import pytest
from app.models.config import ProxyConfig
from app.outputs.base64 import encode_base64_subscription, decode_base64_subscription
from app.outputs.clash import generate_clash_config
from app.outputs.generator import generate_outputs
from pathlib import Path


def test_encode_decode_base64():
    lines = ["vmess://abc", "vless://def"]
    encoded = encode_base64_subscription(lines)
    assert isinstance(encoded, str)
    decoded = decode_base64_subscription(encoded)
    assert "vmess://abc" in decoded
    assert "vless://def" in decoded


def test_clash_generation():
    configs = [
        ProxyConfig(
            protocol="vmess",
            host="a.com",
            port=443,
            uuid="u1",
            tls=True,
            transport="ws",
            path="/ws",
        )
    ]
    yaml = generate_clash_config("test", configs)
    assert yaml is not None
    assert "a.com" in yaml
    assert "vmess-001" in yaml
    assert "/ws" in yaml


def test_clash_empty():
    assert generate_clash_config("test", []) is None


def test_generate_outputs(tmp_path):
    from app.outputs.generator import OUTPUT_DIR
    import app.settings

    original = app.settings.load_settings
    app.settings.load_settings = lambda path=None: type(
        "Settings", (),
        {
            "output": {"raw": True, "base64": True, "clash": False},
            "output_limits": {},
            "timeouts": {}, "health": {}, "sources": {},
            "retry": {}, "logging": {},
        },
    )()

    configs = [
        ProxyConfig(
            protocol="vmess", host="a.com", port=443,
            uuid="u1", raw="vmess://abc",
        )
    ]
    generate_outputs("test", configs)
    raw_file = Path("generated/test.txt")
    assert raw_file.exists()
    content = raw_file.read_text()
    assert "vmess://abc" in content
    raw_file.unlink()

    b64_file = Path("generated/base64/test.txt")
    if b64_file.exists():
        b64_file.unlink()

    app.settings.load_settings = original
