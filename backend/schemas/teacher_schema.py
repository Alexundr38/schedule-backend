from typing import Union
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class TeacherBase(BaseModel):
    name: str = Field(..., max_length=255)


class Teacher(TeacherBase):
    teacher_id: Union[UUID, str]

    @field_serializer('teacher_id')
    def serialize_teacher_id(self, teacher_id: UUID):
        return str(teacher_id) if teacher_id else None


class TeacherCreate(TeacherBase):
    global_group_id: str