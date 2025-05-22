from main import main
from fastapi import Depends
from main.schemas.responses import DefaultResponse
from main.schemas.achievements import AchievementDefault, AchievementAdd
from main.utils.users import get_current_user


@main.get('/api/achievements', status_code=200, tags=["Achievements"], response_model=AchievementDefault)
async def api_get_achievements(current_user=Depends(get_current_user)):
    """
        Этот метод предназначен для школьника, с помощью которого можно получить свои личные достижения.
    """
    from main.utils.schoolchildren_classes import required_schoolchildren_access
    await required_schoolchildren_access(current_user=current_user)
    from main.utils.achievements import get_achievements
    return AchievementDefault(data=await get_achievements(user_guid=current_user.guid, is_accepted=True))


@main.post('/api/achievements', status_code=200, tags=["Achievements"], response_model=DefaultResponse)
async def api_create_achievement(achievement: AchievementAdd, current_user=Depends(get_current_user)):
    """
        Этот метод предназначен для школьника, с помощью которого можно добавить новое личное достижение.
    """
    from main.utils.schoolchildren_classes import required_schoolchildren_access
    await required_schoolchildren_access(current_user=current_user)
    from main.utils.achievements import add_achievement
    return DefaultResponse(
        message=await add_achievement(
            attachment_guid=achievement.attachment_guid,
            description=achievement.description,
            user_guid=current_user.guid
        )
    )
