from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import group_crud, auth_crud
from backend.schemas import group_schema
from backend.database import get_db

router = APIRouter(prefix="/group", tags=["group"])

@router.get("/list", response_model=List[group_schema.Group])
async def get_group_list(
        global_group_id: str,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)) -> List[group_schema.Group]:

    is_auth = await auth_crud.check_relations(db, global_group_id, user_id)
    if not is_auth:
        raise HTTPException(
            status_code=401,
            detail="User ID and group ID do not match"
        )

    groups = await group_crud.get_groups_by_global_group(db, global_group_id)
    return groups


@router.post("/create", response_model=group_schema.Group)
async def create_group(
        group: group_schema.GroupCreate,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    print(group.name)

    await auth_crud.check_relations(db, group.global_group_id, user_id) #TODO other check

    db_group = await group_crud.add_group(db, group.global_group_id, group.name, group.student_count)
    return db_group


@router.delete("/delete")
async def delete_group(
        group: group_schema.GroupGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, group.global_group_id, user_id)

    result = await group_crud.delete_group(db, group.global_group_id, group.group_id)
    return result #TODO change response with False


@router.put("/update", response_model=group_schema.Group)
async def update_group(
        group: group_schema.GroupGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, group.global_group_id, user_id)

    db_group = await group_crud.update_group(db, group.group_id, group.name, group.student_count, group.global_group_id)
    return db_group