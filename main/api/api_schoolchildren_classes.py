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
    from main.utils.schoolchildren_classes import get_schoolchildren_classes
    return SchoolchildrenClassDefault(data=await get_schoolchildren_classes(user_guid=current_user.guid))
