from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.schemas.place import PlaceAdd, PlaceRead, PlaceUpdate
from app.services import place_service

router = APIRouter(prefix="/projects/{project_id}/places", tags=["places"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=PlaceRead, status_code=status.HTTP_201_CREATED)
async def add_place(project_id: int, data: PlaceAdd, session: SessionDep):
    return await place_service.add_place(session, project_id, data)


@router.get("", response_model=list[PlaceRead])
async def list_places(project_id: int, session: SessionDep):
    return await place_service.list_places(session, project_id)


@router.get("/{place_id}", response_model=PlaceRead)
async def get_place(project_id: int, place_id: int, session: SessionDep):
    return await place_service.get_place_or_404(session, project_id, place_id)


@router.patch("/{place_id}", response_model=PlaceRead)
async def update_place(
    project_id: int, place_id: int, data: PlaceUpdate, session: SessionDep
):
    return await place_service.update_place(session, project_id, place_id, data)
