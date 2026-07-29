from typing import Any

from pydantic import BaseModel, ConfigDict


class PlategaObject(BaseModel):
    """Base model for all Platega API objects.

    Immutable (``frozen=True``) and tolerant of unknown fields, so a new
    attribute added server-side does not break existing callers.
    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="allow",
        # No validate_assignment: frozen=True rejects assignment outright, so
        # the validation hook could never run.
        frozen=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        defer_build=True,
    )


class SequenceResponse:
    """Sequence access for responses whose JSON body is a bare array.

    Mixed into a ``RootModel`` so callers can iterate the response directly
    instead of reaching for ``.root``. Deliberately not a generic base class:
    a parametrised generic keeps the ``__module__`` of the base, which makes
    autodoc emit it once per parametrisation.
    """

    root: Any

    def __iter__(self) -> Any:
        return iter(self.root)

    def __getitem__(self, index: int) -> Any:
        return self.root[index]

    def __len__(self) -> int:
        return len(self.root)
