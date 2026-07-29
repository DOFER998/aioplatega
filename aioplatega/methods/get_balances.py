from typing import ClassVar

from aioplatega.types import BalancesResponse

from .base import PlategaMethod


class GetBalances(PlategaMethod[BalancesResponse]):
    """GET ``/balance/all`` — merchant balances, one entry per currency."""

    __api_method__: ClassVar[str] = "/balance/all"
    __http_method__: ClassVar[str] = "GET"
    __returning__: ClassVar[type] = BalancesResponse
