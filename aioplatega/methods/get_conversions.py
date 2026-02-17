from typing import TYPE_CHECKING, Any, ClassVar, Optional

from pydantic import Field

from aioplatega.types import ConversionsResponse

from .base import PlategaMethod


class GetConversions(PlategaMethod[ConversionsResponse]):
    __api_method__: ClassVar[str] = "/transaction/balance-unlock-operations"
    __http_method__: ClassVar[str] = "GET"
    __returning__: ClassVar[type] = ConversionsResponse

    from_date: Optional[str] = Field(None, alias="from")
    to_date: Optional[str] = Field(None, alias="to")
    page: int = 0
    size: int = 20

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            from_date: Optional[str] = None,
            to_date: Optional[str] = None,
            page: int = 0,
            size: int = 20,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                from_date=from_date,
                to_date=to_date,
                page=page,
                size=size,
                **__pydantic_kwargs,
            )
