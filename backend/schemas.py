from pydantic import BaseModel, EmailStr, Field
import uuid
from enum import Enum

class EventFormat(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class UserBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr = Field(..., max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=5, max_length=20)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserReturn(UserBase):
    user_id: uuid.UUID