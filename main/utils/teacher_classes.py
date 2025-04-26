from main.models import engine, TeacherClasses, Classes, CRUD, SessionHandler
from main.schemas.teacher_classes import TeacherClassRegular
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
