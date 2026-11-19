import hmac
from typing import Annotated

from fastapi import APIRouter, Header

from clarion_api.api.deps import ContainerDep
from clarion_api.api.schemas import TelegramUpdateIn, WebhookOut
from clarion_api.domain.errors import NotAuthorizedError
from clarion_api.services.chat_bot import handle_chat_message

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


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
