from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import teacher_crud, auth_crud
from backend.schemas import teacher_schema
from backend.database import get_db

router = APIRouter(prefix="/teachers", tags=["teachers"])

@router.get("/list")
async def get_teacher_list(global_group_id: str, user_id: str = Depends(auth_crud.get_user_id), db: AsyncSession = Depends(get_db)):
    #check equals global_group_id and user_id
    #add global_group_id to local_storage and add schema

    pass

@router.post("/create")
async def create_teacher(global_group_id: str, user_id: str = Depends(auth_crud.get_user_id), db: AsyncSession = Depends(get_db)):
    #also check
    #return teacher_schema
    pass