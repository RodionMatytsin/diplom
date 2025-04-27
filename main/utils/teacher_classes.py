from main.models import engine, TeacherClasses, Classes, SchoolchildrenClasses, Users, CRUD, SessionHandler
from main.schemas.teacher_classes import TeacherClassRegular, TeacherClassWithSchoolchildrenRegular, \
    EstimationUpdate, Schoolchildren
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


async def get_schoolchildren(
        class_guid: UUID | str
) -> tuple[SchoolchildrenClasses] | object | None:

    schoolchildren: tuple[SchoolchildrenClasses] | object | None = await CRUD(
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
            [Users, Users.guid == SchoolchildrenClasses.user_guid]
        ],
        _where=[
            SchoolchildrenClasses.is_deleted == False,
            SchoolchildrenClasses.class_guid == class_guid
        ],
        _group_by=[],
        _order_by=[SchoolchildrenClasses.datetime_create],
        _all=True
    )

    return schoolchildren


async def serialize_teacher_class_with_schoolchildren(
        name_class: str, schoolchildren: tuple[SchoolchildrenClasses] | object | None
) -> TeacherClassWithSchoolchildrenRegular:
    return TeacherClassWithSchoolchildrenRegular(
        name_class=name_class,
        schoolchildren=tuple(
            Schoolchildren(
                schoolchildren_class_guid=i.guid,
                user_guid=i.user_guid,
                user_fio=i.user_fio,
                estimation=i.estimation,
                datetime_estimation_update=f"{i.datetime_estimation_update.strftime('%d.%m.%Y')} в "
                                           f"{i.datetime_estimation_update.strftime('%H:%M')}"
                if i.datetime_estimation_update else None
            ) for i in schoolchildren
        ) if schoolchildren else tuple()
    )


async def get_teacher_class_with_schoolchildren(
        class_guid: UUID | str,
        user_guid: UUID | str
) -> TeacherClassWithSchoolchildrenRegular:

    class_: Classes | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Classes
    ).extended_query(
        _select=[
            Classes.guid,
            Classes.name
        ],
        _join=[
            [TeacherClasses, TeacherClasses.class_guid == Classes.guid]
        ],
        _where=[
            Classes.is_deleted == False,
            Classes.guid == class_guid,
            TeacherClasses.user_guid == user_guid
        ],
        _group_by=[],
        _order_by=[],
        _all=False
    )

    if class_ is None:
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': 'К сожалению, вы не принадлежите к этому учебному классу, либо его просто не существует!',
                'data': {}
            }
        )

    return await serialize_teacher_class_with_schoolchildren(
        name_class=class_.name,
        schoolchildren=await get_schoolchildren(class_guid=class_.guid)
    )


async def update_estimation_to_schoolchildren(estimation_update: EstimationUpdate) -> str:
    from datetime import datetime

    schoolboy: SchoolchildrenClasses | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
    ).read(
        _where=[
            SchoolchildrenClasses.guid == estimation_update.schoolchildren_class_guid,
            SchoolchildrenClasses.is_deleted == False
        ],
        _all=False
    )

    if schoolboy is None:
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': 'К сожалению, школьник был не найден в этом классе!',
                'data': {}
            }
        )

    await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
    ).update(
        _where=[SchoolchildrenClasses.guid == schoolboy.guid],
        _values=dict(
            estimation=estimation_update.estimation,
            datetime_estimation_update=datetime.now()
        )
    )

    return "Вы успешно обновили оценку у школьника!"
