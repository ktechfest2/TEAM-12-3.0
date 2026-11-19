import pytest

from clarion_api.domain.enums import ChannelKind, Language
from clarion_api.repositories.memory import MemorySubscriberRepository
from clarion_api.services.subscriptions import (
    ClaimText,
    IgnoredMessage,
    JoinCommand,
    StopCommand,
    address_hash,
    join,
    leave,
    parse_command,
)

SECRET = "hash-secret"  # noqa: S105


@pytest.mark.parametrize(
    ("raw", "language"),
    [
        ("JOIN YORUBA", Language.YORUBA),
        ("join hausa", Language.HAUSA),
        ("/join Igbo", Language.IGBO),
        ("Join pidgin", Language.PIDGIN),
        ("JOIN pcm", Language.PIDGIN),
        ("/join@ClarionBot english", Language.ENGLISH),
    ],
)
def test_join_reads_the_language(raw: str, language: Language) -> None:
    assert parse_command(raw) == JoinCommand(language=language)


@pytest.mark.parametrize("raw", ["JOIN", "join klingon", "/join "])
def test_join_without_a_known_language_asks_again(raw: str) -> None:
    assert parse_command(raw) == JoinCommand(language=None)


@pytest.mark.parametrize("raw", ["STOP", "stop", "/stop", " Stop "])
def test_stop_is_recognised(raw: str) -> None:
    assert parse_command(raw) == StopCommand()


def test_anything_else_is_a_claim() -> None:
    text = "INEC said voting moves to Sunday"
    assert parse_command(text) == ClaimText(text=text)


@pytest.mark.parametrize("raw", [None, "", "   ", "/start"])
def test_empty_and_start_are_ignored(raw: str | None) -> None:
    assert parse_command(raw) == IgnoredMessage()


def test_address_hash_hides_the_address_and_depends_on_the_key() -> None:
    hashed = address_hash(SECRET, ChannelKind.TELEGRAM, "123456789")
    assert "123456789" not in hashed
    assert hashed == address_hash(SECRET, ChannelKind.TELEGRAM, "123456789")
    assert hashed != address_hash("other", ChannelKind.TELEGRAM, "123456789")
    assert hashed != address_hash(SECRET, ChannelKind.SMS, "123456789")


async def test_join_records_consent_time_and_joining_twice_updates_the_language() -> None:
    repo = MemorySubscriberRepository()
    first = await join(
        secret=SECRET,
        channel=ChannelKind.TELEGRAM,
        address="42",
        language=Language.YORUBA,
        subscribers=repo,
    )
    again = await join(
        secret=SECRET,
        channel=ChannelKind.TELEGRAM,
        address="42",
        language=Language.HAUSA,
        subscribers=repo,
    )
    assert await repo.count() == 1
    assert again.language is Language.HAUSA
    assert again.consented_at == first.consented_at


async def test_leave_removes_the_subscriber_and_reports_when_none_existed() -> None:
    repo = MemorySubscriberRepository()
    await join(
        secret=SECRET,
        channel=ChannelKind.TELEGRAM,
        address="42",
        language=Language.IGBO,
        subscribers=repo,
    )
    assert await leave(secret=SECRET, channel=ChannelKind.TELEGRAM, address="42", subscribers=repo)
    assert not await leave(
        secret=SECRET, channel=ChannelKind.TELEGRAM, address="42", subscribers=repo
    )
    assert await repo.count() == 0
