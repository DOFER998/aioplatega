from __future__ import annotations

from typing import Any

import pytest

from aioplatega.client import Platega
from aioplatega.methods.base import PlategaMethod
from aioplatega.session.base import BaseSession


class MockSession(BaseSession):
    """In-memory session that records calls and returns pre-configured responses."""

    def __init__(self, response: Any = None) -> None:
        self.response = response
        self.calls: list[tuple[str, str, PlategaMethod[Any]]] = []
        self.closed = False

    async def make_request(
        self,
        merchant_id: str,
        secret: str,
        method: PlategaMethod[Any],
    ) -> Any:
        self.calls.append((merchant_id, secret, method))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    async def close(self) -> None:
        self.closed = True


@pytest.fixture
def mock_session() -> MockSession:
    return MockSession()


@pytest.fixture
def client(mock_session: MockSession) -> Platega:
    return Platega(
        merchant_id="test-merchant",
        secret="test-secret",
        session=mock_session,
    )
