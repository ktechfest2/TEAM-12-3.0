"""Signed reviewer tokens (HS256 JWT, built from the standard library).

A token proves that someone presented a valid invite code. The subject is the
reviewer's name; it is what the audit trail records as the approver.
"""

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta

from clarion_api.domain.errors import NotAuthorizedError

_HEADER = {"alg": "HS256", "typ": "JWT"}


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sign(secret: str, signing_input: str) -> str:
    mac = hmac.new(secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256)
    return _b64(mac.digest())


def issue_token(secret: str, subject: str, *, now: datetime, ttl: timedelta) -> str:
    claims = {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + ttl).timestamp())}
    parts = [
        _b64(json.dumps(_HEADER, separators=(",", ":")).encode()),
        _b64(json.dumps(claims, separators=(",", ":")).encode()),
    ]
    signing_input = ".".join(parts)
    return f"{signing_input}.{_sign(secret, signing_input)}"


def verify_token(secret: str, token: str, *, now: datetime) -> str:
    """Return the subject, or raise NotAuthorizedError for any bad, forged or expired token."""
    try:
        header_part, claims_part, signature = token.split(".")
        expected = _sign(secret, f"{header_part}.{claims_part}")
        if not hmac.compare_digest(signature, expected):
            raise NotAuthorizedError("token signature is not valid")
        if json.loads(_unb64(header_part)) != _HEADER:
            raise NotAuthorizedError("token header is not supported")
        claims = json.loads(_unb64(claims_part))
        subject = claims["sub"]
        expires = claims["exp"]
    except NotAuthorizedError:
        raise
    except (ValueError, KeyError, TypeError) as exc:
        raise NotAuthorizedError("token is malformed") from exc
    if not isinstance(subject, str) or not subject or int(now.timestamp()) >= int(expires):
        raise NotAuthorizedError("token has expired")
    return subject


def invite_code_matches(expected: str | None, presented: str) -> bool:
    if not expected:
        return False
    return hmac.compare_digest(expected.encode("utf-8"), presented.encode("utf-8"))
