from main.models import engine, Recommendations, Tests, CRUD, SessionHandler
from main.schemas.recommendations import RecommendationRegular
from uuid import UUID


def serialize_recommendation(recommendation: Recommendations) -> RecommendationRegular:
    return RecommendationRegular(
        recommendation_guid=recommendation.guid,
        description=recommendation.description,
        datetime_create=f"{recommendation.datetime_create.strftime('%d.%m.%Y')} в "
                        f"{recommendation.datetime_create.strftime('%H:%M')}"
    )


async def get_recommendations(user_guid: UUID | str) -> tuple[RecommendationRegular] | tuple:

    from datetime import timedelta
    from sqlalchemy import func

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
        _where=[
            Tests.user_guid == user_guid,
            Recommendations.datetime_create >= (func.now().op('AT TIME ZONE')('Asia/Novosibirsk') - timedelta(days=182))
        ],
        _group_by=[],
        _order_by=[Recommendations.datetime_create],
        _all=True
    )

    if recommendations is None or recommendations == []:
        return tuple()
    return tuple(serialize_recommendation(recommendation=recommendation) for recommendation in recommendations)
