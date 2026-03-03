from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union

from backend.crud import event_crud, auth_crud
from backend.schemas import event_schema
from backend.database import get_db

router = APIRouter(prefix="/event", tags=["event"])

@router.get("/list", response_model=List[event_schema.Event])
async def get_event_list(
        global_group_id: Union[UUID, str] = Query(...),
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)) -> List[event_schema.Event]:

    await auth_crud.check_relations(db, global_group_id, user_id)

    events = await event_crud.get_events_by_global_group(db, global_group_id)
    return events


@router.get("/list_name_id", response_model=List[event_schema.Event])
async def get_event_name_id_list(
        global_group_id: Union[UUID, str] = Query(...),
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)) -> List[event_schema.Event]:

    await auth_crud.check_relations(db, global_group_id, user_id)

    events = await event_crud.get_events_name_id_by_global_group(db, global_group_id)
    return events


@router.post("/create", response_model=event_schema.Event)
async def create_event(
        event: event_schema.EventCreate,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    print(event.name)

    await auth_crud.check_relations(db, event.global_group_id, user_id) #TODO other check

    db_event = await event_crud.add_event(db, event.global_group_id, event.name)
    return db_event


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
        event: event_schema.EventGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, event.global_group_id, user_id)

    await event_crud.delete_event(db, event.global_group_id, event.event_id)


@router.put("/update", response_model=event_schema.Event)
async def update_event(
        event: event_schema.EventGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, event.global_group_id, user_id)

    db_event = await event_crud.update_event(db, event.event_id, event.name, event.global_group_id)
    return db_event