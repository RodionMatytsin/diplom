from main.models import SchoolchildrenClasses
from main.schemas.schoolchildren_classes import SchoolchildrenClassRegular
from main.schemas.users import UserRegular
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


async def get_schoolchildren_classes(
        user_guid: UUID | str | None = None,
        class_guid: UUID | str | None = None
) -> tuple[SchoolchildrenClassRegular] | tuple:
    from main.models import engine, Classes, CRUD, SessionHandler

    where_ = [
        Classes.is_deleted == False,
        SchoolchildrenClasses.is_deleted == False,
    ]
    if user_guid is not None:
        where_.append(SchoolchildrenClasses.user_guid == user_guid)
    if class_guid is not None:
        where_.append(SchoolchildrenClasses.class_guid == class_guid)

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
        _where=where_,
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


async def get_schoolboy(
        class_guid: UUID | str,
        schoolchildren_class_guid: UUID | str | None = None,
        user_guid: UUID | str | None = None,
        with_exception: bool = False,
) -> SchoolchildrenClasses:
    from main.models import engine, CRUD, SessionHandler

    where_ = [
        SchoolchildrenClasses.is_deleted == False,
        SchoolchildrenClasses.class_guid == class_guid
    ]
    if schoolchildren_class_guid is not None:
        where_.append(SchoolchildrenClasses.guid == schoolchildren_class_guid)
    if user_guid is not None:
        where_.append(SchoolchildrenClasses.user_guid == user_guid)

    schoolchildren: SchoolchildrenClasses | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=SchoolchildrenClasses
    ).read(
        _where=where_, _all=False
    )

    if schoolchildren is None and with_exception:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail={'result': False, 'message': 'К сожалению, в этом классе нет такой записи об ученике!', 'data': {}}
        )

    return schoolchildren


async def required_schoolchildren_access(current_user: UserRegular):
    if current_user.is_teacher:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail={
                'result': False,
                'message': 'К сожалению, вы не можете получить данные, потому что вы не школьник!',
                'data': {}
            }
        )
