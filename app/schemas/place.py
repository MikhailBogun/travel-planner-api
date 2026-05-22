from datetime import datetime
from typing import Any

from pydantic import BaseModel, model_validator


class PlaceAdd(BaseModel):
    external_id: int


class PlaceUpdate(BaseModel):
    notes: str | None = None
    visited: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_null_visited(cls, data: Any) -> Any:
        if isinstance(data, dict) and "visited" in data and data["visited"] is None:
            raise ValueError("'visited' must be true or false, not null")
        return data


class PlaceRead(BaseModel):
    id: int
    external_id: int
    title: str
    notes: str | None
    visited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
