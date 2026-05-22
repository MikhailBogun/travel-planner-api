from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.project import Project


class Place(SQLModel, table=True):
    __tablename__ = "places"
    __table_args__ = (UniqueConstraint("project_id", "external_id"),)

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    external_id: int  # artwork ID from the Art Institute of Chicago API
    title: str = Field(max_length=500)  # cached from API to avoid repeated lookups
    notes: str | None = Field(default=None)
    visited: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))

    project: "Project" = Relationship(back_populates="places")
