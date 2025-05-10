from main.models import Classes, Users
from main.schemas.teacher_classes import TeacherClassWithSchoolchildrenRegular
from main.schemas.admin.admin import ClassRegular, SchoolchildrenDetailsAdmin, UsersToClassAdmin, UserRegularAdmin
from uuid import UUID


async def need_key(key: str):
    from main.config import SECRET_KEY
    from fastapi import HTTPException
    if key != SECRET_KEY:
        raise HTTPException(
            status_code=403,
            detail={"result": False, "message": "Нет прав", "data": {}}
        )


def serialize_user_for_admin(user: Users, classes: tuple[Classes] | None) -> UserRegularAdmin:
    from main.schemas.users import BirthdayUser
    return UserRegularAdmin(
        guid=user.guid,
        login=user.login,
        hash_password=user.hash_password,
        phone_number=user.phone_number,
        fio=user.fio,
        birthday=BirthdayUser(
            day=f"0{user.birthday.day}" if user.birthday.day < 10 else f"{user.birthday.day}",
            month=f"0{user.birthday.month}" if user.birthday.month < 10 else f"{user.birthday.month}",
            year=f"{user.birthday.year}"
        ),
        gender=user.gender,
        datetime_create=f"{user.datetime_create.strftime('%d.%m.%Y')} в {user.datetime_create.strftime('%H:%M')}",
        is_teacher=user.is_teacher,
        classes=tuple([serialize_class(class_=class_) for class_ in classes]) if classes is not None else tuple()
    )


async def get_users_for_admin(is_teacher: bool = False) -> tuple[UserRegularAdmin] | tuple:

    from main.models import engine, SchoolchildrenClasses, TeacherClasses, CRUD, SessionHandler

    classes_model = TeacherClasses if is_teacher else SchoolchildrenClasses
    where_ = []
    if not is_teacher:
        where_ = [classes_model.is_deleted == False]

    users: tuple[Users] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Users
    ).extended_query(
        _select=[
            Users.guid,
            Users.login,
            Users.hash_password,
            Users.phone_number,
            Users.fio,
            Users.birthday,
            Users.gender,
            Users.datetime_create,
            Users.is_teacher
        ],
        _join=[],
        _where=[Users.is_teacher == is_teacher],
        _group_by=[],
        _order_by=[Users.datetime_create],
        _all=True
    )

    if users is None or users == []:
        return tuple()

    result = []
    for user in users:
        classes: tuple[Classes] | object | None = await CRUD(
            session=SessionHandler.create(engine=engine), model=classes_model
        ).extended_query(
            _select=[
                classes_model.class_guid.label('guid'),
                Classes.name
            ],
            _join=[
                [Classes, Classes.guid == classes_model.class_guid]
            ],
            _where=[
                classes_model.user_guid == user.guid,
                *where_
            ],
            _group_by=[],
            _order_by=[],
            _all=True
        )
        result.append(serialize_user_for_admin(user=user, classes=classes))
    return tuple(result)


def serialize_class(class_: Classes) -> ClassRegular:
    return ClassRegular(
        guid=class_.guid,
        name=class_.name
    )


async def get_classes_for_admin(
        class_guid: UUID | str | None = None,
        name_class: str | None = None
) -> ClassRegular | tuple[ClassRegular] | tuple:

    from main.models import engine, CRUD, SessionHandler

    where_ = [Classes.is_deleted == False]
    if class_guid is not None:
        where_.append(Classes.guid == class_guid)
    if name_class is not None:
        where_.append(Classes.name == name_class)

    classes: Classes | tuple[Classes] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Classes
    ).extended_query(
        _select=[
            Classes.guid,
            Classes.name
        ],
        _join=[],
        _where=where_,
        _group_by=[],
        _order_by=[Classes.datetime_create],
        _all=True
    )

    if classes is None or classes == []:
        return tuple()

    if class_guid is None:
        return tuple(serialize_class(class_=class_) for class_ in classes)
    return serialize_class(class_=classes)


async def admin_add_new_class(name_class: str) -> str:
    from main.models import engine, CRUD, SessionHandler

    if await get_classes_for_admin(name_class=name_class):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail={"result": False, "message": "Учебный класс с таким наименованием уже существует!", "data": {}}
        )

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


