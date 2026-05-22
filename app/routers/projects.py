from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.schemas.project import ProjectCreate, ProjectRead, ProjectReadWithPlaces, ProjectUpdate
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/", response_model=ProjectReadWithPlaces, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, session: SessionDep):
    return await project_service.create_project(session, data)


@router.get("/", response_model=list[ProjectRead])
async def list_projects(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await project_service.list_projects(session, offset, limit)


@router.get("/{project_id}", response_model=ProjectReadWithPlaces)
async def get_project(project_id: int, session: SessionDep):
    return await project_service.get_project_with_places(session, project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(project_id: int, data: ProjectUpdate, session: SessionDep):
    return await project_service.update_project(session, project_id, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, session: SessionDep):
    await project_service.delete_project(session, project_id)
