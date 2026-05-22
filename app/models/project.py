from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.place import Place


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None)
    start_date: date | None = Field(default=None)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    places: list["Place"] = Relationship(back_populates="project")
