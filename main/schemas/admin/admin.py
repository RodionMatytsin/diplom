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
    user: UserRegular
    achievements: tuple[AchievementRegular] | tuple
    pending_achievements: tuple[AchievementRegular] | tuple
    recommendations: tuple[RecommendationRegular] | tuple
    tests: tuple[TestRegular] | tuple


class SchoolchildrenDetailsAdminDefault(DefaultResponse):
    data: SchoolchildrenDetailsAdmin
