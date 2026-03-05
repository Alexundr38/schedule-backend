from typing import List

from pydantic import BaseModel

class ParsedPlan(BaseModel):
    thema_name: str
    hours: int
    format_name: str
    subject_name: str


class SubjectHours(BaseModel):
    subject_name: str
    hours: int


class ParsedExcel(BaseModel):
    subjects: List[SubjectHours]
    format_names: List[str]
    lessons: List[ParsedPlan]
    sum_hours: int