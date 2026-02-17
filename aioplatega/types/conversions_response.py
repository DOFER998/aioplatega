from typing import TYPE_CHECKING, Any

from pydantic import Field

from .base import PlategaObject
from .conversion_item import ConversionItem


class ConversionsResponse(PlategaObject):
    content: list[ConversionItem] = Field(default_factory=list)
    total_elements: int = Field(0, alias="totalElements")
    total_pages: int = Field(0, alias="totalPages")
    page: int = 0
    size: int = 0

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            content: list[ConversionItem] = ...,  # type: ignore[assignment]
            total_elements: int = 0,
            total_pages: int = 0,
            page: int = 0,
            size: int = 0,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                content=content,
                total_elements=total_elements,
                total_pages=total_pages,
                page=page,
                size=size,
                **__pydantic_kwargs,
            )
