"""SMS through a TextBee gateway: an Android phone you own sends the messages.

Only the numbers in `recipients` are ever messaged. They are people who agreed to
receive test messages (the team's own phones); this adapter never takes a number
from a claim or a subscriber.
"""

import httpx

from clarion_api.domain.enums import ChannelKind

API_URL = "https://api.textbee.dev/api/v1/gateway/send-sms"


class TextBeeChannel:
    kind = ChannelKind.SMS

    def __init__(
        self,
        *,
        api_key: str,
        recipients: list[str],
        client: httpx.AsyncClient,
        device_id: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._recipients = recipients
        self._device_id = device_id
        self._client = client

    async def send_text(self, text: str) -> str:
        """Broadcast to the fixed test numbers from settings."""
        return await self.send_sms(self._recipients, text)

    async def send_sms(self, numbers: list[str], text: str) -> str:
        payload: dict[str, object] = {"recipients": numbers, "message": text}
        if self._device_id:
            payload["deviceId"] = self._device_id
        response = await self._client.post(
            API_URL, json=payload, headers={"x-api-key": self._api_key}, timeout=15.0
        )
        response.raise_for_status()
        data = response.json().get("data", {})
        if data.get("success") is False:
            msg = f"textbee error: {data.get('message', 'unknown')}"
            raise RuntimeError(msg)
        # The gateway accepts a batch; the phone sends it. Acceptance is not delivery.
        return str(data.get("smsBatchId") or "textbee-accepted")
