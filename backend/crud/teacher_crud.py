from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from backend.models import models
from sqlalchemy import select, delete, update


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


#now it equals with previous, but this is look forward to the future
async def get_teachers_name_id_by_global_group(db: AsyncSession, global_group_id: str) -> List[models.Teacher]:
    result = await db.execute(
        select(models.Teacher).\
        join(models.GlobalGroupTeacher).\
        where(models.GlobalGroupTeacher.global_group_id == global_group_id)
    )

    return result.scalars().all()


async def add_teacher(db: AsyncSession, global_group_id: str, teacher_name: str) -> Optional[models.Teacher]:
    check_teacher = await get_teacher_by_name(db, teacher_name, global_group_id)
    if check_teacher:
        raise HTTPException(
            status_code=401,                    #TODO change status code
            detail="Teacher already exists"
        )

    db_teacher = models.Teacher(
        name=teacher_name
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


async def delete_teacher(db: AsyncSession, global_group_id: str, teacher_id: str) -> bool:
    subquery = (
        select(models.GlobalGroupTeacher.teacher_id).\
        where(
            models.GlobalGroupTeacher.global_group_id == global_group_id,
            models.GlobalGroupTeacher.teacher_id == teacher_id
        )
    ).scalar_subquery()

    result = await db.execute(
        delete(models.Teacher).\
        where(models.Teacher.teacher_id == subquery)
    )

    # result = await db.execute(
    #     delete(models.Teacher). \
    #     where(models.Teacher.teacher_id == teacher_id)
    # )

    if result.rowcount == 0:
        return False

    await db.commit()
    return True


async def update_teacher(db: AsyncSession, teacher_id: str, teacher_name:str, global_group_id: str) -> Optional[models.Teacher]:

    old_teacher = await get_teacher_by_name(db, teacher_name, global_group_id)
    if old_teacher:
        raise HTTPException(
            status_code=401, #TODO change code
            detail="Teacher already exists"
        )

    result = await db.execute(
        update(models.Teacher).\
        where(models.Teacher.teacher_id == teacher_id).\
        values(name=teacher_name).\
        returning(models.Teacher)
    )

    db_teacher = result.scalar_one_or_none()

    if not db_teacher:
        raise HTTPException(
            status_code=401,                #TODO check code
            detail="Teacher does not exist"
        )

    await db.commit()
    await db.refresh(db_teacher)

    return db_teacher