from uuid import UUID
from pydantic import BaseModel
from main.schemas.responses import DefaultResponse


class AchievementAdd(BaseModel):
    description: str


class AchievementRegular(BaseModel):
    guid: UUID | str
    description: str
    datetime_create: str


class AchievementDefault(DefaultResponse):
    data: AchievementRegular | tuple[AchievementRegular] | tuple
