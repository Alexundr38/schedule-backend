from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from backend.models import models
from sqlalchemy import select


async def get_teacher_by_name(db: AsyncSession, teacher_name: str, global_group_id: str) -> Optional[models.Teacher]:
    result = await db.execute(
        select(models.Teacher).\
        join(models.GlobalGroupTeacher).\
        where(
            models.GlobalGroupTeacher.global_group_id == global_group_id,
            models.Teacher.name == teacher_name
        )
    )
    return result.scalar_one_or_none()


async def get_teachers_by_global_group(db: AsyncSession, global_group_id: str) -> List[models.Teacher]:
    result = await db.execute(
        select(models.Teacher).\
        join(models.GlobalGroupTeacher).\
        where(models.GlobalGroupTeacher.global_group_id == global_group_id)
    )

    return result.scalars().all()


async def add_teacher(db: AsyncSession, global_group_id: str, teacher_name: str) -> Optional[models.Teacher]:
    check_teacher = await get_teacher_by_name(db, teacher_name, global_group_id)
    print(check_teacher)
    if check_teacher:
        raise HTTPException(
            status_code=401,                    #TODO change status code
            detail="Teacher already exists"
        )

    db_teacher = models.Teacher(
        name=teacher_name
    )
    print('1')

    db.add(db_teacher)
    await db.commit()
    await db.refresh(db_teacher)
    print('2')

    db_global_group_teacher = models.GlobalGroupTeacher(
        global_group_id=global_group_id,
        teacher_id=db_teacher.teacher_id
    )

    print('3')
    db.add(db_global_group_teacher)
    await db.commit()
    print('4')

    return db_teacher