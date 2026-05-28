from __future__ import annotations
import base64


def encode_base64_subscription(lines: list[str]) -> str:
    content = "\n".join(lines)
    return base64.b64encode(content.encode()).decode()


def decode_base64_subscription(data: str) -> str:
    try:
        decoded = base64.b64decode(data + "==", validate=False)
        return decoded.decode("utf-8", errors="replace")
    except Exception:
        return ""
