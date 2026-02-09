from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import teacher_crud, auth_crud
from backend.schemas import teacher_schema
from backend.database import get_db

router = APIRouter(prefix="/teacher", tags=["teacher"])

@router.get("/list", response_model=List[teacher_schema.Teacher])
async def get_teacher_list(
        global_group_id: str,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)) -> List[teacher_schema.Teacher]:

    is_auth = await auth_crud.check_relations(db, global_group_id, user_id)
    if not is_auth:
        raise HTTPException(
            status_code=401,
            detail="User ID and group ID do not match"
        )

    teachers = await teacher_crud.get_teachers_by_global_group(db, global_group_id)
    return teachers


@router.post("/create", response_model=teacher_schema.Teacher)
async def create_teacher(
        teacher: teacher_schema.TeacherCreate,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    print(teacher.name)

    is_auth = await auth_crud.check_relations(db, teacher.global_group_id, user_id)
    if not is_auth:
        raise HTTPException(
            status_code=401,
            detail="User ID and group ID do not match"
        )

    db_teacher = await teacher_crud.add_teacher(db, teacher.global_group_id, teacher.name)
    return db_teacher
