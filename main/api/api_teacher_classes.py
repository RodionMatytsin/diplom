from main import main
from fastapi import Depends
from main.schemas.teacher_classes import TeacherClassDefault, TeacherClassWithSchoolchildrenDefault, \
    EstimationUpdate, SchoolchildrenDetailsDefault
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
    """
        Этот метод предназначен для преподавателя, с помощью которого переходит в подробно о классе
        для просмотра всех состоящих в нем школьнико.
    """
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
            class_guid=class_guid,
            user_guid=current_user.guid
        )
    )


@main.get(
    '/api/teacher_classes/{class_guid}/schoolchildren/{schoolchildren_class_guid}',
    status_code=200,
    tags=["TeacherClasses"],
    response_model=SchoolchildrenDetailsDefault
)
async def api_get_schoolchildren_by_user_guid(
        class_guid: UUID | str,
        schoolchildren_class_guid: UUID | str,
        current_user=Depends(get_current_user)
):
    """
        Этот метод предназначен для преподавателя, с помощью которого он получает подробную инфу об школьнике.
    """
    from main.utils.teacher_classes import required_teacher_access, get_schoolchildren_by_user_guid
    await required_teacher_access(current_user=current_user)
    return SchoolchildrenDetailsDefault(
        data=await get_schoolchildren_by_user_guid(
            class_guid=class_guid,
            schoolchildren_class_guid=schoolchildren_class_guid
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


@main.post(
    '/api/teacher_classes/recommendations/{recommendation_guid}/accept',
    status_code=200,
    tags=["TeacherClasses"],
    response_model=DefaultResponse
)
async def api_teacher_accept_recommendation(
        recommendation_guid: UUID | str,
        current_user=Depends(get_current_user)
):
    """
        Этот метод предназначен для преподавателя, с помощью которого можно
        принять ранее сформированную рекомендацию, чтобы показывать школьнику, админу и себе.
    """
    from main.utils.teacher_classes import required_teacher_access, teacher_accept_recommendation
    await required_teacher_access(current_user=current_user)
    return DefaultResponse(message=await teacher_accept_recommendation(recommendation_guid=recommendation_guid))


@main.post(
    '/api/teacher_classes/recommendations/{recommendation_guid}/reject',
    status_code=200,
    tags=["TeacherClasses"],
    response_model=DefaultResponse
)
async def api_teacher_reject_recommendation(
        recommendation_guid: UUID | str,
        current_user=Depends(get_current_user)
):
    """
        Этот метод предназначен для преподавателя, с помощью которого можно
        отклонять ранее сформированную рекомендацию, чтобы не показывать школьнику, админу и себе.
    """
    from main.utils.teacher_classes import required_teacher_access, teacher_reject_recommendation
    await required_teacher_access(current_user=current_user)
    return DefaultResponse(message=await teacher_reject_recommendation(recommendation_guid=recommendation_guid))
