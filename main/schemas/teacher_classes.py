from uuid import UUID
from pydantic import BaseModel
from main.schemas.responses import DefaultResponse


class TeacherClassRegular(BaseModel):
    class_guid: UUID | str
    name_class: str


class TeacherClassDefault(DefaultResponse):
    data: TeacherClassRegular | tuple[TeacherClassRegular] | tuple


class Schoolchildren(BaseModel):
    schoolchildren_class_guid: UUID | str
    user_guid: UUID | str
    user_fio: str
    estimation: float | None
    datetime_estimation_update: str | None


class TeacherClassWithSchoolchildrenRegular(BaseModel):
    name_class: str
    schoolchildren: tuple[Schoolchildren] | tuple


class TeacherClassWithSchoolchildrenDefault(DefaultResponse):
    data: TeacherClassWithSchoolchildrenRegular


class EstimationUpdate(BaseModel):
    schoolchildren_class_guid: UUID | str
    estimation: float | None
