from main import main
from fastapi import Depends
from main.schemas.responses import DefaultResponse
from main.schemas.users import UserDefault, UserUpdate
from main.utils.users import get_signup_user, get_login_user, get_logout_user, get_current_user, update_user


@main.post('/api/signup', status_code=200, tags=["Auth"], response_model=DefaultResponse)
async def api_signup_user(signup_user=Depends(get_signup_user)):
    """
        Этот метод предназначен для школьника или преподавателя, с помощью которого можно зарегистрироваться в системе.
    """
    return DefaultResponse(message=signup_user['message'], data=signup_user['data'])


@main.post('/api/login', status_code=200, tags=["Auth"], response_model=DefaultResponse)
async def api_login_user(login_user=Depends(get_login_user)):
    """
        Этот метод предназначен для школьника или преподавателя, с помощью которого можно войти в систему.
    """
    return DefaultResponse(message=login_user['message'], data=login_user['data'])


@main.get('/api/logout', status_code=200, tags=["Auth"], response_model=DefaultResponse)
async def api_logout_user(response=Depends(get_logout_user)):
    """
        Этот метод предназначен для школьника или преподавателя, с помощью которого можно выйти из системы.
    """
    return DefaultResponse(message=response)


@main.get('/api/users/me', status_code=200, tags=["Auth"], response_model=UserDefault)
async def api_get_current_user(current_user=Depends(get_current_user)):
    """
        Этот метод предназначен для школьника или преподавателя, с помощью которого можно получить личные данные.
    """
    return UserDefault(data=current_user)


@main.patch('/api/users', status_code=200, tags=['Auth'], response_model=DefaultResponse)
async def api_update_user(user_update: UserUpdate, current_user=Depends(get_current_user)):
    """
        Этот метод предназначен для школьника или преподавателя, с помощью которого
        можно отредактировать свои личные данные.
    """
    return DefaultResponse(message=await update_user(user_update=user_update, current_user=current_user))

