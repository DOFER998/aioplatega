from typing import Any

from pydantic import Field

from .base import PlategaObject
from .conversion_item import ConversionItem
from .pagination import Pagination


class ConversionsResponse(PlategaObject):
    """A page of balance-unlock operations.

    Iterating the response yields the operations directly.

    Note:
        The API answers with ``operations`` and ``pagination``. Earlier
        releases modelled ``content``/``totalElements``, which no live
        response has ever contained, so the operations were silently dropped
        and the list always came back empty.
    """

    operations: list[ConversionItem] = Field(default_factory=list)
    pagination: Pagination | None = None

    def __iter__(self) -> Any:
        return iter(self.operations)

    def __getitem__(self, index: int) -> ConversionItem:
        return self.operations[index]

    def __len__(self) -> int:
        return len(self.operations)
