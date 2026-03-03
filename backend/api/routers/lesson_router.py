from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union

from backend.crud import lesson_crud, auth_crud
from backend.schemas import lesson_schema
from backend.database import get_db

router = APIRouter(prefix="/lesson", tags=["Lesson"])

@router.post("/create", response_model=lesson_schema.LessonAllData)
async def create_lesson(
        lesson_data: lesson_schema.LessonCreate,
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)
        ):

    await auth_crud.check_relations(db, lesson_data.global_group_id, user_id)

    db_lesson = await lesson_crud.add_lesson(db, lesson_data)

    return db_lesson


@router.get("/list", response_model=List[lesson_schema.LessonAllData])
async def get_lessons_by_global_group(
        global_group_id: Union[UUID, str] = Query(...),
        start_date: str = Query(...),
        end_date: str = Query(...),
        user_id: str = Depends(auth_crud.get_user_id),
        db: AsyncSession = Depends(get_db)
        ):

    await auth_crud.check_relations(db, global_group_id, user_id)

    db_lessons = await lesson_crud.get_lessons_by_global_group(db, global_group_id, start_date, end_date)

    return db_lessons