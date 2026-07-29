"""PG-HMAC request signing for the Payout API.

The Payout API does not use the ``X-MerchantId``/``X-Secret`` pair the rest of
the API uses. Every request carries an HMAC-SHA256 signature over a canonical
string, and the server only accepts timestamps within a +/-300 second window.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any, Final

EMPTY_BODY_SHA256: Final[str] = hashlib.sha256(b"").hexdigest()
"""SHA-256 of an empty body, used for GET requests."""

TIMESTAMP_WINDOW_SECONDS: Final[int] = 300
"""How far the server tolerates the client's clock being off."""


def serialize_body(body: dict[str, Any] | None) -> bytes:
    """Serialize a request body to the exact bytes that get signed.

    Args:
        body: The body to serialize, or ``None`` for a bodiless request.

    Returns:
        Compact UTF-8 JSON, or empty bytes when there is no body.

    Note:
        The separators matter. The signature covers these bytes, so the same
        buffer has to reach the socket; re-encoding the dict at send time
        could introduce whitespace and invalidate the signature.
    """
    if body is None:
        return b""
    return json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def build_string_to_sign(
    method: str,
    path: str,
    timestamp: int,
    idempotency_key: str,
    body: bytes,
) -> str:
    """Assemble the canonical string that gets signed.

    Args:
        method: HTTP verb, upper-cased into the string.
        path: Request path, without the host or query string.
        timestamp: Unix time in seconds. The server accepts a window of
            +/-300 seconds around its own clock.
        idempotency_key: Reuse-protection key. Empty for reads, which still
            contribute an empty line to the string.
        body: The exact bytes of the request body.

    Returns:
        The five elements joined by newlines.
    """
    return "\n".join(
        [
            method.upper(),
            path,
            str(timestamp),
            idempotency_key,
            hashlib.sha256(body).hexdigest(),
        ]
    )


def sign(secret: str, string_to_sign: str) -> str:
    """Sign a canonical string.

    Args:
        secret: The Payout API secret.
        string_to_sign: Output of :func:`build_string_to_sign`.

    Returns:
        Base64 of ``HMAC-SHA256(secret, string_to_sign)``.
    """
    digest = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("ascii")


def authorization_header(merchant_id: str, timestamp: int, signature: str) -> str:
    """Render the ``Authorization`` header value.

    Args:
        merchant_id: Merchant identifier, sent as ``kid``.
        timestamp: The same timestamp that went into the signature.
        signature: Output of :func:`sign`.

    Returns:
        A ``PG-HMAC kid=..., ts=..., sig=...`` header value.
    """
    return f"PG-HMAC kid={merchant_id}, ts={timestamp}, sig={signature}"
