from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from backend.models import models
from sqlalchemy import select, delete, update


async def get_group_by_name(db: AsyncSession, group_name: str, global_group_id: str) -> Optional[models.Group]:
    result = await db.execute(
        select(models.Group).\
        join(models.GlobalGroupGroup).\
        where(
            models.GlobalGroupGroup.global_group_id == global_group_id,
            models.Group.name == group_name
        )
    )
    return result.scalar_one_or_none()


async def get_group_by_global_group(db: AsyncSession, global_group_id: str) -> List[models.Group]:
    result = await db.execute(
        select(models.Group).\
        join(models.GlobalGroupGroup).\
        where(models.GlobalGroupGroup.global_group_id == global_group_id)
    )

    return result.scalars().all()


async def get_groups_name_id_by_global_group(db: AsyncSession, global_group_id: str) -> List[Tuple[str, str]]:
    result = await db.execute(
        select(models.Group.name, models.Group.group_id).\
        join(models.GlobalGroupGroup).\
        where(models.GlobalGroupGroup.global_group_id == global_group_id)
    )

    return result.all()


async def add_group(db: AsyncSession, global_group_id: str, group_name: str, student_count: int) -> Optional[models.Group]:
    check_group = await get_group_by_name(db, group_name, global_group_id)
    if check_group:
        raise HTTPException(
            status_code=401,                    #TODO change status code
            detail="group already exists"
        )

    db_group = models.Group(
        name=group_name,
        student_count=student_count
    )

    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)

    db_global_group_group = models.GlobalGroupGroup(
        global_group_id=global_group_id,
        group_id=db_group.group_id
    )

    db.add(db_global_group_group)
    await db.commit()

    return db_group


async def delete_group(db: AsyncSession, global_group_id: str, group_id: str) -> bool:
    subquery = (
        select(models.GlobalGroupGroup.group_id).\
        where(
            models.GlobalGroupGroup.global_group_id == global_group_id,
            models.GlobalGroupGroup.group_id == group_id
        )
    ).scalar_subquery()

    result = await db.execute(
        delete(models.Group).\
        where(models.Group.group_id == subquery)
    )

    # result = await db.execute(
    #     delete(models.group). \
    #     where(models.group.group_id == group_id)
    # )

    if result.rowcount == 0:
        return False

    await db.commit()
    return True


async def update_group(db: AsyncSession, group_id: str, group_name:str, student_count: int, global_group_id: str) -> Optional[models.Group]:

    old_group = await get_group_by_name(db, group_name, global_group_id)
    if str(old_group.group_id) != group_id:
        raise HTTPException(
            status_code=401, #TODO change code
            detail="group already exists"
        )

    result = await db.execute(
        update(models.Group).\
        where(models.Group.group_id == group_id).\
        values(
            name=group_name,
            student_count=student_count
        ).\
        returning(models.Group)
    )

    db_group = result.scalar_one_or_none()

    if not db_group:
        raise HTTPException(
            status_code=401,                #TODO check code
            detail="group does not exist"
        )

    await db.commit()
    await db.refresh(db_group)

    return db_group