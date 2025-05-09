from main.models import Questions
from main.schemas.tests import QuestionRegular, TestRegular, TestDetails
from uuid import UUID


def serialize_question(question: Questions) -> QuestionRegular:
    return QuestionRegular(
        question_id=question.id,
        name=question.name,
        amount_of_points=question.amount_of_points
    )


async def get_questions() -> tuple[QuestionRegular] | tuple:
    from main.models import engine, CRUD, SessionHandler

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


async def get_tests(user_guid: UUID | str) -> tuple[TestRegular] | tuple:
    from main.models import engine, Tests, CRUD, SessionHandler

    tests: tuple[Tests] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Questions
    ).extended_query(
        _select=[
            Tests.guid,
            Tests.datetime_create,
            Tests.is_accepted
        ],
        _join=[],
        _where=[
            Tests.user_guid == user_guid
        ],
        _group_by=[],
        _order_by=[Tests.datetime_create],
        _all=True
    )

    if tests is None or tests == []:
        return tuple()

    result = []
    number_test = 1

    for test in tests:
        result.append(
            TestRegular(
                test_guid=test.guid,
                name_test=f"Тест №{number_test}",
                datetime_create=f"{test.datetime_create.strftime('%d.%m.%Y')} в "
                                f"{test.datetime_create.strftime('%H:%M')}",
                is_accepted=test.is_accepted,
                test_details=tuple()
            )
        )
        number_test += 1

    return tuple(result)


async def update_test(test_guid: UUID | str, user_guid: UUID | str, is_accepted: bool):
    from main.models import engine, Tests, CRUD, SessionHandler
    await CRUD(
        session=SessionHandler.create(engine=engine), model=Tests
    ).update(
        _where=[Tests.guid == test_guid, Tests.user_guid == user_guid],
        _values=dict(is_accepted=is_accepted)
    )


async def accept_changes_for_test(test_guid: UUID | str, user_guid: UUID | str) -> str:
    from main.models import engine, Tests, CRUD, SessionHandler

    current_test: Tests | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Tests
    ).read(
        _where=[Tests.guid == test_guid, Tests.user_guid == user_guid], _all=False
    )

    if current_test is not None:

        await update_test(test_guid=current_test.guid, user_guid=current_test.user_guid, is_accepted=True)

        tests: tuple[Tests] | object | None = await CRUD(
            session=SessionHandler.create(engine=engine), model=Tests
        ).read(
            _where=[Tests.guid != current_test.guid, Tests.user_guid == current_test.user_guid], _all=True
        )

        if tests is not None:
            for test in tests:
                await update_test(test_guid=test.guid, user_guid=test.user_guid, is_accepted=False)

        return "Вы успешно приняли изменения для последующего формирования рекомендации по тесту!"
