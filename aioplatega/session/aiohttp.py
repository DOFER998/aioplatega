from __future__ import annotations

import asyncio
import ssl
from typing import Any, Final
from urllib.parse import quote

import certifi
from aiohttp import ClientError, ClientSession, TCPConnector

from aioplatega.exceptions import ClientDecodeError, PlategaAPIError, PlategaNetworkError
from aioplatega.methods.base import PlategaMethod

from .base import API_URL, BaseSession
from .errors import HTTP_CLIENT_ERROR, raise_for_status

_NETWORK_ERRORS: Final[tuple[type[BaseException], ...]] = (
    ClientError,
    asyncio.TimeoutError,
    OSError,
)
"""Failures meaning the request never made it there and back.

Anything outside this tuple is a defect in this library and is left to
propagate, rather than being reported as a connectivity problem.
"""


def _build_ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=certifi.where())


class AiohttpSession(BaseSession):
    """``aiohttp``-backed session with lazy connection pool creation."""

    def __init__(self, api_url: str = API_URL) -> None:
        """Initialize the session.

        Args:
            api_url: Override the API base URL.
        """
        self._api_url = api_url
        self._session: ClientSession | None = None

    def _get_session(self) -> ClientSession:
        """Return the pooled session, opening one on first use."""
        if self._session is None or self._session.closed:
            connector = TCPConnector(ssl=_build_ssl_context())
            self._session = ClientSession(connector=connector)
        return self._session

    async def make_request(
        self,
        merchant_id: str,
        secret: str,
        method: PlategaMethod[Any],
    ) -> Any:
        """Execute an API method and return the parsed response.

        Args:
            merchant_id: Merchant identifier, sent as ``X-MerchantId``.
            secret: Secret key, sent as ``X-Secret``.
            method: The method object describing the request.

        Returns:
            An instance of the method's ``__returning__`` model.

        Raises:
            PlategaNetworkError: If the request never reached the server.
            PlategaAPIError: If the server reported a failure.
            ClientDecodeError: If the response could not be parsed into the
                expected model.
        """
        session = self._get_session()

        url, path_fields = self._build_url(method)
        payload = self._build_payload(method, path_fields)
        headers = {
            "X-MerchantId": merchant_id,
            "X-Secret": secret,
        }

        try:
            if method.__http_method__ == "POST":
                response = await session.post(url, json=payload, headers=headers)
            else:
                response = await session.get(
                    url,
                    params=self._to_query(payload),
                    headers=headers,
                )
        except _NETWORK_ERRORS as exc:
            raise PlategaNetworkError(str(exc)) from exc

        return await self._handle_response(response, method)

    def _build_url(self, method: PlategaMethod[Any]) -> tuple[str, frozenset[str]]:
        """Substitute ``{field}`` placeholders into the path.

        Args:
            method: The method object supplying the field values.

        Returns:
            The full URL, and the field names the path consumed so the caller
            can keep them out of the query string or body.
        """
        path = method.__api_method__
        consumed: set[str] = set()

        for key, value in method.model_dump(by_alias=False, exclude_none=True).items():
            placeholder = f"{{{key}}}"
            if placeholder in path:
                path = path.replace(placeholder, quote(str(value), safe=""))
                consumed.add(key)

        return f"{self._api_url}{path}", frozenset(consumed)

    @staticmethod
    def _build_payload(
        method: PlategaMethod[Any],
        path_fields: frozenset[str],
    ) -> dict[str, Any]:
        """Serialize a method to JSON-primitive values, minus the path fields.

        Args:
            method: The method object to serialize.
            path_fields: Field names already consumed by the URL path.

        Returns:
            Alias-keyed values ready for a query string or JSON body.

        Note:
            Serializing in JSON mode matters. A plain dump leaves ``UUID`` and
            ``datetime`` objects in place, which yarl silently coerces -- a
            UUID becomes its 128-bit integer -- and which ``json.dumps``
            rejects outright.
        """
        return method.model_dump(
            mode="json",
            by_alias=True,
            exclude_none=True,
            exclude=set(path_fields),
        )

    @staticmethod
    def _to_query(payload: dict[str, Any]) -> dict[str, str]:
        """Render a payload as query parameters.

        Args:
            payload: Alias-keyed values from :meth:`_build_payload`.

        Returns:
            The same mapping with every value rendered as a string, which is
            what aiohttp accepts.
        """
        query: dict[str, str] = {}
        for key, value in payload.items():
            if value is None:
                continue
            query[key] = str(value).lower() if isinstance(value, bool) else str(value)
        return query

    @staticmethod
    async def _handle_response(
        response: Any,
        method: PlategaMethod[Any],
    ) -> Any:
        """Turn a raw response into the method's model, or an exception.

        Args:
            response: The aiohttp response.
            method: The method object, read for its return model.

        Returns:
            An instance of the method's ``__returning__`` model.

        Raises:
            PlategaAPIError: If the server reported a failure.
            ClientDecodeError: If the body was not valid JSON, or did not fit
                the expected model.
        """
        status = response.status
        api_method = method.__api_method__

        try:
            body = await response.json()
        except Exception as decode_exc:
            text = await response.text()
            if status >= HTTP_CLIENT_ERROR:
                raise PlategaAPIError(
                    message=text,
                    method=api_method,
                    status_code=status,
                    body=text,
                ) from decode_exc
            raise ClientDecodeError(
                f"Failed to decode response from {api_method}: {text}"
            ) from decode_exc

        raise_for_status(status, body, api_method)

        try:
            return method.__returning__.model_validate(body)
        except Exception as exc:
            raise ClientDecodeError(f"Failed to parse response from {api_method}: {exc}") from exc

    async def close(self) -> None:
        """Close the connection pool if this session opened one."""
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None
