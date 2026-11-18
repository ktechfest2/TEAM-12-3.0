"""Telegram Bot API over plain HTTPS; no SDK, so nothing to lock in."""

import httpx

from clarion_api.domain.enums import ChannelKind

API_ROOT = "https://api.telegram.org"


class TelegramChannel:
    kind = ChannelKind.TELEGRAM

    def __init__(self, *, bot_token: str, chat_id: str, client: httpx.AsyncClient) -> None:
        self._base = f"{API_ROOT}/bot{bot_token}"
        self._chat_id = chat_id
        self._client = client

    async def send_text(self, text: str) -> str:
        response = await self._client.post(
            f"{self._base}/sendMessage",
            json={"chat_id": self._chat_id, "text": text, "link_preview_options": {}},
            timeout=15.0,
        )
        response.raise_for_status()
        body = response.json()
        if not body.get("ok"):
            msg = f"telegram error: {body.get('description', 'unknown')}"
            raise RuntimeError(msg)
        return str(body["result"]["message_id"])
