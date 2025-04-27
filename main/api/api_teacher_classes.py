from main import main
from fastapi import Depends
from main.schemas.teacher_classes import TeacherClassDefault, TeacherClassWithSchoolchildrenDefault, EstimationUpdate
from main.schemas.responses import DefaultResponse
from main.utils.users import get_current_user
from uuid import UUID


@main.get(
    '/api/teacher_classes',
    status_code=200,
    tags=["TeacherClasses"],
    response_model=TeacherClassDefault
)
async def api_get_teacher_classes(current_user=Depends(get_current_user)):
    from main.utils.teacher_classes import get_teacher_classes, required_teacher_access
    await required_teacher_access(current_user=current_user)
    return TeacherClassDefault(data=await get_teacher_classes(user_guid=current_user.guid))


@main.get(
    '/api/teacher_classes/{class_guid}/schoolchildren',
    status_code=200,
    tags=["TeacherClasses"],
    response_model=TeacherClassWithSchoolchildrenDefault
)
async def api_get_teacher_class_with_schoolchildren(class_guid: UUID | str, current_user=Depends(get_current_user)):
    """
        Этот метод предназначен для преподавателя, с помощью которого он получает свои классы в которых он состоит.
    """
    from main.utils.teacher_classes import required_teacher_access, get_teacher_class_with_schoolchildren
    await required_teacher_access(current_user=current_user)
    return TeacherClassWithSchoolchildrenDefault(
        data=await get_teacher_class_with_schoolchildren(
            class_guid=class_guid
        )
    )


@main.patch(
    '/api/teacher_classes/estimation',
    status_code=200,
    tags=["TeacherClasses"],
    response_model=DefaultResponse
)
async def api_update_estimation_to_schoolchildren(
        estimation_update: EstimationUpdate,
        current_user=Depends(get_current_user)
):
    """
        Этот метод предназначен для преподавателя, с помощью которого он проставляет или обновляет школьнку
        его успеваемость в этом класса.
    """
    from main.utils.teacher_classes import required_teacher_access, update_estimation_to_schoolchildren
    await required_teacher_access(current_user=current_user)
    return DefaultResponse(message=await update_estimation_to_schoolchildren(estimation_update=estimation_update))
