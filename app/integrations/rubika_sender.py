from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SendResult:
    ok: bool
    error: str | None = None


def _build_send_url(token: str, method: str) -> str:
    endpoint = (settings.rubika_send_endpoint or "").strip()
    if not endpoint:
        return ""

    # The shared doc uses these placeholders; keep backward compatibility.
    prepared = endpoint.replace("{TOKEN}", token).replace("{METHOD}", method)
    prepared = prepared.replace("{token}", token).replace("{method}", method)

    # Optional fallback for .format style endpoints.
    if "{" in prepared and "}" in prepared:
        prepared = prepared.format(token=token, method=method)

    if prepared.endswith("/"):
        prepared = prepared.rstrip("/")

    if not prepared.endswith(f"/{method}") and "{METHOD}" not in endpoint and "{method}" not in endpoint:
        prepared = f"{prepared}/{method}"

    return prepared


async def send_text_message(channel_id: str, text: str) -> SendResult:
    """Send a text message through Rubika Bot API.

    If `RUBIKA_BOT_SEND_ENDPOINT` is not set, this returns a successful no-op.
    """
    token = (settings.rubika_bot_token or "").strip()
    method = (settings.rubika_send_method or "sendMessage").strip()

    url = _build_send_url(token=token, method=method)
    if not url:
        logger.info("Rubika send disabled (no endpoint or token). message=%s", text[:80])
        return SendResult(ok=True)

    payload = {
        "chat_id": channel_id,
        "text": text,
    }
    timeout = settings.rubika_send_timeout_seconds

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return SendResult(ok=True)
    except Exception as exc:  # pragma: no cover - integration boundary
        logger.exception("Rubika send failed for channel=%s", channel_id)
        return SendResult(ok=False, error=str(exc))
