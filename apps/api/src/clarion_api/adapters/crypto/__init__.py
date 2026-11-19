from clarion_api.adapters.crypto.base import Cipher
from clarion_api.adapters.crypto.fernet import FernetCipher, generate_key
from clarion_api.config import Settings


def build_cipher(settings: Settings) -> Cipher | None:
    """None means phone subscriptions are switched off (no key set).

    Tests get a throwaway key so the flow can run; real environments must set one.
    """
    if settings.subscriber_encryption_key:
        return FernetCipher(settings.subscriber_encryption_key.get_secret_value())
    if settings.is_test:
        return FernetCipher(generate_key())
    return None


__all__ = ["Cipher", "FernetCipher", "build_cipher", "generate_key"]
