from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_201_CREATED
from sqlalchemy.orm import Session

import models
import schemas
import crud
from database import get_db
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #other domens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users/create/", response_model=schemas.UserReturn, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return crud.create_user(db, user=user)

@app.post("/users/login/", response_model=schemas.UserReturn)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.login_user(db, user=user)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    return db_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)