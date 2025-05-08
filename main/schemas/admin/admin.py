from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from main.schemas.responses import DefaultResponse
from main.utils.validation import check_class
from main.schemas.users import UserRegular
from main.schemas.achievements import AchievementRegular
from main.schemas.recommendations import RecommendationRegular
from main.schemas.tests import TestRegular
from uuid import UUID


class ClassAdd(BaseModel):
    name_class: str

    @field_validator('name_class')
    def check_role_(cls, name_class_):
        name_class_ = check_class(name_class_=name_class_)
        if not name_class_:
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Название класса» введено некорректно!', 'data': {}}
            )
        return name_class_


class ClassRegular(BaseModel):
    guid: UUID | str
    name: str


class ClassDefault(DefaultResponse):
    data: ClassRegular | tuple[ClassRegular] | tuple


class SchoolchildrenDetailsAdmin(BaseModel):
    schoolchildren_class_guid: UUID | str
    user: UserRegular
    achievements: tuple[AchievementRegular] | tuple
    pending_achievements: tuple[AchievementRegular] | tuple
    recommendations: tuple[RecommendationRegular] | tuple
    tests: tuple[TestRegular] | tuple


class SchoolchildrenDetailsAdminDefault(DefaultResponse):
    data: SchoolchildrenDetailsAdmin


class AvailableSchoolchildrenAdmin(BaseModel):
    user_guid: UUID | str
    user_fio: str


class AvailableTeachersAdmin(BaseModel):
    user_guid: UUID | str
    user_fio: str


class AssignedTeachersAdmin(BaseModel):
    user_guid: UUID | str
    user_fio: str


class UsersToClassAdmin(BaseModel):
    available_schoolchildren: tuple[AvailableSchoolchildrenAdmin] | tuple
    available_teachers: tuple[AvailableTeachersAdmin] | tuple
    assigned_teachers: tuple[AssignedTeachersAdmin] | tuple


class UsersToClassAdminDefault(DefaultResponse):
    data: UsersToClassAdmin
