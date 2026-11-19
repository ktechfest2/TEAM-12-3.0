from datetime import UTC, datetime, timedelta

from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.adapters.crypto import FernetCipher, generate_key
from clarion_api.domain.enums import DeliveryMode, DigestFrequency, Language, SubscriptionStatus
from clarion_api.domain.models import MasterMessage, SmsPreferences, SmsSubscription
from clarion_api.repositories.memory import (
    MemoryMessageRepository,
    MemorySmsSubscriptionRepository,
)
from clarion_api.services import sms_dispatch as dispatch
from tests.factories import approved_message

WEB = "https://clarion.test"
PHONE = "+2348031234567"
NOW = datetime(2026, 11, 19, 9, 0, tzinfo=UTC)


class Kit:
    def __init__(self) -> None:
        self.repo = MemorySmsSubscriptionRepository()
        self.messages = MemoryMessageRepository()
        self.sender = ConsoleChannel()
        self.cipher = FernetCipher(generate_key())

    async def add(self, prefs: SmsPreferences, phone: str = PHONE) -> SmsSubscription:
        sub = SmsSubscription(
            phone_hash=f"h-{phone}",
            phone_encrypted=self.cipher.encrypt(phone),
            status=SubscriptionStatus.ACTIVE,
            preferences=prefs,
            consented_at=NOW,
        )
        await self.repo.save(sub)
        return sub

    async def notify(self, message: MasterMessage, at: datetime = NOW) -> int:
        await self.messages.save(message)
        return await dispatch.notify_subscribers(
            message,
            web_url=WEB,
            subscriptions=self.repo,
            cipher=self.cipher,
            sender=self.sender,
            now=at,
        )

    async def flush(self, at: datetime) -> int:
        return await dispatch.flush_due(
            web_url=WEB,
            messages=self.messages,
            subscriptions=self.repo,
            cipher=self.cipher,
            sender=self.sender,
            now=at,
        )

    async def only(self) -> SmsSubscription:
        [sub] = await self.repo.list_active()
        return sub


async def test_instant_subscriber_gets_one_text_in_their_first_language_with_a_link() -> None:
    kit = Kit()
    await kit.add(SmsPreferences(languages=[Language.YORUBA, Language.ENGLISH]))
    message = approved_message()
    assert await kit.notify(message) == 1
    [(number, text)] = kit.sender.sms
    assert number == PHONE
    assert "yo text" in text
    assert f"{WEB}/c/{message.id}" in text
    assert f"{WEB}/subscribe" in text  # how to stop


async def test_a_language_not_yet_approved_falls_back_to_the_next_choice() -> None:
    kit = Kit()
    await kit.add(SmsPreferences(languages=[Language.HAUSA, Language.ENGLISH]))
    await kit.notify(approved_message())
    assert "INEC did not issue this timetable." in kit.sender.sms[0][1]


async def test_a_subscriber_with_no_sendable_language_gets_nothing() -> None:
    kit = Kit()
    await kit.add(SmsPreferences(languages=[Language.HAUSA]))
    assert await kit.notify(approved_message()) == 0
    assert kit.sender.sms == []
    assert (await kit.only()).held_message_ids == []


async def test_an_unapproved_message_is_never_texted() -> None:
    kit = Kit()
    await kit.add(SmsPreferences(languages=[Language.ENGLISH]))
    unsealed = approved_message(integrity_hash=None)
    assert await kit.notify(unsealed) == 0
    assert kit.sender.sms == []


async def test_the_daily_cap_is_a_hard_limit_and_extra_corrections_are_held() -> None:
    kit = Kit()
    await kit.add(SmsPreferences(languages=[Language.ENGLISH], max_per_day=2))
    messages = [approved_message() for _ in range(4)]
    for index, message in enumerate(messages):
        await kit.notify(message, at=NOW + timedelta(minutes=index))
    assert len(kit.sender.sms) == 2
    sub = await kit.only()
    assert sub.held_message_ids == [messages[2].id, messages[3].id]
    # still the same day: nothing more is sent however often we check
    assert await kit.flush(NOW + timedelta(hours=5)) == 0
    assert len(kit.sender.sms) == 2


async def test_held_corrections_go_out_in_one_text_when_a_new_day_starts() -> None:
    kit = Kit()
    await kit.add(SmsPreferences(languages=[Language.ENGLISH], max_per_day=1))
    for index in range(3):
        await kit.notify(approved_message(), at=NOW + timedelta(minutes=index))
    assert len(kit.sender.sms) == 1
    # 09:00 UTC is 10:00 in Lagos; the next Lagos day starts at 23:00 UTC
    assert await kit.flush(NOW + timedelta(hours=14, minutes=1)) == 1
    assert len(kit.sender.sms) == 2
    assert kit.sender.sms[1][1].count(f"{WEB}/c/") == 2
    assert (await kit.only()).held_message_ids == []


async def test_digest_subscribers_wait_for_their_interval_and_get_one_text() -> None:
    kit = Kit()
    await kit.add(
        SmsPreferences(
            languages=[Language.ENGLISH],
            mode=DeliveryMode.DIGEST,
            digest_frequency=DigestFrequency.HOURLY,
            max_per_day=5,
        )
    )
    first, second = approved_message(), approved_message()
    assert await kit.notify(first, at=NOW) == 0
    assert await kit.notify(second, at=NOW + timedelta(minutes=10)) == 0
    assert kit.sender.sms == []
    assert await kit.flush(NOW + timedelta(minutes=30)) == 1  # never texted: first digest is due
    assert kit.sender.sms[0][1].count(f"{WEB}/c/") == 2
    third = approved_message()
    await kit.notify(third, at=NOW + timedelta(minutes=40))
    assert await kit.flush(NOW + timedelta(minutes=50)) == 0  # under an hour since the last text
    assert await kit.flush(NOW + timedelta(minutes=95)) == 1


async def test_the_same_message_is_never_texted_twice() -> None:
    kit = Kit()
    await kit.add(SmsPreferences(languages=[Language.ENGLISH], max_per_day=5))
    message = approved_message()
    await kit.notify(message)
    await kit.notify(message, at=NOW + timedelta(minutes=1))
    assert len(kit.sender.sms) == 1


async def test_a_failed_send_holds_the_message_instead_of_losing_it() -> None:
    class Broken(ConsoleChannel):
        async def send_sms(self, numbers: list[str], text: str) -> str:
            msg = "gateway offline"
            raise RuntimeError(msg)

    kit = Kit()
    kit.sender = Broken()
    await kit.add(SmsPreferences(languages=[Language.ENGLISH], max_per_day=5))
    message = approved_message()
    assert await kit.notify(message) == 0
    assert (await kit.only()).held_message_ids == [message.id]
