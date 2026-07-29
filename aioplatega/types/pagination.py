from .base import PlategaObject


class Pagination(PlategaObject):
    """Page marker returned alongside a paginated list."""

    page: int | None = None
    size: int | None = None
    total: int | None = None
