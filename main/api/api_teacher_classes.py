from main import main
from fastapi import Depends
from main.schemas.teacher_classes import TeacherClassDefault
from main.utils.users import get_current_user


@main.get(
    '/api/teacher_classes',
    status_code=200,
    tags=["TeacherClasses"],
    response_model=TeacherClassDefault
)
async def api_get_teacher_classes(current_user=Depends(get_current_user)):
    from main.utils.teacher_classes import get_teacher_classes
    return TeacherClassDefault(data=await get_teacher_classes(user_guid=current_user.guid))
