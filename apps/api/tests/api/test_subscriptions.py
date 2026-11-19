import re

import httpx

from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.api.container import Container
from tests.factories import approved_message

PHONE = "08031234567"
BODY = {"phone": PHONE, "languages": ["yo", "en"], "mode": "instant", "max_per_day": 2}


def _sms(container: Container) -> ConsoleChannel:
    assert isinstance(container.sms_sender, ConsoleChannel)
    return container.sms_sender


def _code(container: Container) -> str:
    match = re.search(r"code: (\d{6})", _sms(container).sms[-1][1])
    assert match
    return match.group(1)


async def test_signup_then_confirm_activates_the_subscription(
    anonymous_client: httpx.AsyncClient, container: Container
) -> None:
    started = await anonymous_client.post("/subscriptions", json=BODY)
    assert started.status_code == 202
    assert started.json() == {"status": "code_sent"}
    assert _sms(container).sms[0][0] == "+2348031234567"
    assert await container.sms_subscriptions.list_active() == []

    confirmed = await anonymous_client.post(
        "/subscriptions/confirm", json={"phone": PHONE, "code": _code(container)}
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "active"
    assert confirmed.json()["preferences"]["max_per_day"] == 2
    assert len(await container.sms_subscriptions.list_active()) == 1


async def test_wrong_code_is_a_400(
    anonymous_client: httpx.AsyncClient, container: Container
) -> None:
    await anonymous_client.post("/subscriptions", json=BODY)
    real = _code(container)
    wrong = "000000" if real != "000000" else "111111"
    response = await anonymous_client.post(
        "/subscriptions/confirm", json={"phone": PHONE, "code": wrong}
    )
    assert response.status_code == 400


async def test_bad_phone_and_out_of_range_limits_are_rejected(
    anonymous_client: httpx.AsyncClient,
) -> None:
    assert (
        await anonymous_client.post("/subscriptions", json={**BODY, "phone": "abc12345"})
    ).status_code == 422
    assert (
        await anonymous_client.post("/subscriptions", json={**BODY, "max_per_day": 50})
    ).status_code == 422
    assert (
        await anonymous_client.post("/subscriptions", json={**BODY, "languages": []})
    ).status_code == 422


async def test_unsubscribe_flow_removes_the_number(
    anonymous_client: httpx.AsyncClient, container: Container
) -> None:
    await anonymous_client.post("/subscriptions", json=BODY)
    await anonymous_client.post(
        "/subscriptions/confirm", json={"phone": PHONE, "code": _code(container)}
    )
    container.code_limiter_per_client._hits.clear()
    sub = (await container.sms_subscriptions.list_active())[0]
    await container.sms_subscriptions.save(sub.model_copy(update={"code_sent_at": None}))
    started = await anonymous_client.post("/subscriptions/unsubscribe", json={"phone": PHONE})
    assert started.status_code == 202
    done = await anonymous_client.post(
        "/subscriptions/confirm", json={"phone": PHONE, "code": _code(container)}
    )
    assert done.json() == {"status": "removed", "preferences": None}
    assert await container.sms_subscriptions.list_active() == []


async def test_unsubscribe_answers_the_same_for_unknown_numbers(
    anonymous_client: httpx.AsyncClient, container: Container
) -> None:
    response = await anonymous_client.post("/subscriptions/unsubscribe", json={"phone": PHONE})
    assert response.status_code == 202
    assert response.json() == {"status": "code_sent"}
    assert _sms(container).sms == []


async def test_a_client_cannot_request_endless_codes(
    anonymous_client: httpx.AsyncClient,
) -> None:
    statuses = [
        (
            await anonymous_client.post(
                "/subscriptions", json={**BODY, "phone": f"+23480312345{n:02d}"}
            )
        ).status_code
        for n in range(7)
    ]
    assert statuses[:5] == [202] * 5
    assert statuses[5:] == [429, 429]


async def test_switched_off_without_an_encryption_key(
    anonymous_client: httpx.AsyncClient, container: Container
) -> None:
    container.cipher = None
    response = await anonymous_client.post("/subscriptions", json=BODY)
    assert response.status_code == 503
    assert _sms(container).sms == []


async def test_a_broadcast_texts_confirmed_subscribers_only_after_approval(
    anonymous_client: httpx.AsyncClient, container: Container
) -> None:
    await anonymous_client.post("/subscriptions", json=BODY)
    await anonymous_client.post(
        "/subscriptions/confirm", json={"phone": PHONE, "code": _code(container)}
    )
    message = approved_message()
    await container.messages.save(message)
    reviewer = await anonymous_client.post(
        "/auth/tokens", json={"invite_code": "test-invite-code", "reviewer_name": "r"}
    )
    headers = {"Authorization": f"Bearer {reviewer.json()['access_token']}"}
    sent_before = len(_sms(container).sms)
    response = await anonymous_client.post(
        f"/messages/{message.id}/broadcast", json={}, headers=headers
    )
    assert response.status_code == 202
    texts = _sms(container).sms[sent_before:]
    assert len(texts) == 1
    assert "yo text" in texts[0][1]
