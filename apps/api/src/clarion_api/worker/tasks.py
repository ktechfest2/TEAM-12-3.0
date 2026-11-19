"""Queued jobs. Each job does one thing and is safe to retry."""

from uuid import UUID

from clarion_api.domain.enums import DeliveryStatus
from clarion_api.observability import get_logger
from clarion_api.services.broadcasting import send_one
from clarion_api.services.messages import load_message
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
