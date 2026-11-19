"""Phone subscriptions: sign up, confirm with a texted code, change or remove.

Rules (ADR 0008): the number is stored encrypted; nothing is active or sent to until the
owner types the code we texted; a requested change waits for a code too, so typing someone
else's number changes nothing. Numbers are never logged.
"""

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from clarion_api.adapters.channels.base import SmsSender
from clarion_api.adapters.crypto import Cipher
from clarion_api.domain.enums import ChannelKind, SubscriptionStatus
from clarion_api.domain.errors import InvalidCodeError, InvalidPhoneError, RateLimitedError
from clarion_api.domain.models import SmsPreferences, SmsSubscription
from clarion_api.repositories.base import SmsSubscriptionRepository
from clarion_api.services.subscriptions import address_hash

CODE_TTL = timedelta(minutes=10)
RESEND_GAP = timedelta(seconds=60)
MAX_ATTEMPTS = 5
E164 = re.compile(r"^\+[1-9]\d{7,14}$")


def normalize_phone(raw: str) -> str:
    """International format. Nigerian local numbers (0803...) become +234803..."""
    digits = re.sub(r"[\s\-().]", "", raw.strip())
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    elif re.fullmatch(r"0\d{10}", digits):
        digits = "+234" + digits[1:]
    elif re.fullmatch(r"234\d{10}", digits):
        digits = "+" + digits
    if not E164.fullmatch(digits):
        msg = "Enter a phone number with the country code, for example +2348031234567."
        raise InvalidPhoneError(msg)
    return digits


def _code_hash(secret: str, subscription_id: object, code: str) -> str:
    mac = hmac.new(secret.encode(), f"sms-code:{subscription_id}:{code}".encode(), hashlib.sha256)
    return mac.hexdigest()


def _new_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


@dataclass(frozen=True)
class ConfirmResult:
    removed: bool
    preferences: SmsPreferences | None


async def _issue_code(
    subscription: SmsSubscription,
    *,
    phone: str,
    secret: str,
    sender: SmsSender,
    repo: SmsSubscriptionRepository,
    now: datetime,
) -> None:
    code = _new_code()
    await sender.send_sms(
        [phone], f"Clarion code: {code}. It expires in 10 minutes. Not you? Ignore this text."
    )
    await repo.save(
        subscription.model_copy(
            update={
                "code_hash": _code_hash(secret, subscription.id, code),
                "code_sent_at": now,
                "code_expires_at": now + CODE_TTL,
                "code_attempts": 0,
            }
        )
    )


def _check_gap(existing: SmsSubscription | None, now: datetime) -> None:
    if existing and existing.code_sent_at and now - existing.code_sent_at < RESEND_GAP:
        msg = "A code was just sent. Wait a minute before asking for another."
        raise RateLimitedError(msg)


async def request_signup(
    *,
    raw_phone: str,
    preferences: SmsPreferences,
    secret: str,
    cipher: Cipher,
    sender: SmsSender,
    repo: SmsSubscriptionRepository,
    now: datetime,
) -> None:
    """Text a code. Preferences take effect only after the code is confirmed."""
    phone = normalize_phone(raw_phone)
    phone_hash = address_hash(secret, ChannelKind.SMS, phone)
    existing = await repo.get_by_hash(phone_hash)
    _check_gap(existing, now)
    subscription = (
        existing.model_copy(update={"requested": preferences, "unsubscribe_requested": False})
        if existing
        else SmsSubscription(
            phone_hash=phone_hash,
            phone_encrypted=cipher.encrypt(phone),
            preferences=preferences,
            requested=preferences,
        )
    )
    await _issue_code(subscription, phone=phone, secret=secret, sender=sender, repo=repo, now=now)


async def request_unsubscribe(
    *,
    raw_phone: str,
    secret: str,
    sender: SmsSender,
    repo: SmsSubscriptionRepository,
    now: datetime,
) -> None:
    """Text a code to confirm removal. An unknown number does nothing, and says nothing."""
    phone = normalize_phone(raw_phone)
    existing = await repo.get_by_hash(address_hash(secret, ChannelKind.SMS, phone))
    if existing is None:
        return
    _check_gap(existing, now)
    marked = existing.model_copy(update={"unsubscribe_requested": True})
    await _issue_code(marked, phone=phone, secret=secret, sender=sender, repo=repo, now=now)


async def confirm_code(
    *,
    raw_phone: str,
    code: str,
    secret: str,
    repo: SmsSubscriptionRepository,
    now: datetime,
) -> ConfirmResult:
    phone = normalize_phone(raw_phone)
    subscription = await repo.get_by_hash(address_hash(secret, ChannelKind.SMS, phone))
    failure = InvalidCodeError("That code is not right or has expired. Ask for a new one.")
    if (
        subscription is None
        or subscription.code_hash is None
        or subscription.code_expires_at is None
        or now > subscription.code_expires_at
        or subscription.code_attempts >= MAX_ATTEMPTS
    ):
        raise failure
    attempted = subscription.model_copy(update={"code_attempts": subscription.code_attempts + 1})
    expected = subscription.code_hash
    if not hmac.compare_digest(expected, _code_hash(secret, subscription.id, code.strip())):
        await repo.save(attempted)
        raise failure
    if subscription.unsubscribe_requested:
        await repo.delete(subscription.id)
        return ConfirmResult(removed=True, preferences=None)
    active = subscription.model_copy(
        update={
            "status": SubscriptionStatus.ACTIVE,
            "preferences": subscription.requested or subscription.preferences,
            "requested": None,
            "consented_at": subscription.consented_at or now,
            "code_hash": None,
            "code_expires_at": None,
            "code_attempts": 0,
        }
    )
    await repo.save(active)
    return ConfirmResult(removed=False, preferences=active.preferences)
