from main.models import engine, Users, CRUD, SessionHandler
from fastapi import HTTPException, Header
from main.schemas.users import UserSignUp, UserLogin, UserRegular
from uuid import UUID


async def get_user(
        user_guid: UUID | str | None = None,
        login: str | None = None,
        phone_number: int | None = None,
        is_teacher: bool | None = None,
        with_exception: bool = False,
        all_: bool = False
) -> tuple[Users] | Users | None:

    where_ = []
    if user_guid is not None:
        where_.append(Users.guid == user_guid)
    if login is not None:
        where_.append(Users.login == login)
    if phone_number is not None:
        where_.append(Users.phone_number == phone_number)
    if is_teacher is not None:
        where_.append(Users.is_teacher == is_teacher)

    users: tuple[Users] | Users | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Users
    ).read(
        _where=where_, _all=all_
    )

    if users is None:
        if with_exception:
            raise HTTPException(
                status_code=404,
                detail={'result': False, 'message': 'Пользователь не найден!', 'data': {}}
            )
        return None
    return users


# async def create_new_user(user: UserSignUp) -> Users:
#     if await get_user(phone_number=user.phone_number, with_exception=False):
#         raise HTTPException(
#             status_code=409,
#             detail={"result": False, "message": "Пользователь с таким номером телефона уже зарегистрирован!", "data": {}}
#         )
#
#     await CRUD(
#         session=SessionHandler.create(engine=engine), model=Users
#     ).create(
#         _values=user.model_dump()
#     )
#
#     return await get_user(phone_number=user.phone_number, with_exception=False)
#
#
# async def get_signup_user(user: UserSignUp) -> dict:
#     new_user = await create_new_user(user=user)
#     await create_user_gift(user_id=str(new_user.id))
#     return {'message': 'Вы успешно зарегистрировались!', 'data': {'token': str(new_user.id)}}
#
#
# async def get_login_user(user: UserLogin) -> dict:
#     user = await get_user(phone_number=user.phone_number, with_exception=False)
#     if not user:
#         raise HTTPException(
#             status_code=409,
#             detail={"result": False, "message": "Пользователь с таким номером телефона не найден!", "data": {}}
#         )
#
#     return {'message': 'Вы успешно авторизовались!', 'data': {'token': str(user.id)}}


async def get_current_user(user_token: str = Header(default=None)) -> UserRegular:
    if user_token is None or user_token == 'null' or user_token == '':
        raise HTTPException(
            status_code=401,
            detail={"result": False, "message": "Пожалуйста, авторизуйтесь на сайте!", "data": {}}
        )

    user = await get_user(user_guid=user_token, with_exception=False)
    if user:
        return UserRegular(
            guid=user.guid,
            login=user.login,
            phone_number=user.phone_number,
            fio=user.fio,
            birthday=user.birthday.strftime('%d.%m.%Y'),
            gender=user.gender,
            datetime_create=f"{user.datetime_create.strftime('%d.%m.%Y')} в {user.datetime_create.strftime('%H:%M')}",
            is_teacher=user.is_teacher
        )
    else:
        raise HTTPException(
            status_code=401,
            detail={"result": False, "message": "Ваш токен истек, авторизуйтесь на сайте еще раз!", "data": {}}
        )
