from uuid import UUID
from pydantic import BaseModel
from main.schemas.responses import DefaultResponse


class TeacherClassRegular(BaseModel):
    class_guid: UUID | str
    name_class: str


class TeacherClassDefault(DefaultResponse):
    data: TeacherClassRegular | tuple[TeacherClassRegular] | tuple


class TeacherClassWithSchoolchildrenRegular(BaseModel):
    schoolchildren_class_guid: UUID | str
    user_guid: UUID | str
    user_fio: str
    estimation: float | None
    datetime_estimation_update: str | None


class TeacherClassWithSchoolchildrenDefault(DefaultResponse):
    data: TeacherClassWithSchoolchildrenRegular | tuple[TeacherClassWithSchoolchildrenRegular] | tuple
