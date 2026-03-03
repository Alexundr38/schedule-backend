from datetime import date
from typing import Union, List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer
from sqlalchemy.orm import validates


class LessonBase(BaseModel):
    plan_id: Union[UUID, str]
    lesson_time_id: Union[UUID, str]
    date: date


class LessonCreate(LessonBase):
    global_group_id: Union[UUID, str]

class LessonWithId(LessonBase):
    lesson_id: Union[UUID, str]

    @field_serializer('lesson_id')
    def serialize_lesson_id(self, lesson_id: UUID) -> str:
        return str(lesson_id) if lesson_id else None

class LessonAllData(LessonWithId):
    group_id: Union[UUID, str]
    group_name: str
    subject_id: Union[UUID, str]
    subject_name: str
    event_id: Union[UUID, str]
    event_name: str
    teacher_id: Union[UUID, str]
    teacher_name: str
    event_format: str
