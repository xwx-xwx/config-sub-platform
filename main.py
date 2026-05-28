#!/usr/bin/env python3
from __future__ import annotations
import asyncio

from app.pipeline import run_pipeline
from app.utils.logger import setup_logger


def main() -> None:
    setup_logger()
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()
