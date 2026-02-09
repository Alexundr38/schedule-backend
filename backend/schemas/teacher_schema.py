from pydantic import BaseModel, Field

class TeacherBase(BaseModel):
    name: str = Field(..., max_length=255)

class Teacher(TeacherBase):
    id: str