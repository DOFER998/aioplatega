from __future__ import annotations

from typing import Any


class PlategaError(Exception):
    """Base exception for all aioplatega errors."""


class PlategaAPIError(PlategaError):
    """Error returned by the Platega API.

    The API answers failures with an envelope carrying more than a message.
    ``trace_id`` in particular is what Platega support asks for when
    investigating a request.
    """

    def __init__(
        self,
        message: str,
        method: str | None = None,
        status_code: int | None = None,
        body: Any = None,
        *,
        code: str | None = None,
        trace_id: str | None = None,
        errors: list[Any] | None = None,
    ) -> None:
        """Build the error.

        Args:
            message: Human-readable message from the response.
            method: API path the request was sent to.
            status_code: HTTP status code.
            body: Decoded response body, kept whole.
            code: Vendor error code, e.g. ``"Common:VAL_0001"``.
            trace_id: Request identifier to quote to support.
            errors: Per-field failures, each ``{"key": ..., "message": ...}``.
        """
        self.message = message
        self.method = method
        self.status_code = status_code
        self.body = body
        self.code = code
        self.trace_id = trace_id
        self.errors = errors or []
        super().__init__(message)

    def __repr__(self) -> str:
        parts = [
            f"message={self.message!r}",
            f"method={self.method!r}",
            f"status_code={self.status_code!r}",
        ]
        if self.code:
            parts.append(f"code={self.code!r}")
        if self.trace_id:
            parts.append(f"trace_id={self.trace_id!r}")
        if self.errors:
            parts.append(f"errors={self.errors!r}")
        return f"{type(self).__name__}({', '.join(parts)})"


class PlategaBadRequestError(PlategaAPIError):
    """HTTP 400 Bad Request."""


class PlategaUnauthorizedError(PlategaAPIError):
    """HTTP 401 Unauthorized."""


class PlategaForbiddenError(PlategaAPIError):
    """HTTP 403 Forbidden."""


class PlategaNotFoundError(PlategaAPIError):
    """HTTP 404 Not Found."""


class PlategaConflictError(PlategaAPIError):
    """HTTP 409 Conflict."""


class PlategaUnprocessableEntityError(PlategaAPIError):
    """HTTP 422 Unprocessable Entity."""


class PlategaRateLimitError(PlategaAPIError):
    """HTTP 429 Too Many Requests."""


class PlategaServerError(PlategaAPIError):
    """HTTP 5xx Server Error."""


class PlategaNetworkError(PlategaError):
    """Network-level error (connection refused, timeout, DNS failure, etc.)."""


class PlategaValidationError(PlategaError):
    """Invalid arguments — raised before any request is sent."""


class ClientDecodeError(PlategaError):
    """Failed to decode/parse the API response."""
