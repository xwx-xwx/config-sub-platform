from __future__ import annotations
import asyncio
import time

from app.settings import load_settings
from app.sources import (
    load_telegram_channels,
    load_github_sources,
    load_subscription_sources,
)
from app.collectors.telegram import collect_from_telegram
from app.collectors.github import collect_from_github
from app.collectors.subscriptions import collect_from_subscriptions
from app.extractors.links import extract_links
from app.parsers import parse_link
from app.normalizers.normalize import normalize_config
from app.dedup import deduplicate
from app.scoring.engine import score_config
from app.health.checker import check_config
from app.filters import (
    mix_filter,
    cloudflare_filter,
    reality_filter,
    mobile_filter,
    fast_filter,
    clean_filter,
)
from app.outputs.generator import generate_outputs
from app.utils.logger import get_logger

logger = get_logger("config-collector.pipeline")

FILTERS = {
    "mix": mix_filter,
    "cloudflare": cloudflare_filter,
    "reality": reality_filter,
    "mobile": mobile_filter,
    "fast": fast_filter,
    "clean": clean_filter,
}


async def run_pipeline() -> None:
    start = time.monotonic()
    settings = load_settings()

    logger.info("Starting config collection pipeline")

    all_texts: list[str] = []

    if settings.sources.get("telegram", True):
        channels = load_telegram_channels()
        if channels:
            texts = await collect_from_telegram(channels)
            all_texts.extend(texts)
            logger.info(
                "Telegram: collected %d messages from %d channels",
                len(texts),
                len(channels),
            )

    if settings.sources.get("github", True):
        github_sources = load_github_sources()
        if github_sources:
            texts = await collect_from_github(github_sources)
            all_texts.extend(texts)
            logger.info(
                "GitHub: collected %d responses from %d sources",
                len(texts),
                len(github_sources),
            )

    if settings.sources.get("subscriptions", True):
        sub_urls = load_subscription_sources()
        if sub_urls:
            config_lines = await collect_from_subscriptions(sub_urls)
            all_texts.extend(config_lines)
            logger.info(
                "Subscriptions: collected %d configs from %d URLs",
                len(config_lines),
                len(sub_urls),
            )

    raw_links = extract_links(all_texts)
    logger.info("Extracted %d raw links", len(raw_links))

    parsed: list = []
    parse_failures = 0
    for link in raw_links:
        cfg = parse_link(link)
        if cfg is not None:
            cfg.raw = link
            parsed.append(cfg)
        else:
            parse_failures += 1
    logger.info(
        "Parsed %d configs (%d failures)", len(parsed), parse_failures
    )

    if not parsed:
        logger.warning("No configs parsed. Pipeline complete.")
        return

    normalized = [normalize_config(c) for c in parsed]
    logger.info("Normalized %d configs", len(normalized))

    for cfg in normalized:
        cfg.score = score_config(cfg)
    logger.info("Scored %d configs", len(normalized))

    deduped = deduplicate(normalized)
    logger.info(
        "Deduplicated: %d -> %d", len(normalized), len(deduped)
    )

    health_settings = settings.health
    if health_settings.get("enabled", True):
        sem = asyncio.Semaphore(health_settings.get("concurrency", 20))
        timeout = health_settings.get("tcp_timeout", 3.0)

        async def check_with_sem(cfg) -> None:
            async with sem:
                result = await check_config(cfg, timeout=timeout)
                if not result.alive:
                    cfg.score -= 100
                else:
                    cfg.score += 5

        await asyncio.gather(*[check_with_sem(c) for c in deduped])
        alive_count = sum(1 for c in deduped if c.score > -50)
        logger.info(
            "Health check: %d/%d alive", alive_count, len(deduped)
        )

    for name, filter_func in FILTERS.items():
        filtered = filter_func(deduped)
        generate_outputs(name, filtered)
        logger.info("Output '%s': %d configs", name, len(filtered))

    elapsed = time.monotonic() - start
    logger.info("Pipeline complete in %.2fs", elapsed)
