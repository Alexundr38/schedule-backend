from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from backend.models import models
from sqlalchemy import select, delete, update


async def get_event_by_name(db: AsyncSession, event_name: str, global_group_id: str) -> Optional[models.Event]:
    result = await db.execute(
        select(models.Event).\
        join(models.GlobalGroupEvent).\
        where(
            models.GlobalGroupEvent.global_group_id == global_group_id,
            models.Event.name == event_name
        )
    )
    return result.scalar_one_or_none()


async def get_events_by_global_group(db: AsyncSession, global_group_id: str) -> List[models.Event]:
    result = await db.execute(
        select(models.Event).\
        join(models.GlobalGroupEvent).\
        where(models.GlobalGroupEvent.global_group_id == global_group_id)
    )

    return result.scalars().all()


#now it equals with previous, but this is look forward to the future
async def get_events_name_id_by_global_group(db: AsyncSession, global_group_id: str) -> List[models.Event]:
    result = await db.execute(
        select(models.Event).\
        join(models.GlobalGroupEvent).\
        where(models.GlobalGroupEvent.global_group_id == global_group_id)
    )

    return result.scalars().all()


async def add_event(db: AsyncSession, global_group_id: str, event_name: str) -> Optional[models.Event]:
    check_event = await get_event_by_name(db, event_name, global_group_id)
    if check_event:
        raise HTTPException(
            status_code=401,                    #TODO change status code
            detail="Event already exists"
        )

    db_event = models.Event(
        name=event_name
    )

    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)

    db_global_group_event = models.GlobalGroupEvent(
        global_group_id=global_group_id,
        event_id=db_event.event_id
    )

    db.add(db_global_group_event)
    await db.commit()

    return db_event


async def delete_event(db: AsyncSession, global_group_id: str, event_id: str) -> bool:
    subquery = (
        select(models.GlobalGroupEvent.event_id).\
        where(
            models.GlobalGroupEvent.global_group_id == global_group_id,
            models.GlobalGroupEvent.event_id == event_id
        )
    ).scalar_subquery()

    result = await db.execute(
        delete(models.Event).\
        where(models.Event.event_id == subquery)
    )

    # result = await db.execute(
    #     delete(models.Event). \
    #     where(models.Event.event_id == event_id)
    # )

    if result.rowcount == 0:
        return False

    await db.commit()
    return True


async def update_event(db: AsyncSession, event_id: str, event_name:str, global_group_id: str) -> Optional[models.Event]:

    old_event = await get_event_by_name(db, event_name, global_group_id)
    if old_event:
        raise HTTPException(
            status_code=401, #TODO change code
            detail="Event already exists"
        )

    result = await db.execute(
        update(models.Event).\
        where(models.Event.event_id == event_id).\
        values(name=event_name).\
        returning(models.Event)
    )

    db_event = result.scalar_one_or_none()

    if not db_event:
        raise HTTPException(
            status_code=401,                #TODO check code
            detail="Event does not exist"
        )

    await db.commit()
    await db.refresh(db_event)

    return db_event