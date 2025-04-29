import re


def hash_password(password_: str) -> str:
    import hashlib
    return hashlib.sha512(password_.encode()).hexdigest()


def check_fio(fio_: str) -> bool | str:
    try:
        fio_ = fio_.strip()
    except:
        return False
    if re.search(
            r'^([а-яёА-ЯЁ]{2,} [а-яёА-ЯЁ]{2,} [а-яёА-ЯЁ]{2,})|([а-яёА-ЯЁ]{2,} [а-яёА-ЯЁ]{2,})$', fio_
    ) is None:
        return False
    if len(fio_.split()) > 3:
        return False
    return fio_


def check_phone_number(phone_number_: str) -> bool | int:
    try:
        tel_number = phone_number_.strip().replace(' ', '').replace('(', '').replace(')', '').replace('-', '')
    except:
        return False
    if re.search(r'^(([+][0-9]{1,3})[0-9]{10})|(8+[0-9]{10})$', tel_number) is None:
        return False
    return int(tel_number[-10:])


def check_gender(gender_: str) -> bool | str:
    if gender_ not in ['Мужской', 'Женский']:
        return False
    return gender_


def check_role(role_: str) -> bool | str:
    if role_ not in ['Школьник', 'Преподаватель']:
        return False
    return role_


def check_birthday(birthday_: str) -> bool | str:
    if re.search(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', birthday_) is None:
        return False
    return birthday_


def check_login(login_: str) -> str:
    from fastapi import HTTPException
    if not (8 <= len(login_) <= 24):
        raise HTTPException(
            status_code=400,
            detail={'result': False, 'message': 'Поле «Логин» должно содержать от 8 до 24 символов!', 'data': {}}
        )
    if re.match(r'^[a-zA-Z0-9_\-]+$', login_) is None:
        raise HTTPException(
            status_code=400,
            detail={
                'result': False,
                'message': 'Поле «Логин» может содержать только английские буквы, цифры и символы _ и -!',
                'data': {}
            }
        )
    return login_


def check_password(password_: str) -> str:
    from fastapi import HTTPException
    if not (8 <= len(password_) <= 32):
        raise HTTPException(
            status_code=400,
            detail={'result': False, 'message': 'Поле «Пароль» должно содержать от 8 до 32 символов!', 'data': {}}
        )
    if re.match(r'^[a-zA-Z0-9_.\-!]+$', password_) is None:
        raise HTTPException(
            status_code=400,
            detail={
                'result': False,
                'message': 'Поле «Пароль» может содержать только английские буквы, цифры и символы _, -, ., !',
                'data': {}
            }
        )
    return password_


def check_class(name_class_: str) -> bool | str:
    if re.match(r'^[a-zA-ZА-Яа-я0-9_\-+=\s]+$', name_class_) is None:
        return False
    return name_class_
