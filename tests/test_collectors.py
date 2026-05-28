import pytest
from app.collectors.github import collect_from_github
from app.collectors.subscriptions import collect_from_subscriptions, try_decode_base64
from app.sources import (
    load_telegram_channels,
    load_github_sources,
    load_subscription_sources,
)


@pytest.mark.asyncio
async def test_collect_from_github_empty():
    result = await collect_from_github([])
    assert result == []


@pytest.mark.asyncio
async def test_collect_from_subscriptions_empty():
    result = await collect_from_subscriptions([])
    assert result == []


@pytest.mark.asyncio
async def test_collect_from_subscriptions_comments():
    result = await collect_from_subscriptions(["# comment", "  ", ""])
    assert result == []


def test_try_decode_base64_valid():
    import base64
    content = "vmess://abc vless://def"
    encoded = base64.b64encode(content.encode()).decode()
    result = try_decode_base64(encoded)
    assert result is not None
    assert "vmess://abc" in result


def test_try_decode_base64_invalid():
    assert try_decode_base64("not base64 at all") is None


def test_try_decode_base64_plain_text():
    assert try_decode_base64("Just regular text without links") is None


def test_load_telegram_channels(tmp_path):
    f = tmp_path / "channels.txt"
    f.write_text("# comment\n@channel1\nchannel2\n")
    result = load_telegram_channels(str(f))
    assert result == ["@channel1", "@channel2"]


def test_load_github_sources(tmp_path):
    f = tmp_path / "sources.json"
    f.write_text('[{"name": "test", "url": "https://example.com", "type": "raw"}]')
    result = load_github_sources(str(f))
    assert len(result) == 1
    assert result[0]["name"] == "test"


def test_load_github_sources_empty(tmp_path):
    f = tmp_path / "empty.json"
    f.write_text("[]")
    result = load_github_sources(str(f))
    assert result == []


def test_load_subscription_sources(tmp_path):
    f = tmp_path / "subs.txt"
    f.write_text("# comment\nhttps://example.com/sub\n")
    result = load_subscription_sources(str(f))
    assert result == ["https://example.com/sub"]
