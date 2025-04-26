from uuid import UUID
from pydantic import BaseModel
from main.schemas.responses import DefaultResponse


class TeacherClassRegular(BaseModel):
    class_guid: UUID | str
    name_class: str


class TeacherClassDefault(DefaultResponse):
    data: TeacherClassRegular | tuple[TeacherClassRegular] | tuple
