"""Domain exception classes."""


class KeyNotFoundError(Exception):
    """Raised when an API key is not found."""


class InvalidAPIKeyError(Exception):
    """Raised when an API key is invalid or revoked."""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


class InvalidAuthTokenError(Exception):
    """Raised when a bearer auth token is missing, invalid, or expired."""
