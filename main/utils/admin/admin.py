from main.models import engine, Classes, CRUD, SessionHandler


async def admin_add_new_class(name_class: str) -> str:

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Classes
    ).create(
        _values=dict(name=name_class)
    )

    return "Вы успешно создали новый учебный класс!"
