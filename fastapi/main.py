from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, WebSocket, Query, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.security import OAuth2PasswordRequestForm

import user_manager as um
from config import ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme
from connection_manager import ConnectionManager

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно указать конкретные адреса, например: ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы: GET, POST, PUT, DELETE, OPTIONS и т.д.
    allow_headers=["*"],
)


@app.post('/auth/register', tags=['Авторизация'])
async def register(username: str, password: str):
    result = um.create_user(username, password)
    if result:
        return {'code': status.HTTP_201_CREATED, 'result': 'success'}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')


@app.post('/auth/login', tags=['Авторизация'])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = um.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = um.create_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post('/auth/logout', tags=['Авторизация'])
async def logout(token: str = Depends(oauth2_scheme)):
    return um.delete_token(token)


@app.delete('/auth/delete_user', tags=['Авторизация'])
async def delete_user(password: str, token: str = Depends(oauth2_scheme)):
    result = um.delete_user(token, password)
    return result


@app.get('/profiles/me', tags=['Профиль'])
async def profile_get_me(token: str = Depends(oauth2_scheme)):
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
async def profile_update(full_name: str = None, app_id: str = None, do_search: bool = None, description: str = None, roles: str = None, stack: str = None, token: str = Depends(oauth2_scheme)):
    return um.profile_patch(token, new_id=app_id, full_name=full_name, do_search=do_search, description=description, roles=roles, stack=stack)


@app.get('/profiles/{app_id}', tags=['Профиль'])
async def profile_get_user(app_id: str):
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


@app.patch('/teams/my_own/{team_id}/delete_member/', tags=['Команды'])
async def team_delete_member(team_id: str, member_id: str, token: str = Depends(oauth2_scheme)):
    return um.delete_team_member(token, team_id, member_id)


@app.get('/teams/my', tags=['Команды'])
async def team_get_my(token: str = Depends(oauth2_scheme)):
    return [team for team in um.get_membered_teams(um.get_user_by_token(token).get_profile().app_id)]


@app.get('/teams/{team_id}', tags=['Команды'])
async def team_get(team_id: str):
    return um.get_team(team_id)


@app.patch('/teams/{team_id}/patch', tags=['Команды'])
async def team_patch(team_id: str, title: str = None, description: str = None, missing_roles: str = None, token: str = Depends(oauth2_scheme)):
    return um.patch_team(token, team_id, title=title, description=description, missing_roles=missing_roles)


@app.post('/chats/create', tags=['Чаты'])
async def chat_create(addresser: str, token: str = Depends(oauth2_scheme)):
    return um.create_chat(token, addresser)


@app.get('/chats/my', tags=['Чаты'])
async def chat_get_list(token: str = Depends(oauth2_scheme)):
    return um.get_chat_list(token)


@app.get('/chats/{chat_id}', tags=['Чаты'])
async def chat_get(chat_id: str, token: str = Depends(oauth2_scheme)):
    return um.get_chat(chat_id, token)


@app.get('/chats/{chat_id}/get_last_messages', tags=['Чаты'])
async def chat_get_last_messages(chat_id: str, page: int = 1, single: bool = False, token: str = Depends(oauth2_scheme)):
    return um.get_last_messages(chat_id, page, single, token)


@app.get('/invites/my', tags=['Приглашения'])
async def get_invites(token: str = Depends(oauth2_scheme)):
    return um.get_invites(token)


@app.post('/invites/create', tags=['Приглашения'])
async def invite_create(chat_id: str, team_id: str, token: str = Depends(oauth2_scheme)):
    return await um.save_message(token, chat_id, text=team_id, is_invite=True)


@app.post('/invites/{invite_id}/status', tags=['Приглашения'])
async def invite_status(invite_id: str, status: bool, token: str = Depends(oauth2_scheme)):
    return um.invite_status(token, invite_id, status=status)


@app.delete('/invites/{invite_id}/cancel', tags=['Приглашения'])
async def invite_cancel(invite_id: str, token: str = Depends(oauth2_scheme)):
    return um.cancel_invite(token, invite_id)


manager = ConnectionManager()
@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, token: str = Query(None)):
    user = um.get_user_by_token(token)
    username = user.get_profile().app_id
    chat = um.get_chat(chat_id, token)

    if not chat or username not in chat.members.split(', '):
        await websocket.close(code=1008)
        return None

    await manager.connect(websocket, chat_id)

    try:
        await manager.broadcast({'type': 'handshake', 'user': username}, chat_id)
    except Exception as e:
        await manager.disconnect(websocket, chat_id)
        return

    try:
        while True:
            message = await websocket.receive_text()
            message = await um.save_message(token, chat_id, message)
            message = {'id': message.id, 'chat_id': message.chat_id, 'sender_id': message.sender_id, 'send_time': str(message.send_time), 'content': message.content}
            await manager.broadcast(message, chat_id)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, chat_id)
        await manager.broadcast({'type': 'goodbye', 'user': username}, chat_id)
    except Exception as e:
        await manager.disconnect(websocket, chat_id)


@app.get('/search/profiles', tags=['Поиск'])
def search_profiles(roles: str):
    return um.search_profiles(roles)


@app.get('/search/teams', tags=['Поиск'])
def search_teams(roles: str):
    return um.search_teams(roles)


@app.get('/calendar/{month}', tags=['Календарь'])
def get_month_events(month: str):
    um.get_calendar(month)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
