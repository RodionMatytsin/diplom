from main import main
from fastapi import Depends
from main.schemas.schoolchildren_classes import SchoolchildrenClassDefault
from main.utils.users import get_current_user


@main.get(
    '/api/schoolchildren_classes',
    status_code=200,
    tags=["SchoolchildrenClasses"],
    response_model=SchoolchildrenClassDefault
)
async def api_get_schoolchildren_classes(current_user=Depends(get_current_user)):
    """
        Этот метод предназначен для школьника, с помощью которого он получает свои классы в которых он состоит.
    """
    from main.utils.schoolchildren_classes import required_schoolchildren_access, get_schoolchildren_classes
    await required_schoolchildren_access(current_user=current_user)
    return SchoolchildrenClassDefault(data=await get_schoolchildren_classes(user_guid=current_user.guid))
