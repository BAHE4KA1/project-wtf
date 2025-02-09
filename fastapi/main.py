from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status
import uvicorn
from fastapi.security import OAuth2PasswordRequestForm

import user_manager as um

from config import ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme

app = FastAPI()


@app.post('/auth/register', tags=['Авторизация'])
async def register(username: str, password: str):
    """
    Регистрация нового пользователя.

    Параметры:
    - username: Имя пользователя для регистрации.
    - password: Пароль для нового пользователя.

    Возвращает:
    - Код 201 и сообщение об успешной регистрации, если пользователь успешно создан.
    - Исключение HTTP 409, если пользователь с таким именем уже существует.
    """
    result = um.create_user(username, password)
    if result:
        return {'code': status.HTTP_201_CREATED, 'result': 'success'}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')


@app.post('/auth/login', tags=['Авторизация'])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Аутентификация пользователя.

    Параметры:
    - form_data: Данные формы, содержащие имя пользователя и пароль.

    Возвращает:
    - Токен доступа и тип токена, если аутентификация прошла успешно.
    - Исключение HTTP 404, если пользователь не найден.
    """
    user = um.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = um.create_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post('/auth/logout', tags=['Авторизация'])
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Выход пользователя из системы.

    Параметры:
    - token: Токен доступа пользователя, полученный при аутентификации.

    Возвращает:
    - Результат удаления токена из системы.
    """
    return um.delete_token(token)


@app.delete('/auth/delete_user', tags=['Авторизация'])
async def delete_user(password: str, token: str = Depends(oauth2_scheme)):
    result = um.delete_user(um.get_user_by_token(token), password)
    if result:
        return {'result': 'success', 'message': 'User deleted successfully`'}
    else:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect password')


@app.patch('/profiles/me/update', tags=['Профиль'])
async def profile_update(full_name, do_search, description, token: str = Depends(oauth2_scheme)):
    return um.profile_patch(um.get_user_by_token(token), full_name=full_name, do_search=do_search, description=description)


@app.get('/profiles/me', tags=['Профиль'])
async def profile_get_me(token: str = Depends(oauth2_scheme)):
    """
    Получение профиля текущего пользователя.

    Параметры:
    - token: Токен доступа пользователя, полученный при аутентификации.

    Возвращает:
    - Профиль пользователя, связанный с предоставленным токеном.
    """
    return um.get_user_by_token(token).get_profile()


@app.get('/profiles/{app_id}', tags=['Профиль'])
async def profile_get_user(app_id: str):
    """
    Получение профиля пользователя по идентификатору приложения.

    Параметры:
    - app_id: Идентификатор приложения пользователя.

    Возвращает:
    - Профиль пользователя, связанный с указанным идентификатором приложения.
    """
    return um.get_profile(app_id)


@app.post('/teams/create', tags=['Команды'])
async def team_create(title: str, app_id: str, token: str = Depends(oauth2_scheme)):
    return um.create_team(um.get_user_by_token(token), title, app_id)


@app.delete('/teams/delete', tags=['Команды'])
async def team_delete(token: str = Depends(oauth2_scheme)):
    return um.delete_team(um.get_user_by_token(token))


@app.get('/teams/my', tags=['Команды'])
async def team_get_my(token: str = Depends(oauth2_scheme)):
    return um.get_user_by_token(token).get_profile().get_owned_team()


@app.get('/teams/{team_id}', tags=['Команды'])
async def team_get(team_id: str):
    return um.get_team(team_id)


@app.post('/teams/add_member/', tags=['Команды'])
async def team_add_member(app_id: str, token: str = Depends(oauth2_scheme)):
    owner = um.get_user_by_token(token)
    team = owner.get_profile().get_owned_team()
    team.add_member(app_id)
    return owner.get_profile().get_owned_team()


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
