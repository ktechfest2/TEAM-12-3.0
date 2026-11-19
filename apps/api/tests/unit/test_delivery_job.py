from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.api.container import Container, build_container
from clarion_api.config import AppEnv, Settings
from clarion_api.domain.enums import ChannelKind, DeliveryStatus, Language
from clarion_api.domain.models import Delivery
from clarion_api.worker.runtime import use_container
from clarion_api.worker.tasks import send_delivery
from tests.factories import approved_message


def _container() -> Container:
    return build_container(Settings(app_env=AppEnv.TEST, _env_file=None))  # type: ignore[call-arg]


async def _queued(container: Container) -> Delivery:
    message = approved_message()
    await container.messages.save(message)
    delivery = Delivery(
        message_id=message.id, channel=ChannelKind.CONSOLE, language=Language.ENGLISH
    )
    await container.deliveries.save(delivery)
    return delivery


async def test_job_sends_once_and_stores_the_receipt() -> None:
    container = _container()
    use_container(container)
    try:
        delivery = await _queued(container)
        assert await send_delivery(str(delivery.id)) == "sent"
        saved = await container.deliveries.get(delivery.id)
        assert saved is not None
        assert saved.status is DeliveryStatus.SENT
        assert saved.external_id == "console-1"
    finally:
        use_container(None)
        await container.aclose()


async def test_running_the_job_twice_sends_only_once() -> None:
    container = _container()
    use_container(container)
    try:
        delivery = await _queued(container)
        await send_delivery(str(delivery.id))
        assert await send_delivery(str(delivery.id)) == "sent"
        [channel] = container.channels
        assert isinstance(channel, ConsoleChannel)
        assert len(channel.sent) == 1
    finally:
        use_container(None)
        await container.aclose()


async def test_job_for_missing_delivery_does_nothing() -> None:
    container = _container()
    use_container(container)
    try:
        assert await send_delivery("00000000-0000-0000-0000-000000000000") == "missing"
    finally:
        use_container(None)
        await container.aclose()
