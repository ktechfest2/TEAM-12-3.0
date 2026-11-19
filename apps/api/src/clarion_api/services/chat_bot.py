"""What the bot says and does for each incoming chat message.

Every reply is fixed text written by people. Nothing from the language model
or from an unreviewed draft is ever sent back to a person; only an approved,
sealed correction is shared, and that goes through the broadcast path.
"""

from clarion_api.adapters.channels.base import Replier
from clarion_api.adapters.llm.base import LanguageModel
from clarion_api.domain.enums import ChannelKind, Language
from clarion_api.repositories.base import (
    ClaimRepository,
    MessageRepository,
    SourceRepository,
    SubscriberRepository,
)
from clarion_api.services.intake import submit_claim
from clarion_api.services.messages import create_message
from clarion_api.services.subscriptions import (
    ClaimText,
    IgnoredMessage,
    JoinCommand,
    StopCommand,
    join,
    leave,
    parse_command,
)

WELCOME = (
    "Clarion checks election claims against official statements.\n"
    "Send a claim you saw and we will check it.\n"
    "To get future corrections, send JOIN YORUBA, JOIN HAUSA, JOIN IGBO, JOIN PIDGIN or "
    "JOIN ENGLISH. Send STOP at any time to leave."
)
JOIN_HELP = (
    "Which language do you want? Send JOIN YORUBA, JOIN HAUSA, JOIN IGBO, JOIN PIDGIN or "
    "JOIN ENGLISH."
)
CLAIM_RECEIVED = (
    "Thank you. We received your claim. A reviewer will check it against official statements. "
    "We only share an answer after a person has approved it, and we always show the source."
)
STOPPED = "You have been removed. We will not send you more messages."
NOT_SUBSCRIBED = "You were not subscribed, so there is nothing to remove."


def joined_text(language: Language) -> str:
    return (
        f"You are subscribed to corrections in {language.value}. "
        "We will message you when an official correction is approved. Send STOP to leave."
    )


async def handle_chat_message(
    text: str | None,
    *,
    chat_id: str,
    hash_secret: str,
    replier: Replier,
    claims: ClaimRepository,
    sources: SourceRepository,
    messages: MessageRepository,
    subscribers: SubscriberRepository,
    llm: LanguageModel,
) -> None:
    command = parse_command(text)
    channel = ChannelKind.TELEGRAM

    if isinstance(command, IgnoredMessage):
        await replier.reply(chat_id, WELCOME)
    elif isinstance(command, JoinCommand):
        if command.language is None:
            await replier.reply(chat_id, JOIN_HELP)
            return
        await join(
            secret=hash_secret,
            channel=channel,
            address=chat_id,
            language=command.language,
            subscribers=subscribers,
        )
        await replier.reply(chat_id, joined_text(command.language))
    elif isinstance(command, StopCommand):
        removed = await leave(
            secret=hash_secret, channel=channel, address=chat_id, subscribers=subscribers
        )
        await replier.reply(chat_id, STOPPED if removed else NOT_SUBSCRIBED)
    elif isinstance(command, ClaimText):
        claim, result = await submit_claim(
            command.text,
            language=Language.ENGLISH,
            via=channel,
            claims=claims,
            sources=sources,
            llm=llm,
        )
        # Queue a draft for the reviewers; the person gets only the fixed acknowledgement.
        await create_message(
            claim.id,
            claims=claims,
            sources=sources,
            messages=messages,
            llm=llm,
            result=result,
        )
        await replier.reply(chat_id, CLAIM_RECEIVED)
