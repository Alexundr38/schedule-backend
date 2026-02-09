from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from backend.models import models
from sqlalchemy import select
from backend.schemas import teacher_schema


async def get_teacher_by_name(db: AsyncSession, teacher_name: str) -> Optional[models.Teacher]: #TODO add global group
    result = await db.execute(
        select(models.Teacher).where(models.Teacher.name == teacher_name)
    )
    return result.scalar().one_or_none()


async def get_teachers_by_global_group(db: AsyncSession, global_group_id: str) -> Optional[List[models.Teacher]]:
    result = await db.execute(
        select(models.Teacher).\
        join(models.GlobalGroupTeacher).\
        where(models.GlobalGroupTeacher.global_group_id == global_group_id)
    )

    return result.scalars().all()


async def add_teacher(db: AsyncSession, global_group_id: str, teacher: teacher_schema.TeacherBase) -> Optional[models.Teacher]:
    db_teacher = models.Teacher(
        name=teacher.name
    )

    db.add(db_teacher)
    await db.commit()
    await db.refresh(db_teacher)

    db_global_group_teacher = models.GlobalGroupTeacher(
        global_group_id=global_group_id,
        teacher_id=db_teacher.teacher_id
    )

    db.add(db_global_group_teacher)
    await db.commit()

    return db_teacher