from .base import PlategaObject


class ExportUrlResponse(PlategaObject):
    """A link to the generated export file."""

    url: str
