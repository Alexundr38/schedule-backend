from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import user_crud
from backend.schemas import user_schema
from backend.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create/", response_model=user_schema.UserReturn, status_code=status.HTTP_201_CREATED)
async def create_user(user: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    new_user = await user_crud.create_user(db, user=user)
    return new_user

@router.post("/login/", response_model=user_schema.UserReturn)
async def login_user(user: user_schema.UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.login_user(db, user=user)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    return db_user
