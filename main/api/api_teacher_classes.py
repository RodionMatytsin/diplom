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
    from fastapi import HTTPException
    if not current_user.is_teacher:
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': 'К сожалению, вы не можете получить данные, потому что вы не преподаватель!',
                'data': {}
            }
        )
    from main.utils.teacher_classes import get_teacher_classes
    return TeacherClassDefault(data=await get_teacher_classes(user_guid=current_user.guid))
