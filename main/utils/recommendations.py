from main.models import Recommendations
from main.schemas.recommendations import RecommendationRegular
from uuid import UUID


def serialize_recommendation(recommendation: Recommendations) -> RecommendationRegular:
    return RecommendationRegular(
        recommendation_guid=recommendation.guid,
        description=recommendation.description,
        datetime_create=f"{recommendation.datetime_create.strftime('%d.%m.%Y')} в "
                        f"{recommendation.datetime_create.strftime('%H:%M')}",
        is_neural=recommendation.is_neural
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
            Recommendations.is_neural
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


async def generated_recommendation_schoolchildren(
        test_guid: UUID | str,
        schoolchildren_class_guid: UUID | str
) -> str:
    from main.models import engine, Tests, AnswersTests, SchoolchildrenClasses, Questions, CRUD, SessionHandler
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

    current_answers_test: list[AnswersTests] | object | None = await CRUD(
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

    def calculate_recommendation(
            schoolchildren_class: SchoolchildrenClasses,
            answers_test: list[AnswersTests]
    ) -> float:
        def normalize(value: int, min_value: int, max_value: int):
            return (value - min_value) / (max_value - min_value)

        normalized_grade = normalize(int(schoolchildren_class.estimation), 2, 5) * 0.1
        normalized_interest = normalize(int(answers_test[0].score), 1, 10) * 0.15
        normalized_motivation = normalize(int(answers_test[1].score), 1, 10) * 0.1
        normalized_definiteness = normalize(int(answers_test[2].score), 1, 10) * 0.05
        normalized_comfort = normalize(int(answers_test[3].score), 1, 5) * 0.05
        normalized_financial = normalize(int(answers_test[4].score), 1, 5) * 0.05
        normalized_relationships = normalize(int(answers_test[5].score), 1, 5) * 0.05
        normalized_teaching_quality = normalize(int(answers_test[6].score), 1, 10) * 0.05
        normalized_methodical_quality = normalize(int(answers_test[7].score), 1, 10) * 0.05
        normalized_material_quality = normalize(int(answers_test[8].score), 1, 5) * 0.05
        normalized_prestige = normalize(int(answers_test[9].score), 1, 5) * 0.05
        normalized_extracurricular = normalize(int(answers_test[10].score), 1, 10) * 0.1
        normalized_personal_capabilities = normalize(int(answers_test[11].score), 1, 10) * 0.1
        normalized_goals = normalize(int(answers_test[12].score), 1, 5) * 0.05

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
                    schoolchildren_class=current_schoolchildren_class,
                    answers_test=current_answers_test
                )
            ),
            is_neural=True
        )
    )

    return "Вы успешно сформировали рекомендацию для школьника!"
