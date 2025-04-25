from pydantic import BaseModel
from main.schemas.responses import DefaultResponse


class QuestionRegular(BaseModel):
    id: int
    name: str
    amount_of_points: int


class QuestionDefault(DefaultResponse):
    data: QuestionRegular | tuple[QuestionRegular] | tuple
