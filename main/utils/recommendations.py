from main.models import Recommendations
from main.schemas.recommendations import RecommendationRegular
from uuid import UUID


def serialize_recommendation(recommendation: Recommendations) -> RecommendationRegular:
    return RecommendationRegular(
        recommendation_guid=recommendation.guid,
        description=recommendation.description,
        datetime_create=f"{recommendation.datetime_create.strftime('%d.%m.%Y')} в "
                        f"{recommendation.datetime_create.strftime('%H:%M')}"
    )


async def get_recommendations(
        recommendation_guid: UUID | str | None = None,
        user_guid: UUID | str | None = None,
        is_accepted: bool | None = None
) -> tuple[RecommendationRegular] | tuple:

    from main.models import engine, Tests, CRUD, SessionHandler
    from datetime import timedelta
    from sqlalchemy import func, desc

    where_ = [
        Recommendations.is_deleted == False,
        Recommendations.datetime_create >= (func.now().op('AT TIME ZONE')('Asia/Novosibirsk') - timedelta(days=182))
    ]
    if recommendation_guid is not None:
        where_.append(Recommendations.guid == recommendation_guid)
    if user_guid is not None:
        where_.append(Tests.user_guid == user_guid)
    if is_accepted is not None:
        where_.append(Recommendations.is_accepted == is_accepted)

    recommendations: tuple[Recommendations] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Recommendations
    ).extended_query(
        _select=[
            Recommendations.guid,
            Recommendations.description,
            Recommendations.datetime_create
        ],
        _join=[
            [Tests, Tests.guid == Recommendations.test_guid]
        ],
        _where=where_,
        _group_by=[],
        _order_by=[desc(Recommendations.datetime_create)],
        _all=True
    )

    if recommendations is None or recommendations == []:
        return tuple()
    return tuple(serialize_recommendation(recommendation=recommendation) for recommendation in recommendations)


async def recommendation_accept(recommendation_guid: UUID | str) -> str:
    from main.models import engine, Recommendations, CRUD, SessionHandler
    await CRUD(
        session=SessionHandler.create(engine=engine), model=Recommendations
    ).update(
        _where=[Recommendations.guid == recommendation_guid],
        _values=dict(is_accepted=True)
    )
    return "Вы успешно приняли сформированную рекомендацию для школьника!"


async def recommendation_reject(recommendation_guid: UUID | str) -> str:
    from main.models import engine, Recommendations, CRUD, SessionHandler
    await CRUD(
        session=SessionHandler.create(engine=engine), model=Recommendations
    ).update(
        _where=[Recommendations.guid == recommendation_guid],
        _values=dict(is_deleted=True)
    )
    return "Вы успешно отклонили сформированную рекомендацию для школьника!"


async def generated_recommendation_schoolchildren(
        test_guid: UUID | str,
        schoolchildren_class_guid: UUID | str
) -> str:
    from main.models import engine, Tests, AnswersTests, SchoolchildrenClasses, Recommendations, Questions,\
        CRUD, SessionHandler
    from fastapi import HTTPException

    current_schoolchildren_class: SchoolchildrenClasses | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
    ).read(
        _where=[
            SchoolchildrenClasses.guid == schoolchildren_class_guid,
            SchoolchildrenClasses.is_deleted == False
        ], _all=False
    )
    if current_schoolchildren_class.estimation is None:
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': f'Извините, но у данного школьника не проставлена оценка за успеваемость в этом классе, '
                           f'и по этой причине мы не можем продолжать формировать для него/нее рекомендацию!',
                'data': {}
            }
        )

    current_test: Tests | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Tests
    ).read(
        _where=[Tests.guid == test_guid], _all=False
    )
    if current_test is None:
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': f'Извините, но этот тест не был найден для дальнейшего формирования рекомендации '
                           f'для школьника!',
                'data': {}
            }
        )

    answers_test: list[AnswersTests] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=AnswersTests
    ).extended_query(
        _select=[
            Questions.id.label('question_id'),
            Questions.name.label('question_name'),
            AnswersTests.score,
            AnswersTests.comment
        ],
        _join=[
            [Questions, AnswersTests.question_id == Questions.id]
        ],
        _where=[
            AnswersTests.test_guid == current_test.guid
        ],
        _group_by=[],
        _order_by=[],
        _all=True
    )

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Recommendations
    ).create(
        _values=dict(
            test_guid=current_test.guid,
            schoolchildren_class_guid=current_schoolchildren_class.guid,
            description="фвыфвы фы ф фы выфв фывыфвфыыфв ф вфвфвфвф фвфв фв фвфв ф вфв фв фв фывфв фыывфвфвфф вф"
        )
    )

    return "Вы успешно сформировали рекомендацию для школьника!"
