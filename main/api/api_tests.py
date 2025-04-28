from main import main
from fastapi import Depends
from main.schemas.tests import QuestionDefault
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


@main.post('/api/tests/{test_guid}', status_code=200, tags=["Tests"], response_model=DefaultResponse)
async def api_accept_changes_for_test(
        test_guid: UUID | str,
        current_user=Depends(get_current_user)
):
    """
        Этот метод предназначен для преподавателя, который принимает изменения для формирования рекомендации по тесту.
    """
    from main.utils.tests import accept_changes_for_test
    from main.utils.teacher_classes import required_teacher_access
    await required_teacher_access(current_user=current_user)
    return DefaultResponse(message=await accept_changes_for_test(test_guid=test_guid))
