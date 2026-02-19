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

    await auth_crud.check_relations(db, global_group_id, user_id)

    teachers = await teacher_crud.get_teachers_by_global_group(db, global_group_id)
    return teachers


@router.get("/list_name_id", response_model=List[teacher_schema.Teacher])
async def get_teacher_name_id_list(
        global_group_id: str,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)) -> List[teacher_schema.Teacher]:

    await auth_crud.check_relations(db, global_group_id, user_id)

    teachers = await teacher_crud.get_teachers_name_id_by_global_group(db, global_group_id)
    return teachers


@router.post("/create", response_model=teacher_schema.Teacher)
async def create_teacher(
        teacher: teacher_schema.TeacherCreate,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    print(teacher.name)

    await auth_crud.check_relations(db, teacher.global_group_id, user_id) #TODO other check

    db_teacher = await teacher_crud.add_teacher(db, teacher.global_group_id, teacher.name)
    return db_teacher


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
        teacher: teacher_schema.TeacherGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, teacher.global_group_id, user_id)

    await teacher_crud.delete_teacher(db, teacher.global_group_id, teacher.teacher_id)


@router.put("/update", response_model=teacher_schema.Teacher)
async def update_teacher(
        teacher: teacher_schema.TeacherGlobalGroup,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)):

    await auth_crud.check_relations(db, teacher.global_group_id, user_id)

    db_teacher = await teacher_crud.update_teacher(db, teacher.teacher_id, teacher.name, teacher.global_group_id)
    return db_teacher