from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from backend.models import models
from sqlalchemy import select
from backend.schemas import global_group_schema


async def get_list_global_groups(db: AsyncSession, user_id: str) -> List[models.GlobalGroup]:
    result = await db.execute(
        select(models.GlobalGroup).\
        join(models.GlobalGroupUser).\
        where(models.GlobalGroupUser.user_id == user_id)
    )

    return result.scalars().all()


async def create_global_group(db: AsyncSession, user_id: str, global_group_name: str) -> models.GlobalGroup:
    db_global_group = models.GlobalGroup(
        name=global_group_name
    )

    db.add(db_global_group)
    await db.commit()
    await db.refresh(db_global_group)

    db_global_group_user = models.GlobalGroupUser(
        global_group_id=db_global_group.global_group_id,
        user_id=user_id
    )
    db.add(db_global_group_user)
    await db.commit()

    return db_global_group
