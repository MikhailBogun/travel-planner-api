from datetime import datetime

from pydantic import BaseModel


class PlaceAdd(BaseModel):
    external_id: int


class PlaceUpdate(BaseModel):
    notes: str | None = None
    visited: bool | None = None


class PlaceRead(BaseModel):
    id: int
    external_id: int
    title: str
    notes: str | None
    visited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
