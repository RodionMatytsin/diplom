from main.models import Questions
from main.schemas.tests import QuestionRegular, TestRegular, ScoreTestAdd
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
    from main.models import engine, Tests, AnswersTests, Questions, CRUD, SessionHandler
    from main.schemas.tests import TestDetails
    from sqlalchemy import desc

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
        _order_by=[desc(Tests.datetime_create)],
        _all=True
    )

    if tests is None or tests == []:
        return tuple()

    result = []
    number_test = 1

    for test in tests:
        test_details: tuple[AnswersTests] | object | None = await CRUD(
            session=SessionHandler.create(engine=engine), model=AnswersTests
        ).extended_query(
            _select=[
                AnswersTests.question_id,
                Questions.name.label('question_name'),
                Questions.amount_of_points.label('question_amount_of_points'),
                AnswersTests.score,
                AnswersTests.comment
            ],
            _join=[
                [Tests, AnswersTests.test_guid == Tests.guid],
                [Questions, AnswersTests.question_id == Questions.id]
            ],
            _where=[
                AnswersTests.test_guid == test.guid
            ],
            _group_by=[],
            _order_by=[AnswersTests.datetime_create],
            _all=True
        )

        result.append(
            TestRegular(
                test_guid=test.guid,
                name_test=f"Тест №{number_test}",
                datetime_create=test.datetime_create.strftime('%d.%m.%Y в %H:%M'),
                is_accepted=test.is_accepted,
                test_details=tuple([
                    TestDetails(
                        question=QuestionRegular(
                            question_id=test_detail.question_id,
                            name=test_detail.question_name,
                            amount_of_points=test_detail.question_amount_of_points
                        ),
                        score=test_detail.score,
                        comment=test_detail.comment
                    ) for test_detail in test_details
                ])
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

        return "Вы успешно приняли изменения для последующего формирования рекомендации по этому тесту!"


async def add_test_to_schoolchildren(score_test: ScoreTestAdd, user_guid: UUID | str) -> str:
    from main.models import engine, Tests, AnswersTests, CRUD, SessionHandler
    from datetime import datetime, timedelta
    from fastapi import HTTPException
    from sqlalchemy import select

    one_year_ago = datetime.now() - timedelta(days=365)

    existing_test_query = select(Tests).where(
        Tests.user_guid == user_guid,
        Tests.datetime_create >= one_year_ago
    )

    existing_test: Tests | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Tests
    ).get(query=existing_test_query, _all=False)

    if existing_test is not None:
        datetime_test = existing_test.datetime_create + timedelta(days=365)
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': f'Вы уже проходили этот тест в течение последнего года. '
                           f'Вы сможете пройти его снова после '
                           f'{datetime_test.strftime("%d.%m.%Y")} {datetime_test.strftime("%H:%M")}!',
                'data': {}
            }
        )

    test: Tests | object = await CRUD(
        session=SessionHandler.create(engine=engine), model=Tests
    ).create(_values=dict(user_guid=user_guid))

    for i in score_test.details:
        await CRUD(
            session=SessionHandler.create(engine=engine), model=AnswersTests
        ).create(
            _values=dict(
                test_guid=test.guid,
                question_id=i.question_id,
                score=i.score,
                comment=i.comment
            )
        )

    return "Вы успешно отправили данные с оцененными ответами на вопросы этого теста!"
