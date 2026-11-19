from clarion_api.domain.enums import ChannelKind


class ConsoleChannel:
    """Records sends in memory. Used in tests and when no real channel is configured."""

    kind = ChannelKind.CONSOLE

    def __init__(self) -> None:
        self.sent: list[str] = []
        self.replies: list[tuple[str, str]] = []
        self.sms: list[tuple[str, str]] = []

    async def send_text(self, text: str) -> str:
        self.sent.append(text)
        return f"console-{len(self.sent)}"

    async def reply(self, recipient: str, text: str) -> str:
        self.replies.append((recipient, text))
        return f"console-reply-{len(self.replies)}"

    async def send_sms(self, numbers: list[str], text: str) -> str:
        self.sms.extend((number, text) for number in numbers)
        return f"console-sms-{len(self.sms)}"