async def admin_get_users_to_class(class_guid: UUID | str) -> UsersToClassAdmin:
    from main.models import engine, TeacherClasses, SchoolchildrenClasses, CRUD, SessionHandler
    from main.schemas.admin.admin import AvailableSchoolchildrenAdmin, AvailableTeachersAdmin, AssignedTeachersAdmin
    from sqlalchemy import null, and_

    # Получаем список школьников, которых нет в данном классе
    list_available_schoolchildren: tuple[Users] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Users
    ).extended_query(
        _select=[
            Users.guid,
            Users.fio
        ],
        _join=[
            [
                SchoolchildrenClasses,
                and_(
                    Users.guid == SchoolchildrenClasses.user_guid,
                    SchoolchildrenClasses.class_guid == class_guid,
                    SchoolchildrenClasses.is_deleted == False
                )
            ]
        ],
        _where=[
            SchoolchildrenClasses.user_guid == null(),
            Users.is_teacher == False
        ],
        _group_by=[],
        _order_by=[Users.fio],
        _all=True
    )

    # Получаем список преподавателей, которые не назначены в этот класс
    list_available_teachers: tuple[Users] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Users
    ).extended_query(
        _select=[
            Users.guid,
            Users.fio
        ],
        _join=[
            [
                TeacherClasses,
                and_(
                    Users.guid == TeacherClasses.user_guid,
                    TeacherClasses.class_guid == class_guid
                )
            ]
        ],
        _where=[
            TeacherClasses.user_guid == null(),
            Users.is_teacher == True
        ],
        _group_by=[],
        _order_by=[Users.fio],
        _all=True
    )

    # Получаем список преподавателей, которые назначены в данный класс
    list_assigned_teachers: tuple[Users] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Users
    ).extended_query(
        _select=[
            Users.guid,
            Users.fio
        ],
        _join=[
            [
                TeacherClasses,
                and_(
                    Users.guid == TeacherClasses.user_guid,
                    TeacherClasses.class_guid == class_guid
                )
            ]
        ],
        _where=[
            TeacherClasses.user_guid != null(),
            Users.is_teacher == True
        ],
        _group_by=[],
        _order_by=[Users.fio],
        _all=True
    )

    return UsersToClassAdmin(
        available_schoolchildren=tuple(
            [
                AvailableSchoolchildrenAdmin(
                    user_guid=available_schoolchildren.guid,
                    user_fio=available_schoolchildren.fio
                ) for available_schoolchildren in list_available_schoolchildren
            ] if list_available_schoolchildren is not None else tuple()
        ),
        available_teachers=tuple(
            [
                AvailableTeachersAdmin(
                    user_guid=available_teachers.guid,
                    user_fio=available_teachers.fio
                ) for available_teachers in list_available_teachers
            ] if list_available_teachers is not None else tuple()
        ),
        assigned_teachers=tuple(
            [
                AssignedTeachersAdmin(
                    user_guid=assigned_teachers.guid,
                    user_fio=assigned_teachers.fio
                ) for assigned_teachers in list_assigned_teachers
            ] if list_assigned_teachers is not None else tuple()
        )
    )


async def admin_add_user_to_class(
        class_guid: UUID | str,
        user_guid: UUID | str,
        is_teacher: bool = False,
) -> str:
    from main.models import engine, CRUD, SessionHandler

    from main.utils.users import get_users_with_serialize
    current_user = await get_users_with_serialize(user_guid=user_guid, is_teacher=is_teacher)

    if current_user.is_teacher:
        from main.models import TeacherClasses

        current_teacher: TeacherClasses | object | None = await CRUD(
            session=SessionHandler.create(engine=engine), model=TeacherClasses
        ).read(
            _where=[TeacherClasses.class_guid == class_guid, TeacherClasses.user_guid == user_guid],
            _all=False
        )
        if current_teacher is not None:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=409,
                detail={
                    'result': False,
                    'message': 'К сожалению, данный преподаватель уже назначен на этот учебный класс!',
                    'data': {}
                }
            )

        await CRUD(
            session=SessionHandler.create(engine=engine), model=TeacherClasses
        ).create(
            _values=dict(class_guid=class_guid, user_guid=user_guid)
        )

        return "Вы успешно назначили преподавателя для этого учебного класса!"
    else:
        from main.models import SchoolchildrenClasses
        from main.utils.schoolchildren_classes import get_schoolboy

        if await get_schoolboy(class_guid=class_guid, user_guid=user_guid, with_exception=False) is not None:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=409,
                detail={
                    'result': False,
                    'message': 'К сожалению, данный школьник уже состоит в этом учебном классе!',
                    'data': {}
                }
            )

        await CRUD(
            session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
        ).create(
            _values=dict(class_guid=class_guid, user_guid=user_guid)
        )

        return "Вы успешно добавили школьника в этот учебный класс!"


async def admin_del_user_to_class(
        class_guid: UUID | str,
        user_guid: UUID | str
) -> str:
    from main.models import engine, TeacherClasses, CRUD, SessionHandler

    from main.utils.users import get_users_with_serialize
    current_user = await get_users_with_serialize(user_guid=user_guid, is_teacher=True)

    current_teacher: TeacherClasses | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=TeacherClasses
    ).read(
        _where=[TeacherClasses.class_guid == class_guid, TeacherClasses.user_guid == current_user.guid],
        _all=False
    )
    if current_teacher is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': 'К сожалению, этот преподаватель уже был удален из этого учебного класса!',
                'data': {}
            }
        )

    await CRUD(
        session=SessionHandler.create(engine=engine), model=TeacherClasses
    ).delete(
        _where=[
            TeacherClasses.class_guid == current_teacher.class_guid,
            TeacherClasses.user_guid == current_teacher.user_guid
        ]
    )

    return "Вы успешно удалили преподавателя из этого учебного класса!"


async def admin_del_schoolchildren_from_class(
        class_guid: UUID | str,
        schoolchildren_class_guid: UUID | str
) -> str:
    from main.models import engine, SchoolchildrenClasses, CRUD, SessionHandler
    from main.utils.schoolchildren_classes import get_schoolboy

    await get_schoolboy(class_guid=class_guid, schoolchildren_class_guid=schoolchildren_class_guid, with_exception=True)

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
    from main.utils.schoolchildren_classes import get_schoolboy
    from main.utils.tests import get_tests

    schoolchildren = await get_schoolboy(
        class_guid=class_guid,
        schoolchildren_class_guid=schoolchildren_class_guid,
        with_exception=True
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
