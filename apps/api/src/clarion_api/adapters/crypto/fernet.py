"""Fernet (AES 128 CBC plus HMAC) from the `cryptography` package."""

from cryptography.fernet import Fernet, InvalidToken


class FernetCipher:
    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode("ascii"))

    def encrypt(self, plain: str) -> str:
        return self._fernet.encrypt(plain.encode("utf-8")).decode("ascii")

    def decrypt(self, token: str) -> str:
        try:
            return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")
        except InvalidToken as exc:
            msg = "value was not encrypted with the configured key"
            raise ValueError(msg) from exc


def generate_key() -> str:
    return Fernet.generate_key().decode("ascii")
