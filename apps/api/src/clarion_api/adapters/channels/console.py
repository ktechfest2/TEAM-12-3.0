from clarion_api.domain.enums import ChannelKind


class ConsoleChannel:
    """Records sends in memory. Used in tests and when no real channel is configured."""

    kind = ChannelKind.CONSOLE

    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send_text(self, text: str) -> str:
        self.sent.append(text)
        return f"console-{len(self.sent)}"
