from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aioplatega.methods.base import PlategaMethod

API_URL = "https://app.platega.io"


class BaseSession(ABC):
    """Abstract session interface for the Platega API.

    Implement this class to provide a custom HTTP transport.
    The default implementation is :class:`~aioplatega.session.aiohttp.AiohttpSession`.
    """

    @abstractmethod
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
        """

    @abstractmethod
    async def close(self) -> None:
        """Release underlying resources, such as the connection pool."""
