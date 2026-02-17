from __future__ import annotations

from typing import Any


class PlategaError(Exception):
    """Base exception for all aioplatega errors."""


class PlategaAPIError(PlategaError):
    """Error returned by the Platega API."""

    def __init__(
        self,
        message: str,
        method: str | None = None,
        status_code: int | None = None,
        body: Any = None,
    ) -> None:
        self.message = message
        self.method = method
        self.status_code = status_code
        self.body = body
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(message={self.message!r}, "
            f"method={self.method!r}, status_code={self.status_code!r})"
        )


class PlategaBadRequestError(PlategaAPIError):
    """HTTP 400 Bad Request."""


class PlategaUnauthorizedError(PlategaAPIError):
    """HTTP 401 Unauthorized."""


class PlategaForbiddenError(PlategaAPIError):
    """HTTP 403 Forbidden."""


class PlategaNotFoundError(PlategaAPIError):
    """HTTP 404 Not Found."""


class PlategaServerError(PlategaAPIError):
    """HTTP 5xx Server Error."""


class PlategaNetworkError(PlategaError):
    """Network-level error (connection refused, timeout, DNS failure, etc.)."""


class ClientDecodeError(PlategaError):
    """Failed to decode/parse the API response."""
