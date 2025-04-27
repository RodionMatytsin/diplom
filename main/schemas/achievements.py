from uuid import UUID
from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from main.schemas.responses import DefaultResponse


class AchievementAdd(BaseModel):
    description: str

    @field_validator('description')
    def check_description_(cls, description_):
        if description_ is None or description_ == '':
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Наименование достижения» должно быть не пустым!', 'data': {}}
            )
        return description_


class AchievementRegular(BaseModel):
    achievement_guid: UUID | str
    description: str
    datetime_create: str


class AchievementDefault(DefaultResponse):
    data: AchievementRegular | tuple[AchievementRegular] | tuple
