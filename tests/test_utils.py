import pytest
from app.utils.cache import FileCache
from app.utils.retry import async_retry


def test_cache_set_get():
    cache = FileCache("test_cache", ttl=60)
    cache.clear()
    assert cache.get("key1") is None
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    cache.clear()


def test_cache_overwrite():
    cache = FileCache("test_cache2", ttl=60)
    cache.clear()
    cache.set("key", "old")
    cache.set("key", "new")
    assert cache.get("key") == "new"
    cache.clear()


@pytest.mark.asyncio
async def test_async_retry_success():
    async def succeeds():
        return 42

    result = await async_retry(succeeds, max_retries=2)
    assert result == 42


@pytest.mark.asyncio
async def test_async_retry_eventually_fails():
    call_count = 0

    async def always_fails():
        nonlocal call_count
        call_count += 1
        raise ValueError("boom")

    with pytest.raises(ValueError):
        await async_retry(always_fails, max_retries=3, base_delay=0.01, max_delay=0.1)

    assert call_count == 3
