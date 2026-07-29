from pydantic import Field, RootModel

from .base import PlategaObject, SequenceResponse


class SavedCard(PlategaObject):
    """A payout card saved by the merchant."""

    card_id: str | None = Field(None, alias="cardId")
    masked: str | None = None
    last4: str | None = None
    brand: str | None = None
    label: str | None = None
    status: str | None = None


class SavedCardsResponse(SequenceResponse, RootModel[list[SavedCard]]):
    """``GET /api/v1/cards``: a bare array of saved cards."""
