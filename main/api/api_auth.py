from main import main
from fastapi import Depends
from main.schemas.responses import DefaultResponse
from main.schemas.users import UserSignUp, UserDefault
from main.utils.users import get_current_user


# @main.post('/api/signup', status_code=200, tags=["Auth"], response_model=DefaultResponse)
# async def api_signup_user(user: UserSignUp):
#     signup_user = await get_signup_user(user=user)
#     return DefaultResponse(message=signup_user['message'], data=signup_user['data'])
#
#
# @main.post('/api/login', status_code=200, tags=["Auth"], response_model=DefaultResponse)
# async def api_login_user(login_user=Depends(get_login_user)):
#     return DefaultResponse(message=login_user['message'], data=login_user['data'])


@main.get('/api/users/me', status_code=200, tags=["Auth"], response_model=UserDefault)
async def api_get_current_user(user=Depends(get_current_user)):
    return UserDefault(data=user)
