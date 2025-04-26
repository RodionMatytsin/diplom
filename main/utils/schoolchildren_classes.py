from main.models import engine, SchoolchildrenClasses, Classes, CRUD, SessionHandler
from main.schemas.schoolchildren_classes import SchoolchildrenClassRegular
from uuid import UUID


class SchoolchildrenClass:
    class_guid: UUID | str
    name_class: str
    estimation: float | None


def serialize_schoolchildren_class(schoolchildren_class: SchoolchildrenClass) -> SchoolchildrenClassRegular:
    return SchoolchildrenClassRegular(
        class_guid=schoolchildren_class.class_guid,
        name_class=schoolchildren_class.name_class,
        estimation=schoolchildren_class.estimation
    )


async def get_schoolchildren_classes(user_guid: UUID | str) -> tuple[SchoolchildrenClassRegular] | tuple:

    schoolchildren_classes: tuple[SchoolchildrenClass] | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
    ).extended_query(
        _select=[
            SchoolchildrenClasses.class_guid,
            Classes.name.label('name_class'),
            SchoolchildrenClasses.estimation
        ],
        _join=[
            [Classes, Classes.guid == SchoolchildrenClasses.class_guid]
        ],
        _where=[
            Classes.is_deleted == False,
            SchoolchildrenClasses.is_deleted == False,
            SchoolchildrenClasses.user_guid == user_guid
        ],
        _group_by=[],
        _order_by=[],
        _all=True
    )

    if schoolchildren_classes is None or schoolchildren_classes == []:
        return tuple()
    return tuple(
        serialize_schoolchildren_class(
            schoolchildren_class=schoolchildren_class
        ) for schoolchildren_class in schoolchildren_classes
    )
