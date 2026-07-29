"""Client for the Payout API, which authenticates with PG-HMAC.

Kept separate from :class:`~aioplatega.Platega` on purpose: the two share a
host but nothing else. Payouts are signed with a secret the merchant holds
alone, every write is idempotency-keyed, and the signed bytes have to reach
the socket unchanged — none of which the header-pair auth needs.

Payouts are off by default on a Platega account and enabled on request.
"""

from __future__ import annotations

import asyncio
import ssl
import time
import uuid
from typing import TYPE_CHECKING, Any, Final

import certifi
from aiohttp import ClientError, ClientSession, TCPConnector

from aioplatega.exceptions import ClientDecodeError, PlategaAPIError, PlategaNetworkError
from aioplatega.session.aiohttp import USER_AGENT
from aioplatega.session.base import API_URL
from aioplatega.session.errors import HTTP_CLIENT_ERROR, raise_for_status
from aioplatega.types import CardPayoutRequest, CardPayoutResponse, SavedCardsResponse

from .signing import authorization_header, build_string_to_sign, serialize_body, sign

if TYPE_CHECKING:
    from types import TracebackType

_NETWORK_ERRORS: Final[tuple[type[BaseException], ...]] = (
    ClientError,
    asyncio.TimeoutError,
    OSError,
)

_CARDS_PATH: Final[str] = "/api/v1/cards"
_CARD_PAYOUT_PATH: Final[str] = "/api/v1/payouts/card-rub"

MIN_PAYOUT_RUB: Final[int] = 1000
MAX_PAYOUT_RUB: Final[int] = 87500


class PayoutClient:
    """Async client for the Platega Payout API.

    Example:
        .. code-block:: python

            async with PayoutClient(merchant_id="...", secret="...") as payouts:
                cards = await payouts.get_cards()
                result = await payouts.create_card_payout(
                    card_id=cards[0].card_id,
                    amount_rub=1500,
                )
    """

    def __init__(
        self,
        merchant_id: str,
        secret: str,
        api_url: str = API_URL,
    ) -> None:
        """Initialize the Payout client.

        Args:
            merchant_id: Your Platega merchant identifier, sent as ``kid``.
            secret: The Payout API secret. This is *not* the ``X-Secret`` used
                by :class:`~aioplatega.Platega`; it is issued separately, shown
                once, and Platega cannot recover it.
            api_url: Override the API base URL.
        """
        self._merchant_id = merchant_id
        self._secret = secret
        self._api_url = api_url.rstrip("/")
        self._session: ClientSession | None = None

    def _get_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            connector = TCPConnector(ssl=ssl.create_default_context(cafile=certifi.where()))
            self._session = ClientSession(connector=connector)
        return self._session

    async def _request(
        self,
        http_method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        idempotency_key: str = "",
    ) -> Any:
        """Sign a request and send it.

        Args:
            http_method: HTTP verb, contributed to the signature.
            path: Request path, contributed to the signature.
            body: JSON body, or ``None`` for a bodiless request.
            params: Query parameters, which are not signed.
            idempotency_key: Reuse-protection key, empty for reads.

        Returns:
            The decoded JSON response.

        Raises:
            PlategaNetworkError: If the request never reached the server.
            PlategaAPIError: If the server reported a failure.
            ClientDecodeError: If a successful response was not valid JSON.

        Note:
            The body is passed as ``data`` rather than ``json`` so the exact
            bytes that were signed reach the socket. Handing aiohttp the dict
            would let it re-encode, and the signature would no longer match.
        """
        session = self._get_session()
        payload = serialize_body(body)
        timestamp = int(time.time())

        signature = sign(
            self._secret,
            build_string_to_sign(http_method, path, timestamp, idempotency_key, payload),
        )
        headers = {
            "Authorization": authorization_header(self._merchant_id, timestamp, signature),
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        if body is not None:
            headers["Content-Type"] = "application/json"

        try:
            response = await session.request(
                http_method,
                f"{self._api_url}{path}",
                data=payload if body is not None else None,
                params=params,
                headers=headers,
            )
        except _NETWORK_ERRORS as exc:
            raise PlategaNetworkError(str(exc)) from exc

        return await self._parse(response, path)

    @staticmethod
    async def _parse(response: Any, path: str) -> Any:
        status = response.status
        try:
            parsed = await response.json()
        except Exception as decode_exc:
            text = await response.text()
            if status >= HTTP_CLIENT_ERROR:
                raise PlategaAPIError(
                    message=text,
                    method=path,
                    status_code=status,
                    body=text,
                ) from decode_exc
            raise ClientDecodeError(
                f"Failed to decode response from {path}: {text}"
            ) from decode_exc

        raise_for_status(status, parsed, path)
        return parsed

    async def get_cards(self, *, only_active: bool = True) -> SavedCardsResponse:
        """List the merchant's saved payout cards.

        Args:
            only_active: When ``False``, also returns ``DISABLED`` and
                ``PENDING`` cards.

        Returns:
            An iterable of :class:`~aioplatega.types.SavedCard`.
        """
        params = {"onlyActive": "true" if only_active else "false"}
        body = await self._request("GET", _CARDS_PATH, params=params)
        try:
            return SavedCardsResponse.model_validate(body)
        except Exception as exc:
            raise ClientDecodeError(f"Failed to parse response from {_CARDS_PATH}: {exc}") from exc

    async def create_card_payout(
        self,
        *,
        amount_rub: int,
        card_id: str | None = None,
        card_number: str | None = None,
        idempotency_key: str | None = None,
    ) -> CardPayoutResponse:
        """Pay out to a RUB card.

        Args:
            amount_rub: Amount in whole roubles, between 1000 and 87500.
            card_id: A saved card's id. Mutually exclusive with ``card_number``.
            card_number: A full 16-digit PAN. Mutually exclusive with ``card_id``.
            idempotency_key: Reuse-protection key. Generated per call if
                omitted — pass your own to make a retry safe.

        Returns:
            The created payout, with status ``CREATED``.

        Raises:
            ValueError: If the card arguments or the amount are unusable.
                Checked here rather than at the API, because a payout that
                gets sent twice cannot be taken back.
        """
        if (card_id is None) == (card_number is None):
            msg = "Pass exactly one of card_id or card_number"
            raise ValueError(msg)
        if not MIN_PAYOUT_RUB <= amount_rub <= MAX_PAYOUT_RUB:
            msg = (
                f"amount_rub must be between {MIN_PAYOUT_RUB} and "
                f"{MAX_PAYOUT_RUB}, got {amount_rub}"
            )
            raise ValueError(msg)

        request = CardPayoutRequest(
            card_id=card_id,
            card_number=card_number,
            amount_rub=amount_rub,
        )
        body = await self._request(
            "POST",
            _CARD_PAYOUT_PATH,
            body=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            idempotency_key=idempotency_key or str(uuid.uuid4()),
        )
        try:
            return CardPayoutResponse.model_validate(body)
        except Exception as exc:
            raise ClientDecodeError(
                f"Failed to parse response from {_CARD_PAYOUT_PATH}: {exc}"
            ) from exc

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> PayoutClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()
