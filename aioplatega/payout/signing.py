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

    The separators matter: the signature covers these bytes, so the same
    buffer has to be written to the socket. Re-encoding the dict at send time
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
    """Assemble the canonical string: METHOD, PATH, ts, idempotency key, body hash.

    ``idempotency_key`` is empty for GET requests, which still contributes its
    (empty) line to the string.
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
    """Base64 of HMAC-SHA256(secret, string_to_sign)."""
    digest = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("ascii")


def authorization_header(merchant_id: str, timestamp: int, signature: str) -> str:
    """Render the ``Authorization: PG-HMAC ...`` header value."""
    return f"PG-HMAC kid={merchant_id}, ts={timestamp}, sig={signature}"
