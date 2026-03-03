from typing import Union, List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

class PlanBase(BaseModel):
    global_group_id: Union[UUID, str]
    group_id: Union[UUID, str]
    subject_id: Union[UUID, str]
    event_id: Union[UUID, str]
    teacher_id: Union[UUID, str]
    priority: int
    event_format: str
    hours: int


class Plan(PlanBase):
    plan_id: Union[UUID, str]

    @field_serializer('plan_id')
    def serialize_plan_id(self, plan_id: UUID):
        return str(plan_id) if plan_id else None


class PlanAllData(Plan):
    group_name: Union[UUID, str]
    subject_name: Union[UUID, str]
    event_name: Union[UUID, str]
    teacher_name: Union[UUID, str]


class PlanGlobalGroup(BaseModel):
    plan_id: Union[UUID, str]
    global_group_id: Union[UUID, str]


class PlanGroup(BaseModel):
    group_id: Union[UUID, str]
    global_group_id: Union[UUID, str]