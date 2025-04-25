from main import main
from main.schemas.tests import QuestionDefault


@main.get('/api/questions', status_code=200, tags=["Tests"], response_model=QuestionDefault)
async def api_get_questions():
    from main.utils.tests import get_questions
    return QuestionDefault(data=await get_questions())
