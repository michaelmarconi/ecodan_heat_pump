class ApiClientException(Exception):  # noqa: D100
    """Exception to indicate a general API error."""


class ApiClientCommunicationException(ApiClientException):
    """Exception to indicate a communication error."""


class ApiClientAuthenticationException(ApiClientException):
    """Exception to indicate an authentication error."""


class UnrecognisedPresetModeException(Exception):
    """Exception to indicate that a preset mode was unrecognised."""
