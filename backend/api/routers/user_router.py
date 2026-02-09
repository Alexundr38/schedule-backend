from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import user_crud, auth_crud
from backend.schemas import user_schema
from backend.database import get_db

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create/", status_code=status.HTTP_201_CREATED)
async def create_user(user: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    await user_crud.create_user(db, user=user)
    return {"message": "User created successfully"}


@router.post("/login/")
async def login_user(response: Response, user: user_schema.UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.login_user(db, user=user)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = auth_crud.create_access_token({"sub": str(db_user.user_id)})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        # secure=True,
        samesite="strict",
        path="/"
    )
    return {"message": "Logged in successfully"}

#other methods:
#@router.post("/...")
#async def method(user_id: str = Depends(get_user_id)):


@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        # secure=True,
        samesite="strict"
    )
    return {"message": "Logout successful"}