from pydantic import BaseModel, field_validator
from fastapi import HTTPException
from main.schemas.responses import DefaultResponse
from uuid import UUID


class QuestionRegular(BaseModel):
    question_id: int
    name: str
    amount_of_points: int


class QuestionDefault(DefaultResponse):
    data: QuestionRegular | tuple[QuestionRegular] | tuple


class ScoreTestDetail(BaseModel):
    question_id: int
    score: int
    comment: str | None = None

    @field_validator("score")
    def check_score_(cls, score_):
        if score_ == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    'result': False,
                    'message': 'Каждый вопрос должен быть оценен. '
                               'Пожалуйста, укажите ненулевую оценку для всех вопросов!',
                    'data': {}
                }
            )
        return score_

    @field_validator("comment")
    def check_comment_(cls, comment_):
        if comment_ == '' or comment_ is None:
            return None
        return comment_


class ScoreTestAdd(BaseModel):
    details: list[ScoreTestDetail]


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
