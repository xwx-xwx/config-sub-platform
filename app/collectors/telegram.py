from __future__ import annotations
import logging
import os
from typing import Optional

from telethon import TelegramClient
from telethon.errors import FloodWaitError

from app.utils.retry import async_retry

logger = logging.getLogger("config-collector.telegram")


async def collect_from_telegram(
    channels: list[str],
    api_id: Optional[int] = None,
    api_hash: Optional[str] = None,
    session: str = "anon",
    limit: int = 50,
) -> list[str]:
    api_id = api_id or int(os.getenv("TG_API_ID", "0"))
    api_hash = api_hash or os.getenv("TG_API_HASH", "")

    if not api_id or not api_hash:
        logger.warning(
            "Telegram API credentials not configured. "
            "Set TG_API_ID and TG_API_HASH to enable Telegram collection."
        )
        return []

    messages: list[str] = []
    async with TelegramClient(session, api_id, api_hash) as client:
        for channel in channels:
            try:
                entity = await client.get_entity(channel)
                async for msg in client.iter_messages(entity, limit=limit):
                    if msg.text:
                        messages.append(msg.text)
                logger.info("Collected up to %d messages from %s", limit, channel)
            except FloodWaitError as e:
                logger.warning(
                    "Rate limited on %s, waiting %ds", channel, e.seconds
                )
                await async_retry(lambda: None)  # trigger delay
            except Exception as e:
                logger.error("Failed to collect from %s: %s", channel, e)
    return messages
