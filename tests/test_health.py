import pytest
from app.health.checker import check_tcp, check_config, HealthResult
from app.models.config import ProxyConfig


@pytest.mark.asyncio
async def test_check_tcp_valid_host():
    result = await check_tcp("8.8.8.8", 53, timeout=3)
    assert result.alive is True
    assert result.latency_ms > 0


@pytest.mark.asyncio
async def test_check_tcp_unreachable():
    result = await check_tcp("255.255.255.255", 9999, timeout=1)
    assert result.alive is False


@pytest.mark.asyncio
async def test_check_config():
    cfg = ProxyConfig(protocol="vmess", host="8.8.8.8", port=53, uuid="u1")
    result = await check_config(cfg, timeout=3)
    assert result.alive is True
