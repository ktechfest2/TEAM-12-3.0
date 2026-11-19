from typing import Protocol


class Cipher(Protocol):
    """Reversible encryption for the few values we must read back (subscriber phone numbers)."""

    def encrypt(self, plain: str) -> str: ...

    def decrypt(self, token: str) -> str:
        """Raise ValueError when the token was not made with this key."""
        ...
