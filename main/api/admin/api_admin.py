from main import main
from fastapi import Depends
from main.schemas.responses import DefaultResponse
from main.schemas.admin.admin import ClassAdd, ClassDefault
from main.schemas.teacher_classes import TeacherClassWithSchoolchildrenDefault
from main.utils.admin.admin import need_key
from uuid import UUID


@main.get('/api/admin/classes', status_code=200, tags=["Admin"], response_model=ClassDefault)
async def api_admin_get_classes(
        class_guid: UUID | str | None = None,
        key: str = Depends(need_key)
):
    from main.utils.admin.admin import get_classes_for_admin
    return ClassDefault(data=await get_classes_for_admin(class_guid=class_guid))


@main.post('/api/admin/classes', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_admin_create_class(
        class_add: ClassAdd,
        key: str = Depends(need_key)
):
    from main.utils.admin.admin import admin_add_new_class
    return DefaultResponse(message=await admin_add_new_class(name_class=class_add.name_class))


@main.delete('/api/admin/classes/{class_guid}', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_admin_del_class(
        class_guid: UUID | str,
        key: str = Depends(need_key)
):
    from main.utils.admin.admin import admin_del_class
    return DefaultResponse(message=await admin_del_class(class_guid=class_guid))


@main.get(
    '/api/admin/classes/{class_guid}/schoolchildren',
    status_code=200,
    tags=["Admin"],
    response_model=TeacherClassWithSchoolchildrenDefault
)
async def api_admin_get_teacher_class_with_schoolchildren(
        class_guid: UUID | str,
        key: str = Depends(need_key)
):
    from main.utils.teacher_classes import get_teacher_class_with_schoolchildren
    return TeacherClassWithSchoolchildrenDefault(
        data=await get_teacher_class_with_schoolchildren(class_guid=class_guid)
    )


@main.delete(
    '/api/admin/schoolchildren/{schoolchildren_class_guid}',
    status_code=200,
    tags=["Admin"],
    response_model=DefaultResponse
)
async def api_admin_del_schoolchildren_from_class(
        schoolchildren_class_guid: UUID | str,
        key: str = Depends(need_key)
):
    from main.utils.admin.admin import admin_del_schoolchildren_from_class
    return DefaultResponse(
        message=await admin_del_schoolchildren_from_class(schoolchildren_class_guid=schoolchildren_class_guid)
    )


@main.post('/api/admin/achievements/accept', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_admin_accept_achievement(
        achievement_guid: UUID | str,
        key: str = Depends(need_key)
):
    from main.utils.admin.admin import admin_accept_achievement
    return DefaultResponse(message=await admin_accept_achievement(achievement_guid=achievement_guid))


@main.post('/api/admin/achievements/reject', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_admin_reject_achievement(
        achievement_guid: UUID | str,
        key: str = Depends(need_key)
):
    from main.utils.admin.admin import admin_reject_achievement
    return DefaultResponse(message=await admin_reject_achievement(achievement_guid=achievement_guid))
