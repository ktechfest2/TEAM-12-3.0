"""Incoming texts from a TextBee gateway, delivered by its signed webhook.

TextBee signs each delivery with HMAC-SHA256 over "<unix seconds>.<raw body>" using the
signing secret we chose when creating the webhook, and sends it as
`X-Textbee-Signature: t=<seconds>,v1=<hex>`. Retries are signed again with a fresh time.
The legacy `X-Signature` header has no timestamp, so it is not accepted.
"""

import hashlib
import hmac
import json
from collections.abc import Mapping
from datetime import datetime

from clarion_api.adapters.channels.base import InboundSms
from clarion_api.domain.errors import NotAuthorizedError

SIGNATURE_HEADER = "x-textbee-signature"
RECEIVED_EVENT = "MESSAGE_RECEIVED"
TOLERANCE_SECONDS = 300


def sign(secret: str, timestamp: int, body: bytes) -> str:
    """The header value TextBee would send. Used to check deliveries, and by tests."""
    mac = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256)
    return f"t={timestamp},v1={mac.hexdigest()}"


def _parts(header: str) -> dict[str, str]:
    parts: dict[str, str] = {}
    for item in header.split(","):
        key, _, value = item.strip().partition("=")
        parts[key] = value
    return parts


class TextBeeInboundReader:
    def __init__(self, *, signing_secret: str, device_id: str | None = None) -> None:
        self._secret = signing_secret
        self._device_id = device_id

    def read(self, body: bytes, headers: Mapping[str, str], now: datetime) -> InboundSms | None:
        self._verify(body, headers, now)
        try:
            payload = json.loads(body)
        except ValueError:
            return None
        if not isinstance(payload, dict) or payload.get("webhookEvent") != RECEIVED_EVENT:
            return None
        if self._device_id and payload.get("deviceId") != self._device_id:
            return None
        message_id, sender, text = (payload.get(k) for k in ("smsId", "sender", "message"))
        if not (isinstance(message_id, str) and isinstance(sender, str) and isinstance(text, str)):
            return None
        return InboundSms(message_id=message_id, sender=sender, text=text)

    def _verify(self, body: bytes, headers: Mapping[str, str], now: datetime) -> None:
        refused = NotAuthorizedError("incoming text signature is missing, wrong or too old")
        header = next((v for k, v in headers.items() if k.lower() == SIGNATURE_HEADER), None)
        if header is None:
            raise refused
        parts = _parts(header)
        try:
            timestamp = int(parts.get("t", ""))
        except ValueError:
            raise refused from None
        if abs(now.timestamp() - timestamp) > TOLERANCE_SECONDS:
            raise refused
        expected = sign(self._secret, timestamp, body)
        given = f"t={timestamp},v1={parts.get('v1', '')}"
        if not hmac.compare_digest(expected.encode(), given.encode()):
            raise refused
