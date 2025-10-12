"""
App-specific error types. The main loop catches these and prints friendly messages.
"""
class DomainError(Exception):
    """Business rule violation."""


class AuthError(DomainError):
    """Unauthorized or not logged in."""


class NotFound(DomainError):
    """Entity not found in repository."""
