from main.models import Recommendations
from main.schemas.recommendations import RecommendationRegular, RecommendationAdd, RecommendationUpdate
from uuid import UUID


def serialize_recommendation(recommendation: Recommendations) -> RecommendationRegular:
    return RecommendationRegular(
        recommendation_guid=recommendation.guid,
        description=recommendation.description,
        datetime_create=f"{recommendation.datetime_create.strftime('%d.%m.%Y')} в "
                        f"{recommendation.datetime_create.strftime('%H:%M')}",
        is_neural=recommendation.is_neural,
        is_accepted=recommendation.is_accepted
    )


async def get_recommendations(
        recommendation_guid: UUID | str | None = None,
        user_guid: UUID | str | None = None,
        is_accepted: bool | None = None
) -> tuple[RecommendationRegular] | RecommendationRegular | tuple:

    from main.models import engine, Users, CRUD, SessionHandler
    from datetime import timedelta
    from sqlalchemy import func, desc

    where_ = [
        Recommendations.is_deleted == False,
        Recommendations.datetime_create >= (func.now().op('AT TIME ZONE')('Asia/Novosibirsk') - timedelta(days=182))
    ]
    if recommendation_guid is not None:
        where_.append(Recommendations.guid == recommendation_guid)
    if user_guid is not None:
        where_.append(Users.guid == user_guid)
    if is_accepted is not None:
        where_.append(Recommendations.is_accepted == is_accepted)

    recommendations: tuple[Recommendations] | Recommendations | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Recommendations
    ).extended_query(
        _select=[
            Recommendations.guid,
            Recommendations.description,
            Recommendations.datetime_create,
            Recommendations.is_neural,
            Recommendations.is_accepted
        ],
        _join=[
            [Users, Users.guid == Recommendations.user_guid]
        ],
        _where=where_,
        _group_by=[],
        _order_by=[desc(Recommendations.datetime_create)],
        _all=recommendation_guid is None
    )

    if recommendations is None or recommendations == []:
        return tuple()

    if recommendation_guid is None:
        return tuple(serialize_recommendation(recommendation=recommendation) for recommendation in recommendations)
    return serialize_recommendation(recommendation=recommendations)


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


async def add_recommendation(recommendation: RecommendationAdd) -> str:
    from main.models import engine, CRUD, SessionHandler
    from main.utils.users import get_users_with_serialize

    current_user = await get_users_with_serialize(user_guid=recommendation.user_guid)

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Recommendations
    ).create(
        _values=dict(
            user_guid=current_user.guid,
            description=recommendation.description
        )
    )

    return "Вы успешно создали новую рекомендацию для школьника!"


async def set_recommendation(recommendation: RecommendationUpdate) -> str:
    from main.models import engine, CRUD, SessionHandler
    from main.utils.users import get_users_with_serialize

    current_user = await get_users_with_serialize(user_guid=recommendation.user_guid)
    current_recommendation = await get_recommendations(
        recommendation_guid=recommendation.recommendation_guid,
        user_guid=current_user.guid,
        is_accepted=False
    )
    if current_recommendation == tuple() or current_recommendation == []:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': f'Извините, но такой записи, по сформированной рекомендации для редактирование, нет!',
                'data': {}
            }
        )

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Recommendations
    ).update(
        _where=[Recommendations.guid == current_recommendation.recommendation_guid],
        _values=dict(
            user_guid=current_user.guid,
            description=recommendation.description
        )
    )

    return "Вы успешно отредактировали сформированную рекомендацию для школьника!"


