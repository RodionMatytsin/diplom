from pydantic import BaseModel
from main.schemas.responses import DefaultResponse
from uuid import UUID


class QuestionRegular(BaseModel):
    question_id: int
    name: str
    amount_of_points: int


class QuestionDefault(DefaultResponse):
    data: QuestionRegular | tuple[QuestionRegular] | tuple


class TestDetails(BaseModel):
    question: QuestionRegular
    score: int
    comment: str | None


class TestRegular(BaseModel):
    test_guid: UUID | str
    name_test: str
    datetime_create: str
    is_accepted: bool
    test_details: tuple[TestDetails] | tuple
