from __future__ import annotations
import logging
from pathlib import Path

from app.models.config import ProxyConfig
from app.settings import load_settings
from app.outputs.base64 import encode_base64_subscription
from app.outputs.clash import generate_clash_config

logger = logging.getLogger("config-collector.outputs")

OUTPUT_DIR = Path("generated")


def _raw_line(cfg: ProxyConfig) -> str:
    return cfg.raw or ""


def generate_outputs(name: str, configs: list[ProxyConfig]) -> None:
    settings = load_settings()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "base64").mkdir(parents=True, exist_ok=True)

    lines = [_raw_line(c) for c in configs if c.raw]

    if settings.output.get("raw", True):
        raw_path = OUTPUT_DIR / f"{name}.txt"
        raw_path.write_text("\n".join(lines))
        logger.info("Generated %s with %d configs", raw_path, len(lines))

    if settings.output.get("base64", True):
        b64_content = encode_base64_subscription(lines)
        b64_path = OUTPUT_DIR / "base64" / f"{name}.txt"
        b64_path.write_text(b64_content)
        logger.info("Generated base64 %s", b64_path)

    if settings.output.get("clash", False):
        clash_yaml = generate_clash_config(name, configs)
        if clash_yaml:
            clash_path = OUTPUT_DIR / f"{name}.yaml"
            clash_path.write_text(clash_yaml)
            logger.info("Generated Clash %s", clash_path)
