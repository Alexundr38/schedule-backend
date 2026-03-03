from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple, Union

from starlette import status

from backend.crud import teacher_crud
from backend.models import models
from sqlalchemy import select, delete, update

from backend.models import models
from backend.schemas import lesson_schema

async def get_lesson(db: AsyncSession, lesson_data: lesson_schema.LessonCreate) -> Optional[models.Lesson]:
    db_lesson = await db.execute(
        select(models.Lesson).
        join(models.Plan).
        where(
            models.Lesson.plan_id == lesson_data.plan_id,
            models.Lesson.lesson_time_id == lesson_data.lesson_time_id,
            models.Lesson.date == lesson_data.date,
            models.Plan.global_group_id == lesson_data.global_group_id
        )
    )

    return db_lesson.scalar_one_or_none()


async def get_all_lesson_data(db: AsyncSession, lesson_id: Union[UUID, str]) -> lesson_schema.LessonAllData:
    result = (await db.execute(
        select(models.Lesson,
               models.Plan.global_group_id,
               models.Plan.group_id,
               models.Group.name.label("group_name"),
               models.Plan.subject_id,
               models.Subject.name.label("subject_name"),
               models.Plan.event_id,
               models.Event.name.label("event_name"),
               models.Plan.event_format,
               models.TeacherLesson.teacher_id,
               models.Teacher.name.label("teacher_name"),
               )
        .select_from(models.Lesson)
        .join(models.Plan, models.Lesson.plan_id == models.Plan.plan_id)
        .join(models.Group, models.Plan.group_id == models.Group.group_id)
        .join(models.Subject, models.Plan.subject_id == models.Subject.subject_id)
        .join(models.Event, models.Plan.event_id == models.Event.event_id)
        .join(models.TeacherLesson, models.Lesson.lesson_id == models.TeacherLesson.lesson_id)
        .join(models.Teacher, models.TeacherLesson.teacher_id == models.Teacher.teacher_id)
        .where(models.Lesson.lesson_id == lesson_id)
    )).mappings().first()

    return lesson_schema.LessonAllData(
        lesson_id=lesson_id,
        plan_id=result["Lesson"].plan_id,
        lesson_time_id=result["Lesson"].lesson_time_id,
        date=result["Lesson"].date,
        group_id=result["group_id"],
        group_name=result["group_name"],
        subject_id=result["subject_id"],
        subject_name=result["subject_name"],
        event_id=result["event_id"],
        event_name=result["event_name"],
        event_format=result["event_format"],
        teacher_id=result["teacher_id"],
        teacher_name=result["teacher_name"],
    )




async def add_lesson(db: AsyncSession, lesson_data: lesson_schema.LessonCreate) -> lesson_schema.LessonAllData:

    old_lesson = await get_lesson(db, lesson_data)
    if old_lesson:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lesson already exists",
        )

    db_lesson = models.Lesson(
        plan_id=lesson_data.plan_id,
        lesson_time_id=lesson_data.lesson_time_id,
        date=lesson_data.date
    )

    db.add(db_lesson)
    await db.flush()
    await db.refresh(db_lesson)

    teacher_id = await teacher_crud.get_teacher_id_by_plan_id(db, lesson_data.plan_id)

    db_teacher_lesson = models.TeacherLesson(
        teacher_id=teacher_id,
        lesson_id=db_lesson.lesson_id,
    )

    db.add(db_teacher_lesson)
    await db.commit()


    all_lesson_data = await get_all_lesson_data(db, db_lesson.lesson_id)

    return all_lesson_data


async def get_lessons_by_global_group(
        db: AsyncSession,
        global_group_id: str,
        start_date: str,
        end_date: str
        ) -> List[lesson_schema.LessonAllData]:

    parse_start_date = date.fromisoformat(start_date)
    parse_end_date = date.fromisoformat(end_date)

    result = (await db.execute(
        select(models.Lesson,
               models.Plan.global_group_id,
               models.Plan.group_id,
               models.Group.name.label("group_name"),
               models.Plan.subject_id,
               models.Subject.name.label("subject_name"),
               models.Plan.event_id,
               models.Event.name.label("event_name"),
               models.Plan.event_format,
               models.TeacherLesson.teacher_id,
               models.Teacher.name.label("teacher_name"),
               )
        .select_from(models.Lesson)
        .join(models.Plan, models.Lesson.plan_id == models.Plan.plan_id)
        .join(models.Group, models.Plan.group_id == models.Group.group_id)
        .join(models.Subject, models.Plan.subject_id == models.Subject.subject_id)
        .join(models.Event, models.Plan.event_id == models.Event.event_id)
        .join(models.TeacherLesson, models.Lesson.lesson_id == models.TeacherLesson.lesson_id)
        .join(models.Teacher, models.TeacherLesson.teacher_id == models.Teacher.teacher_id)
        .where(
            models.Plan.global_group_id == global_group_id,
            models.Lesson.date.between(parse_start_date, parse_end_date)
        )
    )).mappings()

    return [lesson_schema.LessonAllData(
        lesson_id=r["Lesson"].lesson_id,
        plan_id=r["Lesson"].plan_id,
        lesson_time_id=r["Lesson"].lesson_time_id,
        date=r["Lesson"].date,
        group_id=r["group_id"],
        group_name=r["group_name"],
        subject_id=r["subject_id"],
        subject_name=r["subject_name"],
        event_id=r["event_id"],
        event_name=r["event_name"],
        event_format=r["event_format"],
        teacher_id=r["teacher_id"],
        teacher_name=r["teacher_name"],
    ) for r in result]