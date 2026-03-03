from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import global_group_crud, auth_crud
from backend.schemas import global_group_schema
from backend.database import get_db

router = APIRouter(prefix="/global_group", tags=["global_group"])

@router.get("/list", response_model=List[global_group_schema.GlobalGroup])
async def get_global_group_list(
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):
    global_groups = await global_group_crud.get_list_global_groups(db, user_id)
    return global_groups


@router.post("/create", response_model=global_group_schema.GlobalGroup)
async def create_global_group(
        global_group_name: global_group_schema.GlobalGroupBase,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    global_group = await global_group_crud.create_global_group(db, user_id, global_group_name.name)
    return global_group