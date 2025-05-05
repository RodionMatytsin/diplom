from main.models import Classes
from main.schemas.teacher_classes import TeacherClassWithSchoolchildrenRegular
from main.schemas.admin.admin import ClassRegular, SchoolchildrenDetailsAdmin
from uuid import UUID


async def need_key(key: str):
    from main.config import SECRET_KEY
    from fastapi import HTTPException
    if key != SECRET_KEY:
        raise HTTPException(
            status_code=403,
            detail={"result": False, "message": "Нет прав", "data": {}}
        )


def serialize_class(class_: Classes) -> ClassRegular:
    return ClassRegular(
        guid=class_.guid,
        name=class_.name
    )


async def get_classes_for_admin(
        class_guid: UUID | str | None = None
) -> ClassRegular | tuple[ClassRegular] | tuple:

    from main.models import engine, CRUD, SessionHandler

    where_ = [Classes.is_deleted == False]
    if class_guid is not None:
        where_.append(Classes.guid == class_guid)

    classes: Classes | tuple[Classes] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Classes
    ).read(
        _where=where_, _all=class_guid is None
    )

    if classes is None or classes == []:
        return tuple()

    if class_guid is None:
        return tuple(serialize_class(class_=class_) for class_ in classes)
    return serialize_class(class_=classes)


async def admin_add_new_class(name_class: str) -> str:
    from main.models import engine, CRUD, SessionHandler

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Classes
    ).create(
        _values=dict(name=name_class)
    )

    return "Вы успешно создали новый учебный класс!"


async def admin_del_class(class_guid: UUID | str) -> str:
    from main.models import engine, SchoolchildrenClasses, TeacherClasses, CRUD, SessionHandler

    await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
    ).update(
        _where=[SchoolchildrenClasses.class_guid == class_guid], _values=dict(is_deleted=True)
    )

    await CRUD(
        session=SessionHandler.create(engine=engine), model=TeacherClasses
    ).delete(_where=[TeacherClasses.class_guid == class_guid])

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Classes
    ).update(
        _where=[Classes.guid == class_guid], _values=dict(is_deleted=True)
    )

    return "Вы успешно удалили учебный класс!"


async def get_teacher_class_with_schoolchildren_for_admin(
        class_guid: UUID | str
) -> TeacherClassWithSchoolchildrenRegular | tuple:
    from main.models import engine, CRUD, SessionHandler

    class_: Classes | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Classes
    ).read(
        _where=[Classes.is_deleted == False, Classes.guid == class_guid], _all=False
    )
    if class_ is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': 'К сожалению, такого учебного класса просто не существует!',
                'data': {}
            }
        )

    from main.utils.teacher_classes import get_schoolchildren, serialize_teacher_class_with_schoolchildren
    return await serialize_teacher_class_with_schoolchildren(
        class_guid=class_.guid,
        name_class=class_.name,
        schoolchildren=await get_schoolchildren(class_guid=class_.guid)
    )


async def admin_del_schoolchildren_from_class(
        class_guid: UUID | str,
        schoolchildren_class_guid: UUID | str
) -> str:
    from main.models import engine, SchoolchildrenClasses, CRUD, SessionHandler
    from main.utils.schoolchildren_classes import get_schoolchildren

    await get_schoolchildren(class_guid=class_guid, schoolchildren_class_guid=schoolchildren_class_guid)

    await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
    ).update(
        _where=[
            SchoolchildrenClasses.guid == schoolchildren_class_guid,
            SchoolchildrenClasses.class_guid == class_guid
        ],
        _values=dict(is_deleted=True)
    )

    return "Вы успешно удалили школьника с класса!"


async def admin_accept_achievement(achievement_guid: UUID | str) -> str:
    from main.models import engine, Achievements, CRUD, SessionHandler
    await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).update(
        _where=[Achievements.guid == achievement_guid],
        _values=dict(is_accepted=True)
    )
    return "Вы успешно приняли достижение школьника!"


async def admin_reject_achievement(achievement_guid: UUID | str) -> str:
    from main.models import engine, Achievements, CRUD, SessionHandler
    await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).update(
        _where=[Achievements.guid == achievement_guid],
        _values=dict(is_deleted=True)
    )
    return "Вы успешно отклонили достижение школьника!"


async def get_schoolchildren_by_user_guid_for_admin(
        class_guid: UUID | str,
        schoolchildren_class_guid: UUID | str,
) -> SchoolchildrenDetailsAdmin:

    from main.utils.users import get_users_with_serialize
    from main.utils.achievements import get_achievements
    from main.utils.recommendations import get_recommendations
    from main.utils.schoolchildren_classes import get_schoolchildren
    from main.utils.tests import get_tests

    schoolchildren = await get_schoolchildren(
        class_guid=class_guid,
        schoolchildren_class_guid=schoolchildren_class_guid
    )

    current_user = await get_users_with_serialize(user_guid=schoolchildren.user_guid)

    return SchoolchildrenDetailsAdmin(
        schoolchildren_class_guid=schoolchildren.guid,
        user=current_user,
        achievements=await get_achievements(user_guid=current_user.guid, is_accepted=True),
        pending_achievements=await get_achievements(user_guid=current_user.guid, is_accepted=False),
        recommendations=await get_recommendations(user_guid=current_user.guid, is_accepted=True),
        tests=await get_tests(user_guid=current_user.guid)
    )
