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
    from sqlalchemy import func

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
        _order_by=[Recommendations.datetime_create],
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
