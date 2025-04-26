from main.models import engine, TeacherClasses, Classes, SchoolchildrenClasses, Users, CRUD, SessionHandler
from main.schemas.teacher_classes import TeacherClassRegular, TeacherClassWithSchoolchildrenRegular
from main.schemas.users import UserRegular
from fastapi import HTTPException
from uuid import UUID


class TeacherClass:
    class_guid: UUID | str
    name_class: str


def serialize_teacher_class(teacher_class: TeacherClass) -> TeacherClassRegular:
    return TeacherClassRegular(
        class_guid=teacher_class.class_guid,
        name_class=teacher_class.name_class
    )


async def get_teacher_classes(
        user_guid: UUID | str | None = None,
        class_guid: UUID | str | None = None
) -> tuple[TeacherClassRegular] | tuple:

    where_ = [Classes.is_deleted == False]
    if user_guid is not None:
        where_.append(TeacherClasses.user_guid == user_guid)
    if class_guid is not None:
        where_.append(TeacherClasses.class_guid == class_guid)

    teacher_classes: tuple[TeacherClass] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=TeacherClasses
    ).extended_query(
        _select=[
            TeacherClasses.class_guid,
            Classes.name.label('name_class')
        ],
        _join=[
            [Classes, Classes.guid == TeacherClasses.class_guid]
        ],
        _where=where_,
        _group_by=[],
        _order_by=[],
        _all=True
    )

    if teacher_classes is None or teacher_classes == []:
        return tuple()
    return tuple(serialize_teacher_class(teacher_class=teacher_class) for teacher_class in teacher_classes)


async def required_teacher_access(current_user: UserRegular):
    if not current_user.is_teacher:
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': 'К сожалению, вы не можете получить данные, потому что вы не преподаватель!',
                'data': {}
            }
        )


async def get_teacher_class_with_schoolchildren(
        class_guid: UUID | str
) -> tuple[TeacherClassWithSchoolchildrenRegular] | tuple:

    teacher_class_with_schoolchildren: tuple[SchoolchildrenClasses] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
    ).extended_query(
        _select=[
            SchoolchildrenClasses.guid,
            SchoolchildrenClasses.user_guid,
            Users.fio.label('user_fio'),
            SchoolchildrenClasses.estimation,
            SchoolchildrenClasses.datetime_estimation_update
        ],
        _join=[
            [Users, Users.guid == SchoolchildrenClasses.user_guid],
            [Classes, Classes.guid == SchoolchildrenClasses.class_guid]
        ],
        _where=[
            SchoolchildrenClasses.is_deleted == False,
            Classes.is_deleted == False,
            Classes.guid == class_guid
        ],
        _group_by=[],
        _order_by=[SchoolchildrenClasses.datetime_create],
        _all=True
    )

    if teacher_class_with_schoolchildren is None or teacher_class_with_schoolchildren == []:
        return tuple()
    return tuple(
        TeacherClassWithSchoolchildrenRegular(
            schoolchildren_class_guid=i.guid,
            user_guid=i.user_guid,
            user_fio=i.user_fio,
            estimation=i.estimation,
            datetime_estimation_update=f"{i.datetime_estimation_update.strftime('%d.%m.%Y')} в "
                                       f"{i.datetime_estimation_update.strftime('%H:%M')}"
            if i.datetime_estimation_update else None
        ) for i in teacher_class_with_schoolchildren
    )
