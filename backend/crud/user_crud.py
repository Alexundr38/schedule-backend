from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from backend.models import models
from backend.schemas import user_schema
from datetime import datetime
from sqlalchemy import select
from backend.crud import auth_crud


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    return result.scalars().one_or_none()


async def create_user(db: AsyncSession, user: user_schema.UserCreate):
    hashed_password = auth_crud.get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        date_registration=datetime.now()
    )
    db_global_group = models.GlobalGroup(
        name=user.name
    )

    db.add(db_user)
    db.add(db_global_group)
    await db.commit()
    await db.refresh(db_user)
    await db.refresh(db_global_group)

    db_global_group_user = models.GlobalGroupUser(
        global_group_id=db_global_group.global_group_id,
        user_id=db_user.user_id
    )
    db.add(db_global_group_user)
    await db.commit()



async def login_user(db: AsyncSession, user: user_schema.UserLogin) -> Optional[models.User]:
    db_user = await get_user_by_email(db, user.email)
    if not db_user:
        return None
    if not auth_crud.verify_password(user.password, db_user.password):
        return None
    return db_user