import re
from datetime import UTC, datetime, timedelta

import pytest

from clarion_api.adapters.channels.console import ConsoleChannel
from clarion_api.adapters.crypto import FernetCipher, generate_key
from clarion_api.domain.enums import DeliveryMode, DigestFrequency, Language, SubscriptionStatus
from clarion_api.domain.errors import InvalidCodeError, InvalidPhoneError, RateLimitedError
from clarion_api.domain.models import SmsPreferences
from clarion_api.repositories.memory import MemorySmsSubscriptionRepository
from clarion_api.services import sms_subscriptions as svc
from clarion_api.services.rate_limit import SlidingWindowLimiter

SECRET = "unit-test-secret"  # noqa: S105
PHONE = "+2348031234567"
NOW = datetime(2026, 11, 19, 9, 0, tzinfo=UTC)
PREFS = SmsPreferences(languages=[Language.YORUBA, Language.ENGLISH], max_per_day=2)


class Kit:
    def __init__(self) -> None:
        self.repo = MemorySmsSubscriptionRepository()
        self.sender = ConsoleChannel()
        self.cipher = FernetCipher(generate_key())

    async def signup(
        self, phone: str = PHONE, prefs: SmsPreferences = PREFS, at: datetime = NOW
    ) -> None:
        await svc.request_signup(
            raw_phone=phone,
            preferences=prefs,
            secret=SECRET,
            cipher=self.cipher,
            sender=self.sender,
            repo=self.repo,
            now=at,
        )

    def last_code(self) -> str:
        match = re.search(r"code: (\d{6})", self.sender.sms[-1][1])
        assert match
        return match.group(1)

    async def confirm(self, code: str, at: datetime = NOW, phone: str = PHONE) -> svc.ConfirmResult:
        return await svc.confirm_code(
            raw_phone=phone, code=code, secret=SECRET, repo=self.repo, now=at
        )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+234 803 123 4567", "+2348031234567"),
        ("08031234567", "+2348031234567"),
        ("2348031234567", "+2348031234567"),
        ("002348031234567", "+2348031234567"),
        ("+44 20 7946 0958", "+442079460958"),
    ],
)
def test_numbers_are_normalised_to_international_format(raw: str, expected: str) -> None:
    assert svc.normalize_phone(raw) == expected


@pytest.mark.parametrize("raw", ["", "hello", "0803", "+0123456789", "12345678901234567890"])
def test_bad_numbers_are_refused(raw: str) -> None:
    with pytest.raises(InvalidPhoneError):
        svc.normalize_phone(raw)


async def test_signup_texts_a_code_and_stays_pending_without_consent() -> None:
    kit = Kit()
    await kit.signup()
    assert kit.sender.sms[0][0] == PHONE
    stored = await kit.repo.get_by_hash(next(iter(kit.repo._items.values())).phone_hash)
    assert stored is not None
    assert stored.status is SubscriptionStatus.PENDING
    assert stored.consented_at is None
    assert await kit.repo.list_active() == []


async def test_the_number_is_stored_encrypted_never_in_plain_text() -> None:
    kit = Kit()
    await kit.signup()
    [stored] = kit.repo._items.values()
    assert PHONE not in stored.model_dump_json()
    assert kit.cipher.decrypt(stored.phone_encrypted) == PHONE


async def test_the_right_code_activates_and_records_consent() -> None:
    kit = Kit()
    await kit.signup()
    result = await kit.confirm(kit.last_code(), at=NOW + timedelta(minutes=1))
    assert result.preferences == PREFS
    [active] = await kit.repo.list_active()
    assert active.consented_at == NOW + timedelta(minutes=1)
    assert active.code_hash is None


async def test_a_wrong_code_is_refused_and_five_wrong_tries_burn_the_code() -> None:
    kit = Kit()
    await kit.signup()
    real = kit.last_code()
    wrong = "000000" if real != "000000" else "111111"
    for _ in range(5):
        with pytest.raises(InvalidCodeError):
            await kit.confirm(wrong)
    with pytest.raises(InvalidCodeError):
        await kit.confirm(real)
    assert await kit.repo.list_active() == []


async def test_an_expired_code_is_refused() -> None:
    kit = Kit()
    await kit.signup()
    with pytest.raises(InvalidCodeError):
        await kit.confirm(kit.last_code(), at=NOW + timedelta(minutes=11))


async def test_a_code_for_an_unknown_number_gives_the_same_refusal() -> None:
    with pytest.raises(InvalidCodeError):
        await Kit().confirm("123456")


async def test_asking_for_codes_too_fast_is_rate_limited() -> None:
    kit = Kit()
    await kit.signup()
    with pytest.raises(RateLimitedError):
        await kit.signup(at=NOW + timedelta(seconds=10))
    await kit.signup(at=NOW + timedelta(seconds=61))


async def test_changing_preferences_needs_a_code_and_changes_nothing_until_then() -> None:
    kit = Kit()
    await kit.signup()
    await kit.confirm(kit.last_code())
    digest = SmsPreferences(
        languages=[Language.HAUSA],
        mode=DeliveryMode.DIGEST,
        digest_frequency=DigestFrequency.WEEKLY,
        max_per_day=1,
    )
    await kit.signup(prefs=digest, at=NOW + timedelta(minutes=5))
    [before] = await kit.repo.list_active()
    assert before.preferences == PREFS  # a stranger typing the number changes nothing
    await kit.confirm(kit.last_code(), at=NOW + timedelta(minutes=6))
    [after] = await kit.repo.list_active()
    assert after.preferences == digest
    assert after.consented_at == before.consented_at


async def test_unsubscribe_needs_a_code_then_deletes_the_number() -> None:
    kit = Kit()
    await kit.signup()
    await kit.confirm(kit.last_code())
    await svc.request_unsubscribe(
        raw_phone=PHONE,
        secret=SECRET,
        sender=kit.sender,
        repo=kit.repo,
        now=NOW + timedelta(minutes=5),
    )
    assert len(await kit.repo.list_active()) == 1  # still subscribed until confirmed
    result = await kit.confirm(kit.last_code(), at=NOW + timedelta(minutes=6))
    assert result.removed
    assert kit.repo._items == {}


async def test_unsubscribing_an_unknown_number_sends_nothing() -> None:
    kit = Kit()
    await svc.request_unsubscribe(
        raw_phone=PHONE, secret=SECRET, sender=kit.sender, repo=kit.repo, now=NOW
    )
    assert kit.sender.sms == []


def test_limiter_blocks_after_the_limit_and_recovers() -> None:
    limiter = SlidingWindowLimiter(limit=2, window=timedelta(hours=1))
    limiter.hit("a", NOW)
    limiter.hit("a", NOW)
    with pytest.raises(RateLimitedError):
        limiter.hit("a", NOW)
    limiter.hit("b", NOW)
    limiter.hit("a", NOW + timedelta(hours=1))
