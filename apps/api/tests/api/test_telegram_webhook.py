import httpx

from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.api.container import Container
from clarion_api.domain.enums import ChannelKind
from clarion_api.services.chat_bot import CLAIM_RECEIVED, STOPPED
from clarion_api.services.subscriptions import address_hash
from tests.conftest import WEBHOOK_SECRET

HEADERS = {"X-Telegram-Bot-Api-Secret-Token": WEBHOOK_SECRET}
CHAT_ID = 555001


def _update(text: str | None, update_id: int = 1) -> dict[str, object]:
    message: dict[str, object] = {"chat": {"id": CHAT_ID}}
    if text is not None:
        message["text"] = text
    return {"update_id": update_id, "message": message}


async def test_webhook_without_the_secret_is_refused(anonymous_client: httpx.AsyncClient) -> None:
    response = await anonymous_client.post("/webhooks/telegram", json=_update("hello"))
    assert response.status_code == 401


async def test_webhook_with_the_wrong_secret_is_refused(
    anonymous_client: httpx.AsyncClient, console: ConsoleChannel
) -> None:
    response = await anonymous_client.post(
        "/webhooks/telegram",
        json=_update("JOIN YORUBA"),
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
    )
    assert response.status_code == 401
    assert console.replies == []


async def test_join_stores_a_hashed_subscriber_with_consent_time(
    anonymous_client: httpx.AsyncClient, container: Container, console: ConsoleChannel
) -> None:
    response = await anonymous_client.post(
        "/webhooks/telegram", json=_update("JOIN YORUBA"), headers=HEADERS
    )
    assert response.status_code == 200
    secret = container.settings.auth_jwt_secret.get_secret_value()
    stored = await container.subscribers.get(
        ChannelKind.TELEGRAM, address_hash(secret, ChannelKind.TELEGRAM, str(CHAT_ID))
    )
    assert stored is not None
    assert stored.language.value == "yo"
    assert stored.consented_at is not None
    assert str(CHAT_ID) not in stored.address_hash
    assert console.replies[-1][0] == str(CHAT_ID)
    assert "yo" in console.replies[-1][1]


async def test_stop_removes_the_subscriber(
    anonymous_client: httpx.AsyncClient, container: Container, console: ConsoleChannel
) -> None:
    await anonymous_client.post("/webhooks/telegram", json=_update("JOIN HAUSA"), headers=HEADERS)
    assert await container.subscribers.count() == 1
    await anonymous_client.post("/webhooks/telegram", json=_update("STOP"), headers=HEADERS)
    assert await container.subscribers.count() == 0
    assert console.replies[-1][1] == STOPPED


async def test_join_without_a_language_asks_for_one(
    anonymous_client: httpx.AsyncClient, container: Container, console: ConsoleChannel
) -> None:
    await anonymous_client.post("/webhooks/telegram", json=_update("JOIN"), headers=HEADERS)
    assert await container.subscribers.count() == 0
    assert "JOIN YORUBA" in console.replies[-1][1]


async def test_claim_goes_through_web_intake_and_reply_is_fixed_text_only(
    anonymous_client: httpx.AsyncClient, container: Container, console: ConsoleChannel
) -> None:
    claim_text = "INEC has released a new 2027 campaign timetable graphic"
    response = await anonymous_client.post(
        "/webhooks/telegram", json=_update(claim_text), headers=HEADERS
    )
    assert response.status_code == 200

    [claim] = await container.claims.list_recent(limit=5)
    assert claim.text == claim_text
    assert claim.submitted_via is ChannelKind.TELEGRAM
    [draft] = await container.messages.list_recent(limit=5)
    assert draft.claim_id == claim.id
    assert draft.review is None

    [(recipient, reply)] = console.replies
    assert recipient == str(CHAT_ID)
    assert reply == CLAIM_RECEIVED
    assert "contradicted" not in reply.lower()
    assert console.sent == []


async def test_update_without_a_message_is_acknowledged(
    anonymous_client: httpx.AsyncClient, console: ConsoleChannel
) -> None:
    response = await anonymous_client.post(
        "/webhooks/telegram", json={"update_id": 9}, headers=HEADERS
    )
    assert response.status_code == 200
    assert console.replies == []


async def test_start_sends_the_welcome(
    anonymous_client: httpx.AsyncClient, console: ConsoleChannel
) -> None:
    await anonymous_client.post("/webhooks/telegram", json=_update("/start"), headers=HEADERS)
    assert "JOIN" in console.replies[-1][1]
