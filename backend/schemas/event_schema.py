from typing import Union
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class EventBase(BaseModel):
    name: str = Field(..., max_length=255)


class Event(EventBase):
    event_id: Union[UUID, str]

    @field_serializer('event_id')
    def serialize_event_id(self, event_id: UUID):
        return str(event_id) if event_id else None


class EventCreate(EventBase):
    global_group_id: str


class EventGlobalGroup(Event):
    global_group_id: Union[UUID, str]

    @field_serializer('global_group_id')
    def serialize_global_group_id(self, global_group_id: UUID):
        return str(global_group_id) if global_group_id else None