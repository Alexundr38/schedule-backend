import email

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Optional
import models
import schemas

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = password_context.hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login_user(db: Session, user: schemas.UserLogin) -> Optional[models.User]:
    db_user = get_user_by_email(db, user.email)
    if not db_user:
        return None
    if not password_context.verify(user.password, db_user.password):
        return None
    return db_user