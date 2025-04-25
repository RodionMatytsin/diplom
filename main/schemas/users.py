from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from main.schemas.responses import DefaultResponse
from main.utils.validation import check_role, check_phone_number, check_fio, check_birthday, \
    check_gender, check_password
from uuid import UUID
from datetime import datetime, date


class User(BaseModel):
    phone_number: str | int
    fio: str
    birthday: date | str
    gender: str

    @field_validator('phone_number')
    def check_phone_number_(cls, phone_number_):
        phone_number_ = check_phone_number(phone_number_=str(phone_number_))
        if not phone_number_:
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Номер телефона» введено некорректно!', 'data': {}}
            )
        return phone_number_

    @field_validator('fio')
    def check_fio_(cls, fio_):
        fio_ = check_fio(fio_=fio_)
        if not fio_:
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «ФИО» введено некорректно!', 'data': {}}
            )
        return fio_

    @field_validator('birthday')
    def check_birthday_(cls, birthday_):
        birthday_ = check_birthday(birthday_=birthday_)
        if not birthday_:
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Дата рождения» введено некорректно!', 'data': {}}
            )
        return datetime.strptime(birthday_, '%Y-%m-%d').date()

    @field_validator('gender')
    def check_gender_(cls, gender_):
        gender_ = check_gender(gender_=gender_)
        if not gender_:
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Пол» введено некорректно!', 'data': {}}
            )
        return gender_


class UserSignUp(User):
    role: str
    login: str
    password: str

    @field_validator('role')
    def check_role_(cls, role_):
        role_ = check_role(role_=role_)
        if not role_:
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Роль» введено некорректно!', 'data': {}}
            )
        return role_

    @field_validator('password')
    def check_password_(cls, password_):
        password_ = check_password(password_=password_)
        if not password_:
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Пароль» введено некорректно!', 'data': {}}
            )
        return password_


class UserLogin(BaseModel):
    login: str
    password: str

    @field_validator('password')
    def check_password_(cls, password_):
        password_ = check_password(password_=password_)
        if not password_:
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Пароль» введено некорректно!', 'data': {}}
            )
        return password_


class UserUpdate(User):
    pass


class BirthdayUser(BaseModel):
    day: str
    month: str
    year: str


class UserRegular(BaseModel):
    guid: UUID | str
    login: str
    phone_number: str | int
    fio: str
    birthday: BirthdayUser
    gender: str
    datetime_create: str
    is_teacher: bool

    @field_validator('phone_number')
    def validate_tel_number(cls, phone_number_: int):
        phone = str(phone_number_)
        return f'+7 ({phone[:3]}) {phone[3:6]} {phone[6:]}'


class UserDefault(DefaultResponse):
    data: UserRegular | tuple[UserRegular] | tuple
