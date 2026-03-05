"""Domain exception classes."""


class ModelNotFoundError(Exception):
    """Raised when a requested model does not exist on HuggingFace."""


class ModelPullError(Exception):
    """Raised when a model cannot be pulled from HuggingFace."""


class GPUUnavailableError(Exception):
    """Raised when no GPU is available on the host."""


class KeyNotFoundError(Exception):
    """Raised when an API key is not found."""


class InvalidAPIKeyError(Exception):
    """Raised when an API key is invalid or revoked."""


class ServedModelNotFoundError(Exception):
    """Raised when a served model record is not found."""


class VLLMError(Exception):
    """Raised when vLLM encounters an error."""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


class InvalidAuthTokenError(Exception):
    """Raised when a bearer auth token is missing, invalid, or expired."""
