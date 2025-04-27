from main.models import engine, Users, CRUD, SessionHandler
from fastapi import HTTPException, Response, Cookie
from main.schemas.users import UserSignUp, UserLogin, UserRegular, BirthdayUser, UserUpdate
from uuid import UUID


def serialize_user(user: Users) -> UserRegular:
    return UserRegular(
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
        is_teacher=user.is_teacher
    )


async def get_user(
        user_guid: UUID | str | None = None,
        login: str | None = None,
        hash_password: str | None = None,
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
    if hash_password is not None:
        where_.append(Users.hash_password == hash_password)
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


async def get_users_with_serialize(
        user_guid: UUID | str | None = None,
        is_teacher: bool = False
) -> tuple[UserRegular] | UserRegular:
    users = await get_user(user_guid=user_guid, is_teacher=is_teacher, with_exception=True)
    if user_guid is None:
        return tuple(serialize_user(user=user) for user in users)
    return serialize_user(user=users)


async def create_new_user(user: UserSignUp) -> Users:

    if await get_user(login=user.login, with_exception=False):
        raise HTTPException(
            status_code=409,
            detail={"result": False, "message": "Пользователь с таким логином уже существует!", "data": {}}
        )

    if await get_user(phone_number=user.phone_number, with_exception=False):
        raise HTTPException(
            status_code=409,
            detail={"result": False, "message": "Пользователь с таким номером телефона уже существует!", "data": {}}
        )

    from main.utils.validation import hash_password
    new_user: Users | object = await CRUD(
        session=SessionHandler.create(engine=engine), model=Users
    ).create(_values=dict(
        login=user.login,
        password=user.password,
        hash_password=hash_password(password_=user.password),
        phone_number=user.phone_number,
        fio=user.fio,
        birthday=user.birthday,
        gender=user.gender,
        is_teacher=True if user.role == 'Преподаватель' else False
    ))
    return new_user


async def get_signup_user(user: UserSignUp, response: Response) -> dict:
    new_user = await create_new_user(user=user)
    response.set_cookie(key="user_token", value=new_user.guid, httponly=True, samesite="strict", max_age=4838400)
    return {'message': 'Вы успешно зарегистрировались!', 'data': serialize_user(user=new_user)}


async def get_login_user(user: UserLogin, response: Response) -> dict:
    from main.utils.validation import hash_password
    current_user = await get_user(login=user.login, hash_password=hash_password(user.password), with_exception=False)
    if not current_user:
        raise HTTPException(
            status_code=409,
            detail={"result": False, "message": "Пользователь с таким логином и паролем не найден!", "data": {}}
        )

    response.set_cookie(key="user_token", value=current_user.guid, httponly=True, samesite="strict", max_age=4838400)
    return {'message': 'Вы успешно авторизовались!', 'data': serialize_user(user=current_user)}


async def get_logout_user(response: Response) -> str:
    response.delete_cookie(key="user_token")
    return "Выход выполнен успешно!"


async def update_user(user_update: UserUpdate, current_user: UserRegular) -> str:

    from main.utils.validation import check_phone_number
    if check_phone_number(phone_number_=current_user.phone_number) != user_update.phone_number:
        if await get_user(phone_number=user_update.phone_number, with_exception=False):
            raise HTTPException(
                status_code=409,
                detail={'result': False, 'message': 'Ошибка, данный телефон уже занят!', 'data': {}}
            )

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Users
    ).update(
        _where=[Users.guid == current_user.guid],
        _values=user_update.model_dump()
    )

    return 'Вы успешно отредактировали свои личные данные!'


async def get_current_user(user_token=Cookie(default=None)) -> UserRegular:

    if user_token is None or user_token == 'null' or user_token == '':
        raise HTTPException(
            status_code=401,
            detail={"result": False, "message": "Пожалуйста, авторизуйтесь на сайте!", "data": {}}
        )

    current_user = await get_user(user_guid=user_token, with_exception=False)
    if current_user:
        return serialize_user(user=current_user)
    else:
        raise HTTPException(
            status_code=401,
            detail={"result": False, "message": "Ваш токен истек, авторизуйтесь на сайте еще раз!", "data": {}}
        )
