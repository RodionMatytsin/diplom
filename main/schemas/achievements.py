from uuid import UUID
from pydantic import BaseModel


class AchievementAdd(BaseModel):
    user_guid: UUID | str
    description: str
