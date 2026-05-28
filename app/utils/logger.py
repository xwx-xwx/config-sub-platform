from __future__ import annotations
import logging
import sys

from app.settings import load_settings


def setup_logger(name: str = "config-collector") -> logging.Logger:
    settings = load_settings()
    level = getattr(logging, settings.logging.get("level", "INFO").upper(), logging.INFO)
    fmt = settings.logging.get("format", "simple")

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if fmt == "structured":
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "msg": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name or "config-collector")
