from uuid import UUID
from pydantic import BaseModel, field_validator
from main.schemas.responses import DefaultResponse
from fastapi import HTTPException


class Recommendation(BaseModel):
    user_guid: UUID | str
    description: str

    @field_validator('description')
    def check_recommendation_description_(cls, description_):
        if description_ is None or description_ == '':
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Описание рекомендации» должно быть не пустым!', 'data': {}}
            )
        if not (12 <= len(description_) <= 250):
            raise HTTPException(
                status_code=400,
                detail={
                    'result': False,
                    'message': 'Поле «Описание рекомендации» должно содержать от 8 до 250 символов!',
                    'data': {}
                }
            )
        return description_


class RecommendationAdd(Recommendation):
    pass


class RecommendationUpdate(Recommendation):
    recommendation_guid: UUID | str


class RecommendationRegular(BaseModel):
    recommendation_guid: UUID | str
    description: str
    datetime_create: str
    is_neural: bool
    is_accepted: bool


class RecommendationDefault(DefaultResponse):
    data: RecommendationRegular | tuple[RecommendationRegular] | tuple
