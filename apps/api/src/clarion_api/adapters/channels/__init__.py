import httpx

from clarion_api.adapters.channels.base import Channel
from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.adapters.channels.telegram import TelegramChannel
from clarion_api.config import Settings


def build_channels(settings: Settings, client: httpx.AsyncClient) -> list[Channel]:
    """Every configured channel. A channel with missing credentials is simply off."""
    if settings.is_test:
        return [ConsoleChannel()]
    channels: list[Channel] = []
    if settings.channel_telegram_bot_token and settings.channel_telegram_chat_id:
        channels.append(
            TelegramChannel(
                bot_token=settings.channel_telegram_bot_token.get_secret_value(),
                chat_id=settings.channel_telegram_chat_id,
                client=client,
            )
        )
    return channels or [ConsoleChannel()]


__all__ = ["Channel", "build_channels"]
