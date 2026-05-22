from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class PlaceCreate(BaseModel):
    external_id: int


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    start_date: date | None = None
    places: list[PlaceCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_places(self):
        if len(self.places) > 10:
            raise ValueError("A project can have at most 10 places")
        ids = [p.external_id for p in self.places]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate place IDs in request")
        return self


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_date: date | None = None


class PlaceRead(BaseModel):
    id: int
    external_id: int
    title: str
    notes: str | None
    visited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    start_date: date | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectReadWithPlaces(ProjectRead):
    places: list[PlaceRead] = []
