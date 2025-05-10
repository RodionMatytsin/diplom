from main import main
from fastapi import Depends
from main.schemas.tests import QuestionDefault, ScoreTestAdd
from main.schemas.responses import DefaultResponse
from main.utils.users import get_current_user
from uuid import UUID


@main.get('/api/questions', status_code=200, tags=["Tests"], response_model=QuestionDefault)
async def api_get_questions():
    """
        Этот метод предназначен для выведения всех существующих вопросов для прохождения теста школьником.
    """
    from main.utils.tests import get_questions
    return QuestionDefault(data=await get_questions())


@main.post('/api/tests', status_code=200, tags=["Tests"], response_model=DefaultResponse)
async def api_add_test_to_schoolchildren(
        score_test: ScoreTestAdd,
        current_user=Depends(get_current_user)
):
    """
        Этот метод предназначен для школьника, который создает запись о выполненного теста с оценками
        и ответами на вопросы (можно проходить раз в год).
    """
    from main.utils.tests import add_test_to_schoolchildren
    from main.utils.schoolchildren_classes import required_schoolchildren_access
    await required_schoolchildren_access(current_user=current_user)
    return DefaultResponse(message=await add_test_to_schoolchildren(score_test=score_test, user_guid=current_user.guid))


@main.patch('/api/tests/{test_guid}/users/{user_guid}', status_code=200, tags=["Tests"], response_model=DefaultResponse)
async def api_accept_changes_for_test(
        test_guid: UUID | str,
        user_guid: UUID | str,
        current_user=Depends(get_current_user)
):
    """
        Этот метод предназначен для преподавателя, который принимает изменения для формирования рекомендации
        по тесту у конкретного школьника.
    """
    from main.utils.tests import accept_changes_for_test
    from main.utils.teacher_classes import required_teacher_access
    await required_teacher_access(current_user=current_user)
    return DefaultResponse(message=await accept_changes_for_test(test_guid=test_guid, user_guid=user_guid))
