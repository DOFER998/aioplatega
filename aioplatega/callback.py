"""Verification of incoming callbacks.

Platega authenticates a callback by echoing the merchant's own credentials
back in the ``X-MerchantId`` and ``X-Secret`` headers; there is no signature
over the body. Verification is therefore a comparison of two secrets, which
is only safe done in constant time.
"""

from __future__ import annotations

import hmac
import json
from typing import TYPE_CHECKING, Any, Final

from aioplatega.exceptions import PlategaValidationError
from aioplatega.types import CallbackPayload

if TYPE_CHECKING:
    from collections.abc import Mapping

_MERCHANT_HEADERS: Final[tuple[str, ...]] = ("x-merchantid", "x-merchant-id")
"""Spellings of the merchant header seen in the wild.

Some proxies and frameworks re-case or re-hyphenate incoming headers.
"""

_SECRET_HEADER: Final[str] = "x-secret"


def _header(headers: Mapping[str, str], *names: str) -> str:
    lowered = {str(k).lower(): v for k, v in headers.items()}
    for name in names:
        value = lowered.get(name)
        if value:
            return str(value)
    return ""


def _matches(received: str, expected: str) -> bool:
    """Compare two credentials without leaking their contents through timing."""
    if not received:
        return False
    return hmac.compare_digest(received, expected)


def verify_callback(
    headers: Mapping[str, str],
    body: str | bytes,
    *,
    merchant_id: str,
    secret: str,
    model: type[Any] = CallbackPayload,
) -> Any:
    """Authenticate a callback and parse its body.

    Framework-agnostic: pass whatever mapping of headers and raw body your web
    framework exposes.

    Args:
        headers: Request headers. Looked up case-insensitively.
        secret: The API secret to compare the ``X-Secret`` header against.
        merchant_id: The merchant id to compare ``X-MerchantId`` against.
        body: Raw request body, decoded as UTF-8 if given as bytes.
        model: Model to parse the body into. Pass
            :class:`~aioplatega.types.SubscriptionChargeCallback` or
            :class:`~aioplatega.types.SubscriptionStatusCallback` for the
            subscription callbacks, whose fields are PascalCase.

    Returns:
        The parsed callback body, an instance of ``model``.

    Raises:
        PlategaValidationError: If the credentials do not match, or the body is
            empty, malformed, or missing required fields. Never reveals which
            of the two credentials was wrong.

    Example:
        .. code-block:: python

            @app.route("/callback", methods=["POST"])
            def callback():
                try:
                    payload = client.verify_callback(request.headers, request.get_data())
                except PlategaValidationError:
                    return "", 401
                if payload.status == PaymentStatus.CONFIRMED:
                    mark_paid(payload.payload)
                return "", 200
    """
    received_merchant = _header(headers, *_MERCHANT_HEADERS)
    received_secret = _header(headers, _SECRET_HEADER)

    merchant_ok = _matches(received_merchant, merchant_id)
    secret_ok = _matches(received_secret, secret)
    if not (merchant_ok and secret_ok):
        msg = "Callback credentials do not match"
        raise PlategaValidationError(msg)

    text = body.decode("utf-8") if isinstance(body, bytes) else body
    if not text.strip():
        msg = "Callback body is empty"
        raise PlategaValidationError(msg)

    try:
        parsed = json.loads(text)
    except ValueError as exc:
        msg = f"Callback body is not valid JSON: {exc}"
        raise PlategaValidationError(msg) from exc

    try:
        return model.model_validate(parsed)
    except Exception as exc:
        msg = f"Callback body does not match {model.__name__}: {exc}"
        raise PlategaValidationError(msg) from exc
