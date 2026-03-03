from typing import List, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.crud import auth_crud, time_crud
from backend.schemas import time_schema
from backend.database import get_db

router = APIRouter(prefix="/time", tags=["Plan"])

@router.post("/create", response_model=time_schema.LessonTimeGroup)
async def create_time(
        time_data: time_schema.TimeGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, time_data.global_group_id, user_id)

    db_time_group = await time_crud.add_time_group(db, time_data)
    return db_time_group


@router.get("/list", response_model=List[time_schema.LessonTimeGroup])
async def get_time_group_list(
        global_group_id: Union[UUID, str] = Query(...),
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, global_group_id, user_id)

    db_times = await time_crud.get_time_groups_by_global_group(db, global_group_id)
    return db_times


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_group(
        time_data: time_schema.TimeGroupNameId,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)
        ):

    await auth_crud.check_relations(db, time_data.global_group_id, user_id)

    await time_crud.delete_time_group(db, time_data)


#TODO add update


@router.put("/update", response_model=time_schema.LessonTimeGroup)
async def update_time_group(
        time_data: time_schema.TimeGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)
        ):

    await auth_crud.check_relations(db, time_data.global_group_id, user_id)

    db_time_group = await time_crud.update_time_group(db, time_data)
    return db_time_group