async def generated_recommendation_schoolchildren(
        test_guid: UUID | str,
        schoolchildren_class_guid: UUID | str
) -> str:
    from main.models import engine, Tests, AnswersTests, SchoolchildrenClasses, SchoolchildrenScores,  Questions, \
        Factors, CRUD, SessionHandler
    from fastapi import HTTPException

    current_schoolchildren_class: SchoolchildrenClasses | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
    ).read(
        _where=[
            SchoolchildrenClasses.guid == schoolchildren_class_guid,
            SchoolchildrenClasses.is_deleted == False
        ], _all=False
    )
    if current_schoolchildren_class is None:
        raise HTTPException(
            status_code=409,
            detail={'result': False, 'message': f'Извините, но такой записи о школьнике не было найдено!', 'data': {}}
        )

    current_schoolchildren_scores: list[SchoolchildrenScores] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenScores
    ).extended_query(
        _select=[
            Factors.name,
            Factors.weight_factor,
            Factors.amount_of_points,
            SchoolchildrenScores.estimation
        ],
        _join=[
            [Factors, Factors.id == SchoolchildrenScores.factor_id]
        ],
        _where=[
            SchoolchildrenScores.schoolchildren_class_guid == current_schoolchildren_class.guid,
            Factors.for_the_teacher == True
        ],
        _all=True
    )

    missing_scores = [f"'{score.name}'" for score in current_schoolchildren_scores if score.estimation is None]
    if missing_scores:
        factors_list = missing_scores[0] if len(missing_scores) == 1 else ', '.join(missing_scores[:-1]) + (
            ' и ' + missing_scores[-1] if len(missing_scores) > 1 else ''
        )
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': f'Извините, но у данного школьника не проставлены оценки по следующим факторам: '
                           f'{factors_list}. По этой причине мы не можем продолжать формировать для него/нее '
                           f'рекомендацию!',
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

    current_answers_test: list[AnswersTests] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=AnswersTests
    ).extended_query(
        _select=[
            Factors.name,
            Factors.weight_factor,
            Factors.amount_of_points,
            Questions.name,
            AnswersTests.score,
            AnswersTests.comment
        ],
        _join=[
            [Questions, AnswersTests.question_id == Questions.id],
            [Factors, Factors.id == Questions.factor_id]
        ],
        _where=[
            AnswersTests.test_guid == current_test.guid,
            Factors.for_the_teacher == False
        ],
        _group_by=[],
        _order_by=[],
        _all=True
    )

    def calculate_recommendation(
            schoolchildren_scores: list[SchoolchildrenScores],
            answers_test: list[AnswersTests]
    ) -> float:
        def normalize(value: int, min_value: int, max_value: int):
            return (value - min_value) / (max_value - min_value)

        normalized_grade = normalize(
            value=int(schoolchildren_scores[0].estimation),
            min_value=2,
            max_value=int(schoolchildren_scores[0].amount_of_points)
        ) * schoolchildren_scores[0].weight_factor

        normalized_interest = normalize(
            value=int(schoolchildren_scores[1].estimation),
            min_value=1,
            max_value=int(schoolchildren_scores[1].amount_of_points)
        ) * schoolchildren_scores[1].weight_factor

        normalized_motivation = normalize(
            value=int(schoolchildren_scores[2].estimation),
            min_value=1,
            max_value=int(schoolchildren_scores[2].amount_of_points)
        ) * schoolchildren_scores[2].weight_factor

        normalized_definiteness = normalize(
            value=int(answers_test[0].score),
            min_value=1,
            max_value=int(answers_test[0].amount_of_points)
        ) * answers_test[0].weight_factor

        normalized_comfort = normalize(
            value=int(answers_test[1].score),
            min_value=1,
            max_value=int(answers_test[1].amount_of_points)
        ) * answers_test[1].weight_factor

        normalized_financial = normalize(
            value=int(answers_test[2].score),
            min_value=1,
            max_value=int(answers_test[2].amount_of_points)
        ) * answers_test[2].weight_factor

        normalized_relationships = normalize(
            value=int(schoolchildren_scores[3].estimation),
            min_value=1,
            max_value=int(schoolchildren_scores[3].amount_of_points)
        ) * schoolchildren_scores[3].weight_factor

        normalized_teaching_quality = normalize(
            value=int(answers_test[3].score),
            min_value=1,
            max_value=int(answers_test[3].amount_of_points)
        ) * answers_test[3].weight_factor

        normalized_methodical_quality = normalize(
            value=int(answers_test[4].score),
            min_value=1,
            max_value=int(answers_test[4].amount_of_points)
        ) * answers_test[4].weight_factor

        normalized_material_quality = normalize(
            value=int(answers_test[5].score),
            min_value=1,
            max_value=int(answers_test[5].amount_of_points)
        ) * answers_test[5].weight_factor

        normalized_prestige = normalize(
            value=int(answers_test[6].score),
            min_value=1,
            max_value=int(answers_test[6].amount_of_points)
        ) * answers_test[6].weight_factor

        normalized_extracurricular = normalize(
            value=int(answers_test[7].score),
            min_value=1,
            max_value=int(answers_test[7].amount_of_points)
        ) * answers_test[7].weight_factor

        normalized_personal_capabilities = normalize(
            value=int(answers_test[8].score),
            min_value=1,
            max_value=int(answers_test[8].amount_of_points)
        ) * answers_test[8].weight_factor

        normalized_goals = normalize(
            value=int(answers_test[9].score),
            min_value=1,
            max_value=int(answers_test[9].amount_of_points)
        ) * answers_test[9].weight_factor

        target_function = (
                normalized_grade + normalized_interest + normalized_motivation - normalized_definiteness +
                normalized_comfort + normalized_financial + normalized_relationships + normalized_teaching_quality +
                normalized_methodical_quality + normalized_material_quality + normalized_prestige -
                normalized_extracurricular + normalized_personal_capabilities + normalized_goals
        )

        return target_function

    def generate_recommendation_text(target_function: float) -> str:
        import random
        if target_function > 0.7:
            recommendations = [
                "У вас высокий интерес к учебе. Рекомендуем рассмотреть карьеру в программировании или дизайне.",
                "Ваши достижения впечатляют! Возможно, вам стоит рассмотреть изучение наук или технологий.",
                "Вы проявляете большой интерес к учебе. Рекомендуем обратить внимание на курсы по "
                "математике или информатике."
            ]
            description_recommendation = random.choice(recommendations)
        elif target_function > 0.5:
            recommendations = [
                "Ваши результаты показывают средний интерес. Возможно, стоит обратить внимание на "
                "дополнительные занятия в области искусства или технологий.",
                "Вы на правильном пути! Рекомендуем рассмотреть занятия по графическому дизайну или музыке.",
                "Ваши результаты неплохие. Попробуйте уделить больше времени на изучение языков или истории."
            ]
            description_recommendation = random.choice(recommendations)
        else:
            recommendations = [
                "Вам стоит обратить внимание на развитие ваших интересов. Рекомендуем попробовать "
                "занятия по рукоделию или спорту.",
                "Не отчаивайтесь! Возможно, стоит попробовать что-то новое, например, занятия по театру или танцам.",
                "Рекомендуем обратить внимание на хобби, которые могут вас заинтересовать, например, "
                "рисование или спорт."
            ]
            description_recommendation = random.choice(recommendations)
        return description_recommendation

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Recommendations
    ).create(
        _values=dict(
            user_guid=current_schoolchildren_class.user_guid,
            description=generate_recommendation_text(
                target_function=calculate_recommendation(
                    schoolchildren_scores=current_schoolchildren_scores,
                    answers_test=current_answers_test
                )
            ),
            is_neural=True
        )
    )

    return "Вы успешно сформировали рекомендацию для школьника!"
