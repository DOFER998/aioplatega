from .base import PlategaObject


class H2HQrResponse(PlategaObject):
    """QR code or payment link for a host-to-host transaction."""

    amount: float | None = None
    qr: str | None = None
