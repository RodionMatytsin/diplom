from uuid import UUID
from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from main.schemas.responses import DefaultResponse


class AchievementAdd(BaseModel):
    attachment_guid: UUID | str
    description: str

    @field_validator('description')
    def check_description_(cls, description_):
        if description_ is None or description_ == '':
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Наименование достижения» должно быть не пустым!', 'data': {}}
            )
        if not (12 <= len(description_) <= 250):
            raise HTTPException(
                status_code=400,
                detail={
                    'result': False,
                    'message': 'Поле «Наименование достижения» должно содержать от 8 до 250 символов!',
                    'data': {}
                }
            )
        return description_


class AchievementRegular(BaseModel):
    achievement_guid: UUID | str
    attachment_guid: UUID | str
    description: str
    datetime_create: str
    is_accepted: bool


class AchievementDefault(DefaultResponse):
    data: AchievementRegular | tuple[AchievementRegular] | tuple
