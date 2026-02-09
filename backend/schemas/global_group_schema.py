from uuid import UUID
from typing import Union

from pydantic import BaseModel, Field, field_serializer

class GlobalGroupBase(BaseModel):
    name: str = Field(..., max_length=255)

class GlobalGroup(GlobalGroupBase):
    global_group_id: Union[UUID, str]

    @field_serializer('global_group_id')
    def serialize_global_group_id(self, global_group_id: UUID):
        return str(global_group_id) if global_group_id else None