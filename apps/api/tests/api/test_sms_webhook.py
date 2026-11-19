import json
from datetime import UTC, datetime

import httpx
import pytest

from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.adapters.channels.textbee_inbound import TextBeeInboundReader, sign
from clarion_api.api.container import Container
from clarion_api.domain.enums import ChannelKind, Language, SubscriptionStatus
from clarion_api.services.sms_inbox import CLAIM_RECEIVED, STOPPED
from clarion_api.services.subscriptions import address_hash

SECRET = "test-sms-webhook-signing-secret"  # noqa: S105
DEVICE = "device-1"
PHONE = "+2348031234567"


@pytest.fixture
def sms(container: Container) -> ConsoleChannel:
    container.inbound_sms = TextBeeInboundReader(signing_secret=SECRET, device_id=DEVICE)
    assert isinstance(container.sms_sender, ConsoleChannel)
    return container.sms_sender


def _payload(text: str, *, sms_id: str = "sms-1", sender: str = PHONE, **extra: str) -> bytes:
    body = {
        "smsId": sms_id,
        "sender": sender,
        "message": text,
        "deviceId": DEVICE,
        "webhookEvent": "MESSAGE_RECEIVED",
        "receivedAt": "2026-11-20T10:00:00.000Z",
        **extra,
    }
    return json.dumps(body).encode()


async def _send(
    client: httpx.AsyncClient, body: bytes, *, secret: str = SECRET, at: int | None = None
) -> httpx.Response:
    timestamp = at if at is not None else int(datetime.now(UTC).timestamp())
    return await client.post(
        "/webhooks/sms",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Textbee-Signature": sign(secret, timestamp, body),
        },
    )


def _hash(container: Container) -> str:
    secret = container.settings.auth_jwt_secret.get_secret_value()
    return address_hash(secret, ChannelKind.SMS, PHONE)


async def test_switched_off_without_a_signing_secret(
    anonymous_client: httpx.AsyncClient, container: Container
) -> None:
    assert container.inbound_sms is None
    response = await _send(anonymous_client, _payload("CLARION hello"))
    assert response.status_code == 401


async def test_wrong_missing_or_old_signatures_are_refused(
    anonymous_client: httpx.AsyncClient, container: Container, sms: ConsoleChannel
) -> None:
    body = _payload("CLARION INEC moved the election")
    assert (await _send(anonymous_client, body, secret="not-the-secret")).status_code == 401
    old = int(datetime.now(UTC).timestamp()) - 600
    assert (await _send(anonymous_client, body, at=old)).status_code == 401
    unsigned = await anonymous_client.post("/webhooks/sms", content=body)
    assert unsigned.status_code == 401
    assert await container.claims.list_recent(limit=10) == []
    assert sms.sms == []


@pytest.mark.parametrize(
    ("text", "sender"),
    [
        ("Mummy says call her when you are free", PHONE),
        ("Check this out, INEC changed the date", PHONE),
        ("join us for dinner on Sunday", PHONE),
        ("STOP", PHONE),  # not a subscriber, so this is a personal text
        ("Your OTP is 123456", "GTBank"),
        ("CLARION INEC moved the election", "MTN"),  # names are never people
    ],
)
async def test_personal_texts_are_not_stored_or_answered(
    anonymous_client: httpx.AsyncClient,
    container: Container,
    sms: ConsoleChannel,
    text: str,
    sender: str,
) -> None:
    response = await _send(anonymous_client, _payload(text, sender=sender))
    assert response.status_code == 200
    assert await container.claims.list_recent(limit=10) == []
    assert await container.sms_subscriptions.get_by_hash(_hash(container)) is None
    assert sms.sms == []
    assert container.sms_inbox_guard.seen == {}


async def test_claim_is_stored_without_the_sender_and_answered_with_fixed_text(
    anonymous_client: httpx.AsyncClient, container: Container, sms: ConsoleChannel
) -> None:
    claim_text = "INEC has moved the presidential election to March"
    response = await _send(anonymous_client, _payload(f"clarion: {claim_text}"))
    assert response.status_code == 200
    [claim] = await container.claims.list_recent(limit=10)
    assert claim.text == claim_text
    assert claim.submitted_via is ChannelKind.SMS
    assert PHONE not in claim.model_dump_json()
    assert len(await container.messages.list_recent(limit=10)) == 1  # a draft for reviewers
    assert sms.sms == [(PHONE, CLAIM_RECEIVED)]


async def test_a_retried_delivery_is_handled_once(
    anonymous_client: httpx.AsyncClient, container: Container, sms: ConsoleChannel
) -> None:
    body = _payload("CLARION INEC has moved the election", sms_id="same")
    await _send(anonymous_client, body)
    await _send(anonymous_client, body)
    assert len(await container.claims.list_recent(limit=10)) == 1
    assert len(sms.sms) == 1


async def test_join_by_text_is_active_and_encrypted_and_stop_deletes_it(
    anonymous_client: httpx.AsyncClient, container: Container, sms: ConsoleChannel
) -> None:
    await _send(anonymous_client, _payload("Clarion join yoruba", sms_id="a"))
    stored = await container.sms_subscriptions.get_by_hash(_hash(container))
    assert stored is not None
    assert stored.status is SubscriptionStatus.ACTIVE
    assert stored.consented_at is not None
    assert stored.preferences.languages == [Language.YORUBA]
    assert PHONE not in stored.phone_encrypted
    assert "Yoruba" in sms.sms[-1][1]

    await _send(anonymous_client, _payload("CLARION INEC moved the date", sms_id="b"))
    [claim] = await container.claims.list_recent(limit=10)
    assert claim.language is Language.YORUBA

    await _send(anonymous_client, _payload("Stop", sms_id="c"))
    assert await container.sms_subscriptions.get_by_hash(_hash(container)) is None
    assert sms.sms[-1][1] == STOPPED


async def test_other_gateway_events_and_other_devices_are_ignored(
    anonymous_client: httpx.AsyncClient, container: Container, sms: ConsoleChannel
) -> None:
    sent = _payload("CLARION hello", webhookEvent="MESSAGE_SENT")
    other = _payload("CLARION hello", deviceId="someone-else")
    assert (await _send(anonymous_client, sent)).status_code == 200
    assert (await _send(anonymous_client, other)).status_code == 200
    assert sms.sms == []


async def test_a_flood_from_one_number_is_capped(
    anonymous_client: httpx.AsyncClient, container: Container, sms: ConsoleChannel
) -> None:
    for i in range(8):
        await _send(anonymous_client, _payload(f"CLARION rumour number {i}", sms_id=f"f{i}"))
    assert len(await container.claims.list_recent(limit=20)) == 5
    assert len(sms.sms) == 3
