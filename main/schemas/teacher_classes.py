from uuid import UUID
from pydantic import BaseModel, field_validator
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

    @field_validator('estimation')
    def check_estimation_(cls, estimation_):
        if estimation_ is None or estimation_ == '':
            return None
        return estimation_
