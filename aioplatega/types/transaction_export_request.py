from pydantic import Field

from .base import PlategaObject


class TransactionExportRequest(PlategaObject):
    """Filters shared by the CSV, Excel and JSON transaction exports."""

    statuses: list[str] | None = None
    payment_methods: list[str] | None = Field(None, alias="paymentMethods")
    from_date: str | None = Field(None, alias="from")
    to_date: str | None = Field(None, alias="to")
    time_zone_id: str | None = Field(None, alias="timeZoneId")
