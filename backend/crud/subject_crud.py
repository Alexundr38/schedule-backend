from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from backend.models import models
from sqlalchemy import select, delete, update


async def get_subject_by_name(db: AsyncSession, subject_name: str, global_group_id: str) -> Optional[models.Subject]:
    result = await db.execute(
        select(models.Subject).\
        join(models.GlobalGroupSubject).\
        where(
            models.GlobalGroupSubject.global_group_id == global_group_id,
            models.Subject.name == subject_name
        )
    )
    return result.scalar_one_or_none()


async def get_subjects_by_global_group(db: AsyncSession, global_group_id: str) -> List[models.Subject]:
    result = await db.execute(
        select(models.Subject).\
        join(models.GlobalGroupSubject).\
        where(models.GlobalGroupSubject.global_group_id == global_group_id)
    )

    return result.scalars().all()


async def add_subject(db: AsyncSession, global_group_id: str, subject_name: str) -> Optional[models.Subject]:
    check_subject = await get_subject_by_name(db, subject_name, global_group_id)
    if check_subject:
        raise HTTPException(
            status_code=401,                    #TODO change status code
            detail="Subject already exists"
        )

    db_subject = models.Subject(
        name=subject_name
    )

    db.add(db_subject)
    await db.commit()
    await db.refresh(db_subject)

    db_global_group_subject = models.GlobalGroupSubject(
        global_group_id=global_group_id,
        subject_id=db_subject.subject_id
    )

    db.add(db_global_group_subject)
    await db.commit()

    return db_subject


async def delete_subject(db: AsyncSession, global_group_id: str, subject_id: str) -> bool:
    subquery = (
        select(models.GlobalGroupSubject.subject_id).\
        where(
            models.GlobalGroupSubject.global_group_id == global_group_id,
            models.GlobalGroupSubject.subject_id == subject_id
        )
    ).scalar_subquery()

    result = await db.execute(
        delete(models.Subject).\
        where(models.Subject.subject_id == subquery)
    )

    # result = await db.execute(
    #     delete(models.Subject). \
    #     where(models.Subject.subject_id == subject_id)
    # )

    if result.rowcount == 0:
        return False

    await db.commit()
    return True


async def update_subject(db: AsyncSession, subject_id: str, subject_name:str, global_group_id: str) -> Optional[models.Subject]:

    old_subject = await get_subject_by_name(db, subject_name, global_group_id)
    if old_subject:
        raise HTTPException(
            status_code=401, #TODO change code
            detail="Subject already exists"
        )

    result = await db.execute(
        update(models.Subject).\
        where(models.Subject.subject_id == subject_id).\
        values(name=subject_name).\
        returning(models.Subject)
    )

    db_subject = result.scalar_one_or_none()

    if not db_subject:
        raise HTTPException(
            status_code=401,                #TODO check code
            detail="Subject does not exist"
        )

    await db.commit()
    await db.refresh(db_subject)

    return db_subject