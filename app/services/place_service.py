from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.place import Place
from app.models.project import Project
from app.schemas.place import PlaceAdd, PlaceUpdate
from app.services.art_institute import fetch_artwork
from app.services.project_service import get_project_or_404


async def get_place_or_404(
    session: AsyncSession, project_id: int, place_id: int
) -> Place:
    result = await session.exec(
        select(Place).where(Place.id == place_id, Place.project_id == project_id)
    )
    place = result.first()
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    return place


async def add_place(
    session: AsyncSession, project_id: int, data: PlaceAdd
) -> Place:
    await get_project_or_404(session, project_id)

    result = await session.exec(select(Place).where(Place.project_id == project_id))
    existing = result.all()

    if len(existing) >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project already has the maximum of 10 places",
        )

    if any(p.external_id == data.external_id for p in existing):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This place is already in the project",
        )

    artwork = await fetch_artwork(data.external_id)
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Artwork {data.external_id} not found in Art Institute of Chicago API",
        )

    place = Place(
        project_id=project_id,
        external_id=data.external_id,
        title=artwork["title"],
    )
    session.add(place)
    await session.commit()
    await session.refresh(place)
    return place


async def list_places(session: AsyncSession, project_id: int) -> list[Place]:
    await get_project_or_404(session, project_id)
    result = await session.exec(select(Place).where(Place.project_id == project_id))
    return list(result.all())


async def update_place(
    session: AsyncSession, project_id: int, place_id: int, data: PlaceUpdate
) -> Place:
    project = await get_project_or_404(session, project_id)
    place = await get_place_or_404(session, project_id, place_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(place, field, value)
    place.updated_at = datetime.now(UTC).replace(tzinfo=None)
    session.add(place)
    await session.flush()

    if "visited" in data.model_dump(exclude_unset=True):
        all_places = await session.exec(
            select(Place).where(Place.project_id == project_id)
        )
        is_completed = all(p.visited for p in all_places.all())
        if project.is_completed != is_completed:
            project.is_completed = is_completed
            project.updated_at = datetime.now(UTC).replace(tzinfo=None)
            session.add(project)

    await session.commit()
    await session.refresh(place)
    return place
