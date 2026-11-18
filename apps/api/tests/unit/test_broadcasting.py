import pytest

from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.domain.enums import DeliveryStatus, Language
from clarion_api.domain.errors import NotPublishableError
from clarion_api.services.broadcasting import plan_deliveries, send_one
from tests.factories import approved_message


def test_plan_refuses_unreviewed_message() -> None:
    with pytest.raises(NotPublishableError):
        plan_deliveries(approved_message(review=None), [ConsoleChannel()], [Language.ENGLISH])


async def test_send_includes_public_link_and_records_receipt() -> None:
    channel = ConsoleChannel()
    msg = approved_message()
    [delivery] = plan_deliveries(msg, [channel], [Language.YORUBA])
    sent = await send_one(msg, delivery, channel, "https://clarion.example/c/1")
    assert sent.status is DeliveryStatus.SENT
    assert "yo text" in channel.sent[0]
    assert "https://clarion.example/c/1" in channel.sent[0]


class _Broken:
    kind = ConsoleChannel.kind

    async def send_text(self, text: str) -> str:
        raise RuntimeError("provider down")


async def test_failed_channel_is_recorded_not_raised() -> None:
    msg = approved_message()
    [delivery] = plan_deliveries(msg, [_Broken()], [Language.ENGLISH])
    result = await send_one(msg, delivery, _Broken(), "https://x")
    assert result.status is DeliveryStatus.FAILED
    assert result.error == "provider down"
