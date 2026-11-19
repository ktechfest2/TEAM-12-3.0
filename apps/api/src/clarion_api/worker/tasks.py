"""Queued jobs. Each job does one thing and is safe to retry."""

import asyncio
from contextlib import suppress
from uuid import UUID

from taskiq import TaskiqEvents, TaskiqState

from clarion_api.domain.enums import DeliveryStatus
from clarion_api.observability import get_logger
from clarion_api.services.broadcasting import send_one
from clarion_api.services.messages import load_message
from clarion_api.services.sms_dispatch import flush_due, notify_subscribers
from clarion_api.worker.broker import broker
from clarion_api.worker.runtime import worker_container

log = get_logger(__name__)


@broker.task(task_name="deliveries.send", retry_on_error=True, max_retries=3)
async def send_delivery(delivery_id: str) -> str:
    """Send one delivery. Only a delivery still `queued` is sent, so a retry never double sends."""
    container = worker_container()
    delivery = await container.deliveries.get(UUID(delivery_id))
    if delivery is None:
        log.warning("delivery.send.missing", delivery_id=delivery_id)
        return "missing"
    if delivery.status is not DeliveryStatus.QUEUED:
        log.info("delivery.send.skipped", delivery_id=delivery_id, status=delivery.status.value)
        return delivery.status.value

    channel = next((c for c in container.channels if c.kind is delivery.channel), None)
    if channel is None:
        failed = delivery.model_copy(
            update={"status": DeliveryStatus.FAILED, "error": "channel is not configured"}
        )
        await container.deliveries.save(failed)
        return failed.status.value

    message = await load_message(delivery.message_id, container.messages)
    public_url = f"{container.settings.public_web_url}/c/{message.id}"
    result = await send_one(message, delivery, channel, public_url)
    await container.deliveries.save(result)
    log.info(
        "delivery.send.finished",
        delivery_id=delivery_id,
        channel=delivery.channel.value,
        status=result.status.value,
    )
    return result.status.value


@broker.task(task_name="subscribers.notify", retry_on_error=False)
async def notify_phone_subscribers(message_id: str) -> int:
    """Text a newly broadcast correction to phone subscribers.

    Not retried: a retry could text someone twice, and anything that failed is already
    held for the next digest."""
    container = worker_container()
    if container.cipher is None:
        return 0
    message = await load_message(UUID(message_id), container.messages)
    return await notify_subscribers(
        message,
        web_url=container.settings.public_web_url,
        subscriptions=container.sms_subscriptions,
        cipher=container.cipher,
        sender=container.sms_sender,
    )


@broker.task(task_name="subscribers.flush", retry_on_error=False)
async def flush_phone_digests() -> int:
    """Send held corrections to subscribers whose digest or daily cap window has opened."""
    container = worker_container()
    if container.cipher is None:
        return 0
    return await flush_due(
        web_url=container.settings.public_web_url,
        messages=container.messages,
        subscriptions=container.sms_subscriptions,
        cipher=container.cipher,
        sender=container.sms_sender,
    )


FLUSH_EVERY_SECONDS = 60
_flush_loop: asyncio.Task[None] | None = None


async def _flush_forever() -> None:
    while True:
        await asyncio.sleep(FLUSH_EVERY_SECONDS)
        try:
            await flush_phone_digests()
        except Exception:
            log.exception("subscribers.flush.failed")


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def start_digest_loop(_: TaskiqState) -> None:
    """Check digests once a minute inside the worker, so no separate scheduler is needed.

    Run one worker process: two would each flush (the daily cap holds, but texts could double).
    """
    global _flush_loop  # noqa: PLW0603 - one loop per worker process
    if _flush_loop is None:
        _flush_loop = asyncio.create_task(_flush_forever())


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def stop_digest_loop(_: TaskiqState) -> None:
    global _flush_loop  # noqa: PLW0603
    if _flush_loop is not None:
        _flush_loop.cancel()
        with suppress(asyncio.CancelledError):
            await _flush_loop
        _flush_loop = None
