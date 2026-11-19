from collections.abc import Callable

from clarion_api.domain.enums import ChannelKind, DeliveryStatus, Language
from clarion_api.domain.models import Delivery
from clarion_api.repositories.memory import MemoryDeliveryRepository
from clarion_api.services.delivery_stream import DeliveryEvent, stream_delivery_events
from tests.factories import approved_message


def _queued(message_id: object, channel: ChannelKind, language: Language) -> Delivery:
    return Delivery(message_id=message_id, channel=channel, language=language)  # type: ignore[arg-type]


async def _collect(
    repo: MemoryDeliveryRepository,
    message_id: object,
    *,
    on_tick: Callable[[int], object] | None = None,
    **options: float,
) -> list[DeliveryEvent]:
    ticks = 0

    async def fake_sleep(_: float) -> None:
        nonlocal ticks
        ticks += 1
        if on_tick:
            result = on_tick(ticks)
            if hasattr(result, "__await__"):
                await result  # type: ignore[misc]

    return [
        event
        async for event in stream_delivery_events(
            message_id,  # type: ignore[arg-type]
            deliveries=repo,
            sleep=fake_sleep,
            **options,
        )
    ]


async def test_stream_sends_a_snapshot_then_each_receipt_then_done() -> None:
    message = approved_message()
    repo = MemoryDeliveryRepository()
    telegram = _queued(message.id, ChannelKind.TELEGRAM, Language.ENGLISH)
    sms = _queued(message.id, ChannelKind.SMS, Language.ENGLISH)
    await repo.save(telegram)
    await repo.save(sms)

    async def deliver(tick: int) -> None:
        target = telegram if tick == 1 else sms
        await repo.save(
            target.model_copy(update={"status": DeliveryStatus.SENT, "external_id": f"id-{tick}"})
        )

    events = await _collect(repo, message.id, on_tick=deliver)

    assert [e.name for e in events] == ["snapshot", "delivery", "delivery", "done"]
    assert {d.status for d in events[0].deliveries} == {DeliveryStatus.QUEUED}
    assert [e.deliveries[0].channel for e in events[1:3]] == [ChannelKind.TELEGRAM, ChannelKind.SMS]
    assert all(e.deliveries[0].status is DeliveryStatus.SENT for e in events[1:3])


async def test_stream_ends_at_once_when_everything_is_already_sent() -> None:
    message = approved_message()
    repo = MemoryDeliveryRepository()
    await repo.save(
        _queued(message.id, ChannelKind.TELEGRAM, Language.ENGLISH).model_copy(
            update={"status": DeliveryStatus.SENT, "external_id": "1"}
        )
    )
    events = await _collect(repo, message.id)
    assert [e.name for e in events] == ["snapshot", "done"]


async def test_failed_receipts_are_reported_not_hidden() -> None:
    message = approved_message()
    repo = MemoryDeliveryRepository()
    failing = _queued(message.id, ChannelKind.SMS, Language.YORUBA)
    await repo.save(failing)

    async def fail(_: int) -> None:
        await repo.save(failing.model_copy(update={"status": DeliveryStatus.FAILED, "error": "x"}))

    events = await _collect(repo, message.id, on_tick=fail)
    assert [e.name for e in events] == ["snapshot", "delivery", "done"]
    assert events[1].deliveries[0].status is DeliveryStatus.FAILED


async def test_stream_waits_while_there_are_no_deliveries_and_gives_up_after_the_limit() -> None:
    message = approved_message()
    events = await _collect(
        MemoryDeliveryRepository(), message.id, poll_seconds=1.0, ping_seconds=3.0, max_seconds=6.0
    )
    names = [e.name for e in events]
    assert names[0] == "snapshot"
    assert names[-1] == "done"
    assert names.count("ping") == 2


async def test_unchanged_deliveries_are_not_repeated() -> None:
    message = approved_message()
    repo = MemoryDeliveryRepository()
    waiting = _queued(message.id, ChannelKind.TELEGRAM, Language.ENGLISH)
    await repo.save(waiting)

    async def send_on_third_tick(tick: int) -> None:
        if tick == 3:
            await repo.save(waiting.model_copy(update={"status": DeliveryStatus.SENT}))

    events = await _collect(repo, message.id, on_tick=send_on_third_tick)
    assert [e.name for e in events] == ["snapshot", "delivery", "done"]
