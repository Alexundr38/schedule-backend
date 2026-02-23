from uuid import UUID
from datetime import time
from typing import Union, Optional

from pydantic import BaseModel, field_serializer, ConfigDict


class LessonTimeBase(BaseModel):
    start_time: time
    end_time: time
    lesson_time_id: Optional[Union[UUID, str]] = None

    @field_serializer('lesson_time_id')
    def serialize_lesson_time(self, lesson_time_id: UUID):
        return str(lesson_time_id) if lesson_time_id else None

class LessonTime(LessonTimeBase):
    model_config = ConfigDict(from_attributes=True)

    time_group_id: Union[UUID, str]

    @field_serializer('time_group_id')
    def serialize_time_group(self, time_group_id: UUID):
        return str(time_group_id) if time_group_id else None

class TimeGroup(BaseModel):
    name: str
    times: list[LessonTimeBase]
    global_group_id: Union[UUID, str]
    time_group_id: Optional[Union[UUID, str]] = None

class LessonTimeGroup(BaseModel):
    name: str
    times: list[LessonTime]
    time_group_id: Union[UUID, str]

    @field_serializer('time_group_id')
    def serialize_time_group(self, time_group_id: UUID):
        return str(time_group_id) if time_group_id else None

class TimeGroupNameId(BaseModel):
    name: str
    time_group_id: Union[UUID, str]
    global_group_id: Union[UUID, str]