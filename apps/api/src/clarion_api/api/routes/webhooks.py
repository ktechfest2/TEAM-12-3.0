import hmac
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Header, Request

from clarion_api.api.deps import ContainerDep
from clarion_api.api.schemas import TelegramUpdateIn, WebhookOut
from clarion_api.domain.errors import NotAuthorizedError
from clarion_api.observability import get_logger
from clarion_api.services.chat_bot import handle_chat_message
from clarion_api.services.sms_inbox import InboxDeps, handle_inbound_sms

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
log = get_logger(__name__)


@router.post("/telegram", operation_id="receiveTelegramUpdate")
async def receive_telegram_update(
    update: TelegramUpdateIn,
    container: ContainerDep,
    secret_token: Annotated[str | None, Header(alias="X-Telegram-Bot-Api-Secret-Token")] = None,
) -> WebhookOut:
    """Telegram calls this for every message sent to the bot.

    Always answers 200 for updates we choose to ignore, so Telegram does not retry them.
    """
    expected = container.settings.channel_telegram_webhook_secret
    if expected is None or secret_token is None:
        msg = "telegram webhook is not enabled or the secret header is missing"
        raise NotAuthorizedError(msg)
    if not hmac.compare_digest(expected.get_secret_value().encode(), secret_token.encode()):
        msg = "telegram webhook secret does not match"
        raise NotAuthorizedError(msg)
    if update.message is None:
        return WebhookOut()
    await handle_chat_message(
        update.message.text,
        chat_id=str(update.message.chat.id),
        hash_secret=container.settings.auth_jwt_secret.get_secret_value(),
        replier=container.replier,
        claims=container.claims,
        sources=container.sources,
        messages=container.messages,
        subscribers=container.subscribers,
        llm=container.llm,
    )
    return WebhookOut()


@router.post("/sms", operation_id="receiveSms")
async def receive_sms(request: Request, container: ContainerDep) -> WebhookOut:
    """The SMS gateway calls this for every text its phone receives (ADR 0010).

    The phone is also a personal SIM: texts that do not start with CLARION are dropped
    without being stored, logged or answered. Answers 200 for those, so they are not retried.
    """
    reader = container.inbound_sms
    if reader is None:
        msg = "incoming texts are not enabled"
        raise NotAuthorizedError(msg)
    now = datetime.now(UTC)
    sms = reader.read(await request.body(), request.headers, now)
    if sms is None:
        return WebhookOut()
    outcome = await handle_inbound_sms(
        sms,
        InboxDeps(
            secret=container.settings.auth_jwt_secret.get_secret_value(),
            cipher=container.cipher,
            sender=container.sms_sender,
            claims=container.claims,
            sources=container.sources,
            messages=container.messages,
            subscriptions=container.sms_subscriptions,
            llm=container.llm,
            guard=container.sms_inbox_guard,
        ),
        now,
    )
    log.info("sms_received", outcome=outcome.value)
    return WebhookOut()
