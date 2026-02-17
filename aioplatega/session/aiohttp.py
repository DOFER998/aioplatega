from __future__ import annotations

import ssl
from typing import Any, Final

import certifi
from aiohttp import ClientSession, TCPConnector

from aioplatega.exceptions import (
    ClientDecodeError,
    PlategaAPIError,
    PlategaBadRequestError,
    PlategaForbiddenError,
    PlategaNetworkError,
    PlategaNotFoundError,
    PlategaServerError,
    PlategaUnauthorizedError,
)
from aioplatega.methods.base import PlategaMethod

from .base import API_URL, BaseSession

_STATUS_MAP: Final[dict[int, type[PlategaAPIError]]] = {
    400: PlategaBadRequestError,
    401: PlategaUnauthorizedError,
    403: PlategaForbiddenError,
    404: PlategaNotFoundError,
}


_HTTP_CLIENT_ERROR = 400
_HTTP_SERVER_ERROR = 500


def _build_ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=certifi.where())


class AiohttpSession(BaseSession):
    """``aiohttp``-backed session with lazy connection pool creation."""

    def __init__(self, api_url: str = API_URL) -> None:
        self._api_url = api_url
        self._session: ClientSession | None = None

    def _get_session(self) -> ClientSession:
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
        session = self._get_session()

        url = self._build_url(method)
        headers = {
            "X-MerchantId": merchant_id,
            "X-Secret": secret,
        }

        data = method.model_dump(by_alias=True, exclude_none=True)

        try:
            if method.__http_method__ == "POST":
                response = await session.post(url, json=data, headers=headers)
            else:
                response = await session.get(url, params=data, headers=headers)
        except Exception as exc:
            raise PlategaNetworkError(str(exc)) from exc

        return await self._handle_response(response, method)

    def _build_url(self, method: PlategaMethod[Any]) -> str:
        path = method.__api_method__
        data = method.model_dump(by_alias=False, exclude_none=True)
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in path:
                path = path.replace(placeholder, str(value))
        return f"{self._api_url}{path}"

    @staticmethod
    async def _handle_response(
        response: Any,
        method: PlategaMethod[Any],
    ) -> Any:
        status = response.status
        api_method = method.__api_method__

        try:
            body = await response.json()
        except Exception as decode_exc:
            text = await response.text()
            if status >= _HTTP_CLIENT_ERROR:
                raise PlategaAPIError(
                    message=text,
                    method=api_method,
                    status_code=status,
                    body=text,
                ) from decode_exc
            raise ClientDecodeError(
                f"Failed to decode response from {api_method}: {text}"
            ) from decode_exc

        if status >= _HTTP_CLIENT_ERROR:
            message = body.get("message", "") if isinstance(body, dict) else str(body)
            exc_cls = _STATUS_MAP.get(status)
            if exc_cls is None:
                exc_cls = PlategaServerError if status >= _HTTP_SERVER_ERROR else PlategaAPIError
            raise exc_cls(
                message=message,
                method=api_method,
                status_code=status,
                body=body,
            )

        try:
            return method.__returning__.model_validate(body)
        except Exception as exc:
            raise ClientDecodeError(f"Failed to parse response from {api_method}: {exc}") from exc

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None
