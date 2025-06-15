from main import main
from fastapi import Depends
from main.schemas.responses import DefaultResponse
from main.schemas.admin.admin import (ClassAdd, ClassDefault, SchoolchildrenDetailsAdminDefault,
                                      UserRegularAdminDefault, UsersToClassAdminDefault)
from main.schemas.teacher_classes import TeacherClassWithSchoolchildrenDefault
from main.schemas.factors import FactorDefault, FactorUpdate
from main.utils.admin.admin import need_key
from uuid import UUID


@main.get('/api/admin/users', status_code=200, tags=["Admin"], response_model=UserRegularAdminDefault)
async def api_admin_get_users(
        is_teacher: bool = False,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, который отображает список всех существующих пользователей,
        в зависимости от его роли, а именно: школьник или преподаватель.
    """
    from main.utils.admin.admin import get_users_for_admin
    return UserRegularAdminDefault(data=await get_users_for_admin(is_teacher=is_teacher))


@main.get('/api/admin/classes', status_code=200, tags=["Admin"], response_model=ClassDefault)
async def api_admin_get_classes(
        class_guid: UUID | str | None = None,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, который отображает список всех существующих учебных классов.
    """
    from main.utils.admin.admin import get_classes_for_admin
    return ClassDefault(data=await get_classes_for_admin(class_guid=class_guid))


@main.post('/api/admin/classes', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_admin_create_class(
        class_add: ClassAdd,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, который создает учебный класс.
    """
    from main.utils.admin.admin import admin_add_new_class
    return DefaultResponse(message=await admin_add_new_class(name_class=class_add.name_class))


@main.delete('/api/admin/classes/{class_guid}', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_admin_del_class(
        class_guid: UUID | str,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, который удаляет учебный класс.
    """
    from main.utils.admin.admin import admin_del_class
    return DefaultResponse(message=await admin_del_class(class_guid=class_guid))


@main.get(
    '/api/admin/classes/{class_guid}/users',
    status_code=200,
    tags=["Admin"],
    response_model=UsersToClassAdminDefault
)
async def api_admin_get_users_to_class(
        class_guid: UUID | str,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, с помощью которого он получает списки пользователей, а именно:
        - список школьников, которых нет в этом учебном классе, но которые могут быть добавлены в этот класс;
        - список преподаватель, которые не назначены в этот класс, но могут быть назначены в этот класс;
        - список преподаватель, которые могут быть удалены из этого класса и они не смогут взаимодействовать
          в системе с данным учебным классов;
    """
    from main.utils.admin.admin import admin_get_users_to_class
    return UsersToClassAdminDefault(data=await admin_get_users_to_class(class_guid=class_guid))


@main.post(
    '/api/admin/classes/{class_guid}/users/{user_guid}',
    status_code=200,
    tags=["Admin"],
    response_model=DefaultResponse
)
async def api_admin_add_user_to_class(
        class_guid: UUID | str,
        user_guid: UUID | str,
        is_teacher: bool = False,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, с помощью которого он может добавлять нового ученика в
        учебный класс или назначать нового преподавателя для данного учебного класса.
    """
    from main.utils.admin.admin import admin_add_user_to_class
    return DefaultResponse(
        message=await admin_add_user_to_class(
            class_guid=class_guid,
            user_guid=user_guid,
            is_teacher=is_teacher
        )
    )


@main.delete(
    '/api/admin/classes/{class_guid}/users/{user_guid}',
    status_code=200,
    tags=["Admin"],
    response_model=DefaultResponse
)
async def api_admin_del_user_to_class(
        class_guid: UUID | str,
        user_guid: UUID | str,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, с помощью которого он может удалять определенного
        преподавателя из учебного класса.
    """
    from main.utils.admin.admin import admin_del_user_to_class
    return DefaultResponse(
        message=await admin_del_user_to_class(
            class_guid=class_guid,
            user_guid=user_guid
        )
    )


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
    """
        Этот метод предназначен для администратора, с помощью которого переходит в подробно о классе
        для просмотра всех состоящих в нем школьников.
    """
    from main.utils.admin.admin import get_teacher_class_with_schoolchildren_for_admin
    return TeacherClassWithSchoolchildrenDefault(
        data=await get_teacher_class_with_schoolchildren_for_admin(class_guid=class_guid)
    )


@main.delete(
    '/api/admin/classes/{class_guid}/schoolchildren/{schoolchildren_class_guid}',
    status_code=200,
    tags=["Admin"],
    response_model=DefaultResponse
)
async def api_admin_del_schoolchildren_from_class(
        class_guid: UUID | str,
        schoolchildren_class_guid: UUID | str,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, с помощью которого можно удалять школьника с определенного класса.
    """
    from main.utils.admin.admin import admin_del_schoolchildren_from_class
    return DefaultResponse(
        message=await admin_del_schoolchildren_from_class(
            class_guid=class_guid,
            schoolchildren_class_guid=schoolchildren_class_guid
        )
    )


@main.post(
    '/api/admin/achievements/{achievement_guid}/accept',
    status_code=200,
    tags=["Admin"],
    response_model=DefaultResponse
)
async def api_admin_accept_achievement(
        achievement_guid: UUID | str,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, с помощью которого можно
        принять добавленное достижение школьника.
    """
    from main.utils.admin.admin import admin_accept_achievement
    return DefaultResponse(message=await admin_accept_achievement(achievement_guid=achievement_guid))


@main.post(
    '/api/admin/achievements/{achievement_guid}/reject',
    status_code=200,
    tags=["Admin"],
    response_model=DefaultResponse
)
async def api_admin_reject_achievement(
        achievement_guid: UUID | str,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для администратора, с помощью которого можно
        отклонить добавленное достижение школьника.
    """
    from main.utils.admin.admin import admin_reject_achievement
    return DefaultResponse(message=await admin_reject_achievement(achievement_guid=achievement_guid))


@main.get(
    '/api/admin/classes/{class_guid}/schoolchildren/{schoolchildren_class_guid}',
    status_code=200,
    tags=["Admin"],
    response_model=SchoolchildrenDetailsAdminDefault
)
async def api_get_schoolchildren_by_user_guid_for_admin(
        class_guid: UUID | str,
        schoolchildren_class_guid: UUID | str,
        key: str = Depends(need_key)
):
    """
        Этот метод предназначен для админа, с помощью которого он получает подробную инфу об школьнике.
    """
    from main.utils.admin.admin import get_schoolchildren_by_user_guid_for_admin
    return SchoolchildrenDetailsAdminDefault(
        data=await get_schoolchildren_by_user_guid_for_admin(
            class_guid=class_guid,
            schoolchildren_class_guid=schoolchildren_class_guid
        )
    )


@main.get('/api/admin/factors', status_code=200, tags=["Admin"], response_model=FactorDefault)
async def api_get_factors(key: str = Depends(need_key)):
    """
        Этот метод предназначен для админа, с помощью которого можно получить существующие факторы и их веса.
    """
    from main.utils.admin.admin import get_factors
    return FactorDefault(data=await get_factors())


@main.patch('/api/admin/factors', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_set_factors(factors: FactorUpdate, key: str = Depends(need_key)):
    """
        Этот метод предназначен для админа, с помощью которого можно отредактировать веса существующих факторов.
    """
    from main.utils.admin.admin import set_factors
    return DefaultResponse(message=await set_factors(factors=factors))
