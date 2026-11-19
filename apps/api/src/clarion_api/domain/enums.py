from enum import StrEnum


class Verdict(StrEnum):
    """The only three answers Clarion ever gives. Never add opinion values."""

    CONFIRMED = "confirmed"
    CONTRADICTED = "contradicted"
    NO_OFFICIAL_STATEMENT = "no_official_statement"


class Language(StrEnum):
    """ISO 639 codes. Pidgin uses pcm."""

    ENGLISH = "en"
    YORUBA = "yo"
    HAUSA = "ha"
    IGBO = "ig"
    PIDGIN = "pcm"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ChannelKind(StrEnum):
    TELEGRAM = "telegram"
    WEB_FEED = "web_feed"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    X = "x"
    INSTAGRAM = "instagram"
    CONSOLE = "console"


class RenditionFormat(StrEnum):
    TEXT = "text"
    SMS_TEXT = "sms_text"
    VOICE_NOTE = "voice_note"
    RADIO_SCRIPT = "radio_script"
    SOCIAL_CARD = "social_card"
    POSTER_PDF = "poster_pdf"
    SHORT_VIDEO = "short_video"


class DeliveryStatus(StrEnum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    RETRACTED = "retracted"


class SubscriptionStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"


class DeliveryMode(StrEnum):
    INSTANT = "instant"
    DIGEST = "digest"


class DigestFrequency(StrEnum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
