from __future__ import annotations

from typing import Any, ClassVar, Generic, TypeVar

from aioplatega.types.base import PlategaObject

PlategaType = TypeVar("PlategaType")


class PlategaMethod(PlategaObject, Generic[PlategaType]):
    """Base class for all Platega API methods (command pattern).

    Subclasses must specify:
      - ``__api_method__``: URL path (may contain ``{field_name}`` placeholders).
      - ``__http_method__``: ``"GET"`` or ``"POST"``.
      - ``__returning__``: response model class.
    """

    __api_method__: ClassVar[str]
    __http_method__: ClassVar[str]
    __returning__: ClassVar[type[Any]]
