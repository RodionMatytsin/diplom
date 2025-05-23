from uuid import UUID
from pydantic import BaseModel
from main.schemas.responses import DefaultResponse


class RecommendationRegular(BaseModel):
    recommendation_guid: UUID | str
    description: str
    datetime_create: str
    is_neural: bool


class RecommendationDefault(DefaultResponse):
    data: RecommendationRegular | tuple[RecommendationRegular] | tuple
