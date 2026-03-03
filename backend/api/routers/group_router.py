from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union

from backend.crud import group_crud, auth_crud
from backend.schemas import group_schema
from backend.database import get_db

router = APIRouter(prefix="/group", tags=["group"])


@router.get("/list", response_model=List[group_schema.Group])
async def get_group_list(
        global_group_id: Union[UUID, str] = Query(...),
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)) -> List[group_schema.Group]:

    await auth_crud.check_relations(db, global_group_id, user_id)

    groups = await group_crud.get_groups_by_global_group(db, global_group_id)
    return groups


@router.get("/list_name_id", response_model=List[group_schema.GroupNameId])
async def get_group_name_id_list(
        global_group_id: Union[UUID, str] = Query(...),
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, global_group_id, user_id)

    db_groups = await group_crud.get_groups_name_id_by_global_group(db, global_group_id)
    return db_groups


@router.post("/create", response_model=group_schema.Group)
async def create_group(
        group: group_schema.GroupCreate,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    print(group.name)

    await auth_crud.check_relations(db, group.global_group_id, user_id) #TODO other check

    db_group = await group_crud.add_group(db, group.global_group_id, group.name, group.student_count)
    return db_group


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
        group: group_schema.GroupGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, group.global_group_id, user_id)

    await group_crud.delete_group(db, group.global_group_id, group.group_id)


@router.put("/update", response_model=group_schema.Group)
async def update_group(
        group: group_schema.GroupGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, group.global_group_id, user_id)

    db_group = await group_crud.update_group(db, group.group_id, group.name, group.student_count, group.global_group_id)
    return db_group