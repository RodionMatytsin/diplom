from main import main
from fastapi import Depends
from main.schemas.recommendations import RecommendationDefault
from main.utils.users import get_current_user


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
    from main.utils.recommendations import get_recommendations
    await required_schoolchildren_access(current_user=current_user)
    return RecommendationDefault(data=await get_recommendations(user_guid=current_user.guid))
