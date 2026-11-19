import pytest

from clarion_api.domain.enums import Language
from clarion_api.services.rendering.sms import SmsEncoding, measure
from clarion_api.services.sms_inbox import (
    ALERTS_CLOSED,
    CLAIM_RECEIVED,
    HELP,
    JOIN_HELP,
    NOT_SUBSCRIBED,
    STOPPED,
    joined_text,
    read_text,
)
from clarion_api.services.subscriptions import (
    ClaimText,
    IgnoredMessage,
    JoinCommand,
    StopCommand,
)

REPLIES = [
    HELP,
    JOIN_HELP,
    CLAIM_RECEIVED,
    STOPPED,
    NOT_SUBSCRIBED,
    ALERTS_CLOSED,
    *(joined_text(language, 10) for language in Language),
]


@pytest.mark.parametrize("reply", REPLIES)
def test_every_reply_is_one_plain_text(reply: str) -> None:
    size = measure(reply)
    assert size.encoding is SmsEncoding.GSM7
    assert size.segments == 1


def test_keyword_gate() -> None:
    assert read_text("CLARION INEC moved it", has_subscription=False) == ClaimText("INEC moved it")
    assert read_text("clarion, join hausa", has_subscription=False) == JoinCommand(Language.HAUSA)
    assert read_text("Clarion", has_subscription=False) == IgnoredMessage()
    assert read_text("CLARION STOP", has_subscription=False) == StopCommand()
    assert read_text("STOP", has_subscription=True) == StopCommand()
    assert read_text("STOP", has_subscription=False) is None
    assert read_text("stop calling me please", has_subscription=True) is None
    assert read_text("Clarions are loud", has_subscription=False) is None
    assert read_text("   ", has_subscription=False) is None
