"""Queued jobs. Each job does one thing and is safe to retry."""

from clarion_api.observability import get_logger
from clarion_api.worker.broker import broker

log = get_logger(__name__)


@broker.task(task_name="deliveries.send", retry_on_error=True, max_retries=3)
async def send_delivery(delivery_id: str) -> str:
    # Task T-04: load delivery, message and channel, call services.broadcasting.send_one,
    # persist the receipt and publish a board update.
    log.info("delivery.send.requested", delivery_id=delivery_id)
    return delivery_id
