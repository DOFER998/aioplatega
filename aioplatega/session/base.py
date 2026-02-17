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
        """Execute an API method and return the parsed response."""

    @abstractmethod
    async def close(self) -> None:
        """Release underlying resources (connection pool, etc.)."""
