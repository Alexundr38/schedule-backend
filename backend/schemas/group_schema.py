from typing import Union
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class GroupBase(BaseModel):
    name: str = Field(..., max_length=255)
    student_count: int = Field(...)


class Group(GroupBase):
    group_id: Union[UUID, str]

    @field_serializer('group_id')
    def serialize_group_id(self, group_id: UUID):
        return str(group_id) if group_id else None


class GroupCreate(GroupBase):
    global_group_id: str


class GroupGlobalGroup(Group):
    global_group_id: Union[UUID, str]

    @field_serializer('global_group_id')
    def serialize_global_group_id(self, global_group_id: UUID):
        return str(global_group_id) if global_group_id else None