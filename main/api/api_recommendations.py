from main import main
from fastapi import Depends
from main.schemas.responses import DefaultResponse
from main.schemas.recommendations import RecommendationDefault
from main.utils.users import get_current_user
from uuid import UUID


@main.get(
    '/api/recommendations',
    status_code=200,
    tags=["Recommendations"],
    response_model=RecommendationDefault
)
async def api_get_recommendations(current_user=Depends(get_current_user)):
    """
        Этот метод предназначен для школьника, с помощью которого он получает все существующие на данный момент
        сформированные рекомендации по дате создания.
    """
    from main.utils.schoolchildren_classes import required_schoolchildren_access
    await required_schoolchildren_access(current_user=current_user)
    from main.utils.recommendations import get_recommendations
    return RecommendationDefault(data=await get_recommendations(user_guid=current_user.guid, is_accepted=True))


@main.post(
    '/api/recommendations/{recommendation_guid}/accept',
    status_code=200,
    tags=["Recommendations"],
    response_model=DefaultResponse
)
async def api_recommendation_accept(
        recommendation_guid: UUID | str,
        current_user=Depends(get_current_user)
):
    """
        Этот метод предназначен для преподавателя, с помощью которого можно
        принять ранее сформированную рекомендацию, чтобы показывать школьнику, админу и себе.
    """
    from main.utils.teacher_classes import required_teacher_access
    await required_teacher_access(current_user=current_user)
    from main.utils.recommendations import recommendation_accept
    return DefaultResponse(message=await recommendation_accept(recommendation_guid=recommendation_guid))


@main.post(
    '/api/recommendations/{recommendation_guid}/reject',
    status_code=200,
    tags=["Recommendations"],
    response_model=DefaultResponse
)
async def api_recommendation_reject(
        recommendation_guid: UUID | str,
        current_user=Depends(get_current_user)
):
    """
        Этот метод предназначен для преподавателя, с помощью которого можно
        отклонять ранее сформированную рекомендацию, чтобы не показывать школьнику, админу и себе.
    """
    from main.utils.teacher_classes import required_teacher_access
    await required_teacher_access(current_user=current_user)
    from main.utils.recommendations import recommendation_reject
    return DefaultResponse(message=await recommendation_reject(recommendation_guid=recommendation_guid))
