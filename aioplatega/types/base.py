from pydantic import BaseModel, ConfigDict


class PlategaObject(BaseModel):
    """Base model for all Platega API objects.

    Configured as immutable (``frozen=True``) with extra fields allowed.
    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="allow",
        validate_assignment=True,
        frozen=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        defer_build=True,
    )
