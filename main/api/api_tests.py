from main import main
from main.schemas.tests import QuestionDefault


@main.get('/api/questions', status_code=200, tags=["Tests"], response_model=QuestionDefault)
async def api_get_questions():
    """
        Этот метод предназначен для выведения всех существующих вопросов для прохождения теста школьником.
    """
    from main.utils.tests import get_questions
    return QuestionDefault(data=await get_questions())
