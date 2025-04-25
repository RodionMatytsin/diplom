from main.models import engine, Questions, CRUD, SessionHandler
from main.schemas.tests import QuestionRegular


def serialize_question(question: Questions) -> QuestionRegular:
    return QuestionRegular(
        id=question.id,
        name=question.name,
        amount_of_points=question.amount_of_points
    )


async def get_questions() -> tuple[QuestionRegular] | tuple:

    questions: tuple[Questions] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Questions
    ).extended_query(
        _select=[
            Questions.id,
            Questions.name,
            Questions.amount_of_points
        ],
        _join=[],
        _where=[],
        _group_by=[],
        _order_by=[Questions.id, Questions.datetime_create],
        _all=True
    )

    if questions is None or questions == []:
        return tuple()
    return tuple(serialize_question(question=question) for question in questions)
