import httpx

from clarion_api.adapters.channels.base import (
    Channel,
    InboundSms,
    InboundSmsReader,
    Replier,
    SmsSender,
)
from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.adapters.channels.telegram import TelegramChannel
from clarion_api.adapters.channels.textbee import TextBeeChannel
from clarion_api.adapters.channels.textbee_inbound import TextBeeInboundReader
from clarion_api.adapters.channels.x_posts import XChannel
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
    if (
        settings.channel_sms_provider == "textbee"
        and settings.channel_sms_api_key
        and settings.sms_recipients
    ):
        channels.append(
            TextBeeChannel(
                api_key=settings.channel_sms_api_key.get_secret_value(),
                recipients=settings.sms_recipients,
                device_id=settings.channel_sms_device_id,
                client=client,
            )
        )
    if settings.channel_x_access_token:
        channels.append(
            XChannel(access_token=settings.channel_x_access_token.get_secret_value(), client=client)
        )
    return channels or [ConsoleChannel()]


def build_replier(channels: list[Channel]) -> Replier:
    """The first channel that can hold a conversation; the console recorder if none can."""
    for channel in channels:
        if isinstance(channel, Replier):
            return channel
    return ConsoleChannel()


def build_sms_sender(settings: Settings, client: httpx.AsyncClient) -> SmsSender:
    """TextBee when configured (even with no broadcast numbers); the console recorder otherwise."""
    if (
        not settings.is_test
        and settings.channel_sms_provider == "textbee"
        and settings.channel_sms_api_key
    ):
        return TextBeeChannel(
            api_key=settings.channel_sms_api_key.get_secret_value(),
            recipients=[],
            device_id=settings.channel_sms_device_id,
            client=client,
        )
    return ConsoleChannel()


def build_inbound_sms_reader(settings: Settings) -> InboundSmsReader | None:
    """None keeps incoming texts switched off: the webhook then refuses every request."""
    if settings.channel_sms_provider == "textbee" and settings.channel_sms_webhook_secret:
        return TextBeeInboundReader(
            signing_secret=settings.channel_sms_webhook_secret.get_secret_value(),
            device_id=settings.channel_sms_device_id,
        )
    return None


__all__ = [
    "Channel",
    "InboundSms",
    "InboundSmsReader",
    "Replier",
    "SmsSender",
    "build_channels",
    "build_inbound_sms_reader",
    "build_replier",
    "build_sms_sender",
]
