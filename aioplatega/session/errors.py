"""Mapping HTTP responses onto the exception hierarchy.

Shared by the main session and the Payout API client, which authenticate
differently but report failures identically.
"""

from __future__ import annotations

from typing import Any, Final

from aioplatega.exceptions import (
    PlategaAPIError,
    PlategaBadRequestError,
    PlategaConflictError,
    PlategaForbiddenError,
    PlategaNotFoundError,
    PlategaRateLimitError,
    PlategaServerError,
    PlategaUnauthorizedError,
    PlategaUnprocessableEntityError,
)

STATUS_MAP: Final[dict[int, type[PlategaAPIError]]] = {
    400: PlategaBadRequestError,
    401: PlategaUnauthorizedError,
    403: PlategaForbiddenError,
    404: PlategaNotFoundError,
    409: PlategaConflictError,
    422: PlategaUnprocessableEntityError,
    429: PlategaRateLimitError,
}

HTTP_CLIENT_ERROR: Final[int] = 400
HTTP_SERVER_ERROR: Final[int] = 500


def exception_for_status(status: int) -> type[PlategaAPIError]:
    """Pick the exception class for a status code.

    Codes without a dedicated class fall back to :class:`PlategaServerError`
    for 5xx and the generic :class:`PlategaAPIError` for everything else.
    """
    mapped = STATUS_MAP.get(status)
    if mapped is not None:
        return mapped
    return PlategaServerError if status >= HTTP_SERVER_ERROR else PlategaAPIError


def raise_for_status(status: int, body: Any, method: str) -> None:
    """Raise the matching exception if the status indicates failure."""
    if status < HTTP_CLIENT_ERROR:
        return
    message = body.get("message", "") if isinstance(body, dict) else str(body)
    raise exception_for_status(status)(
        message=message,
        method=method,
        status_code=status,
        body=body,
    )
