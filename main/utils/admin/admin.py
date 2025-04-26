from main.models import engine, Classes, SchoolchildrenClasses, TeacherClasses, CRUD, SessionHandler
from main.schemas.admin.admin import ClassRegular
from uuid import UUID


def serialize_class(class_: Classes) -> ClassRegular:
    return ClassRegular(
        guid=class_.guid,
        name=class_.name
    )


async def get_classes_for_admin(
        class_guid: UUID | str | None = None
) -> ClassRegular | tuple[ClassRegular] | tuple:

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

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Classes
    ).create(
        _values=dict(name=name_class)
    )

    return "Вы успешно создали новый учебный класс!"


async def admin_del_class(class_guid: UUID | str) -> str:

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


# async def accept_achievement(achievement_guid: UUID | str):
#     await CRUD(
#         session=SessionHandler.create(engine=engine), model=Achievements
#     ).update(
#         _where=[Achievements.guid == achievement_guid],
#         _values=dict(is_accepted=True)
#     )
#
#
# async def reject_achievement(achievement_guid: UUID | str):
#     await CRUD(
#         session=SessionHandler.create(engine=engine), model=Achievements
#     ).update(
#         _where=[Achievements.guid == achievement_guid],
#         _values=dict(is_deleted=True)
#     )
