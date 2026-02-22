from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple

from starlette import status

from backend.models import models
from sqlalchemy import select, delete, update

from backend.schemas.time_schema import LessonTimeGroup, TimeGroup, TimeGroupNameId


async def get_time_group_by_name(db: AsyncSession, time_group_name: str, global_group_id: str) -> Optional[models.TimeGroup]:
    result = await db.execute(
        select(models.TimeGroup).\
        join(models.GlobalGroupTimeGroup).\
        where(
            models.GlobalGroupTimeGroup.global_group_id == global_group_id,
            models.TimeGroup.name == time_group_name
        )
    )
    return result.scalar_one_or_none()


async def get_time_groups_by_global_group(db: AsyncSession, global_group_id: str) -> List[LessonTimeGroup]:
    db_time_groups = (await db.execute(
        select(models.TimeGroup).
        join(models.GlobalGroupTimeGroup).
        where(models.GlobalGroupTimeGroup.global_group_id == global_group_id)
    )).scalars().all()

    returned_time_groups = []

    for time_group in db_time_groups:
        times = (await db.execute(
            select(models.LessonTime).\
            where(models.LessonTime.time_group_id == time_group.time_group_id)
        )).scalars().all()

        returned_time_groups.append(
            LessonTimeGroup(
                time_group_id=time_group.time_group_id,
                name=time_group.name,
                times=times
            )
        )

    return returned_time_groups


async def add_time_group(db: AsyncSession, data: TimeGroup) -> Optional[LessonTimeGroup]:
    try:

        check_group = await get_time_group_by_name(db, data.name, data.global_group_id)
        if check_group:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Time group already exists"
            )

        db_time_group = models.TimeGroup(
            name=data.name,
        )

        db.add(db_time_group)
        await db.flush()
        await db.refresh(db_time_group)

        db_global_group_time_group = models.GlobalGroupTimeGroup(
            global_group_id=data.global_group_id,
            time_group_id=db_time_group.time_group_id
        )

        db.add(db_global_group_time_group)
        await db.flush()

        times = []

        for time in data.times:
            lesson_time = models.LessonTime(
                time_group_id=db_time_group.time_group_id,
                start_time=time.start_time,
                end_time=time.end_time,
            )
            db.add(lesson_time)
            await db.flush()
            await db.refresh(lesson_time)

            times.append(lesson_time)

        await db.commit()

        return LessonTimeGroup(
            time_group_id=db_time_group.time_group_id,
            name=data.name,
            times=times
        )

    except (HTTPException) as e:
        await db.rollback()
        raise e


async def delete_time_group(db: AsyncSession, data: TimeGroupNameId):
    subquery = (
        select(models.GlobalGroupTimeGroup.time_group_id).
        where(
            models.GlobalGroupTimeGroup.global_group_id == data.global_group_id,
            models.GlobalGroupTimeGroup.time_group_id == data.time_group_id
        )
    ).scalar_subquery()

    result = await db.execute(
        delete(models.TimeGroup).\
        where(models.TimeGroup.time_group_id == subquery)
    )

    # result = await db.execute(
    #     delete(models.Teacher). \
    #     where(models.Teacher.teacher_id == teacher_id)
    # )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Time group does not exist"
        )

    await db.commit()