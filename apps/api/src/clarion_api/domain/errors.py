class DomainError(Exception):
    """Base for rule violations. API maps these to 4xx responses."""


class NotPublishableError(DomainError):
    """Raised when something tries to broadcast a message that fails the publish rules."""


class NotFoundError(DomainError):
    """Raised when an id does not match any stored record."""


class LlmBudgetExceededError(DomainError):
    """Raised before a language model call when the monthly spend cap is reached."""


class NotAuthorizedError(DomainError):
    """Raised when a request has no valid reviewer token or a wrong invite code."""


class RenderError(DomainError):
    """Raised when a rendition cannot be produced, for example audio in the wrong format."""


class InvalidCodeError(DomainError):
    """Raised when a verification code is wrong, expired or out of attempts."""


class RateLimitedError(DomainError):
    """Raised when too many verification codes were requested."""


class FeatureUnavailableError(DomainError):
    """Raised when a feature is switched off in this environment (for example no key set)."""


class InvalidPhoneError(DomainError):
    """Raised when a phone number cannot be read as an international number."""
