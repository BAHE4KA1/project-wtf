from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, WebSocket
import uvicorn
from fastapi.security import OAuth2PasswordRequestForm

import user_manager as um
from config import ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme
from connection_manager import ConnectionManager
from database import session

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
    result = um.delete_user(token, password)
    if result:
        return {'result': 'success', 'message': 'User deleted successfully`'}
    else:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect password')


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


@app.post('/profiles/me/add_icon/', tags=['Профиль'])
async def profile_add_icon(file: UploadFile, token: str = Depends(oauth2_scheme)):
    return um.save_icon(file, token)


@app.patch('/profiles/me/update_icon/', tags=['Профиль'])
async def profile_update_icon(file: UploadFile, token: str = Depends(oauth2_scheme)):
    return um.update_icon(token, file)


@app.delete('/profiles/me/delete_icon/', tags=['Профиль'])
async def profile_delete_icon(token: str = Depends(oauth2_scheme)):
    return um.delete_icon(token)


@app.patch('/profiles/me/update', tags=['Профиль'])
async def profile_update(full_name: str = None, app_id: str = None, do_search: bool = None, description: str = None, token: str = Depends(oauth2_scheme)):
    return um.profile_patch(token, new_id=app_id, full_name=full_name, do_search=do_search, description=description)


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
    return um.create_team(token, title, app_id)


@app.get('/teams/my_own', tags=['Команды'])
async def team_get_my_own(token: str = Depends(oauth2_scheme)):
    return [team for team in um.get_my_teams(token)]


@app.delete('/teams/my_own/{team_id}/delete', tags=['Команды'])
async def team_delete(team_id: str, token: str = Depends(oauth2_scheme)):
    return um.delete_team(token, team_id)


@app.post('/teams/my_own/{team_id}/add_member/', tags=['Команды'])
async def team_add_member(team_id: str, member_id: str, token: str = Depends(oauth2_scheme)):
    return um.add_team_member(token, team_id, member_id)


@app.delete('/teams/my_own/{team_id}/delete_member/', tags=['Команды'])
async def team_delete_member(team_id: str, member_id: str, token: str = Depends(oauth2_scheme)):
    return um.delete_team_member(token, team_id, member_id)


@app.get('/teams/my', tags=['Команды'])
async def team_get_my(token: str = Depends(oauth2_scheme)):
    return [team for team in um.get_membered_teams(um.get_user_by_token(token).get_profile().app_id)]


@app.get('/teams/{team_id}', tags=['Команды'])
async def team_get(team_id: str):
    return um.get_team(team_id)

# TODO: Профиль команды и patch

@app.post('/chats/create', tags=['Чаты'])
async def chat_create(addresser: str, token: str = Depends(oauth2_scheme)):
    return um.create_chat(token, addresser)


@app.get('/chats/my', tags=['Чаты'])
async def chat_get_list(token: str = Depends(oauth2_scheme)):
    return um.get_chat_list(token)


@app.get('/chats/{chat_id}', tags=['Чаты'])
async def chat_get(chat_id: str):
    return um.get_chat(chat_id)


@app.get('/chats/{chat_id}/get_messages', tags=['Чаты'])
async def chat_get_messages(chat_id: str):
    return um.get_chat_messages(chat_id)


manager = ConnectionManager()
@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    chat = um.get_chat(chat_id)

    token = websocket.headers.get("Authorization")

    if not token or not token.startswith("Bearer "):
        await websocket.close()
        return

    token = token.split("Bearer ")[1]

    username = um.get_user_by_token(token).get_profile().app_id

    if not chat or username not in chat.members.split(', '):
        # await websocket.close()
        return

    await manager.connect(chat_id, websocket)
    await manager.broadcast(chat_id, f"{username} connected")
    print('connected')

    try:
        while True:
            message = await websocket.receive_text()
            um.save_message(token, chat_id, message)
            await manager.broadcast(chat_id, f"{username}: {message}")

    except Exception:
        pass

    finally:
        # manager.disconnect(chat_id, websocket)
        # await websocket.close()
        print('disconnected')


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)

# TODO: Do chat endpoints with websockets
# TODO: Do email and phone reg and auth endpoints and funcs in um
