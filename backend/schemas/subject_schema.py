from typing import Union
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class SubjectBase(BaseModel):
    name: str = Field(..., max_length=255)


class Subject(SubjectBase):
    subject_id: Union[UUID, str]

    @field_serializer('subject_id')
    def serialize_subject_id(self, subject_id: UUID):
        return str(subject_id) if subject_id else None


class SubjectCreate(SubjectBase):
    global_group_id: str


class SubjectGlobalGroup(Subject):
    global_group_id: Union[UUID, str]

    @field_serializer('global_group_id')
    def serialize_global_group_id(self, global_group_id: UUID):
        return str(global_group_id) if global_group_id else None