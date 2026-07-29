from __future__ import annotations

from typing import Any

import pytest
from faker import Faker

from aioplatega.client import Platega
from aioplatega.methods.base import PlategaMethod
from aioplatega.session.base import BaseSession

SEED = 20260729
"""Fixed so a failure reproduces from the test name alone."""


@pytest.fixture(scope="session")
def faker_seed() -> int:
    return SEED


@pytest.fixture
def fake() -> Faker:
    """Faker with a fixed seed, so generated values stay stable across runs."""
    instance = Faker()
    Faker.seed(SEED)
    return instance


@pytest.fixture
def transaction_id(fake: Faker) -> str:
    return str(fake.uuid4())


@pytest.fixture
def subscription_id(fake: Faker) -> str:
    return str(fake.uuid4())


@pytest.fixture
def merchant_id(fake: Faker) -> str:
    return str(fake.uuid4())


@pytest.fixture
def secret(fake: Faker) -> str:
    return fake.password(length=32, special_chars=False)


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
def client(mock_session: MockSession, merchant_id: str, secret: str) -> Platega:
    return Platega(
        merchant_id=merchant_id,
        secret=secret,
        session=mock_session,
    )
