from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.place import Place
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.art_institute import fetch_artwork


async def get_project_or_404(session: AsyncSession, project_id: int) -> Project:
    result = await session.exec(select(Project).where(Project.id == project_id))
    project = result.first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


async def get_project_with_places(session: AsyncSession, project_id: int) -> Project:
    result = await session.exec(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    project = result.first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


async def create_project(session: AsyncSession, data: ProjectCreate) -> Project:
    project = Project(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )
    session.add(project)
    await session.flush()

    for place_data in data.places:
        artwork = await fetch_artwork(place_data.external_id)
        if not artwork:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Artwork {place_data.external_id} not found in Art Institute of Chicago API",
            )
        session.add(Place(
            project_id=project.id,
            external_id=place_data.external_id,
            title=artwork["title"],
        ))

    await session.commit()
    return await get_project_with_places(session, project.id)


async def list_projects(
    session: AsyncSession, offset: int, limit: int
) -> list[Project]:
    result = await session.exec(select(Project).offset(offset).limit(limit))
    return list(result.all())


async def update_project(
    session: AsyncSession, project_id: int, data: ProjectUpdate
) -> Project:
    project = await get_project_or_404(session, project_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    project.updated_at = datetime.utcnow()
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def delete_project(session: AsyncSession, project_id: int) -> None:
    project = await get_project_or_404(session, project_id)

    visited = await session.exec(
        select(Place)
        .where(Place.project_id == project_id)
        .where(Place.visited == True)  # noqa: E712
    )
    if visited.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a project that has visited places",
        )

    places = await session.exec(select(Place).where(Place.project_id == project_id))
    for place in places.all():
        await session.delete(place)

    await session.delete(project)
    await session.commit()
