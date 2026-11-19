class DomainError(Exception):
    """Base for rule violations. API maps these to 4xx responses."""


class NotPublishableError(DomainError):
    """Raised when something tries to broadcast a message that fails the publish rules."""


class NotFoundError(DomainError):
    """Raised when an id does not match any stored record."""
