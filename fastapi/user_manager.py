from datetime import datetime
from datetime import timedelta
from typing import Optional
import os
from fastapi import Depends
from jose import JWTError, jwt

from database import User, Profile, session, SessionToken, Team, Chat, Message
# from types import Result
from config import pwd_context, oauth2_scheme, ALGORITHM, SECRET_KEY


"""
Пользователи
"""


def create_user(username: str, password: str, app_id: str = None):
    user = session.query(User).filter(User.username == username).first()
    if not user:
        user = User(username=username, hashed_password=pwd_context.hash(password))
        session.add(user)
        session.commit()
        user = session.query(User).filter(User.username == username).first()
        if not app_id:
            app_id = user.id
        session.add(Profile(user=user, app_id=app_id))
        session.commit()
        return True
    else:
        return None


def get_user_by_username(username: str):
    user = session.query(User).filter(User.username == username).first()
    if user:
        return user
    else:
        return None


def get_user_by_token(token: str):
    user = session.query(SessionToken).filter(SessionToken.token == token).first().get_user()
    if user:
        return user
    else:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    else:
        return user


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    user = session.query(User).filter(User.username == data['sub']).first()
    token = session.query(SessionToken).filter(SessionToken.user_id == user.id).first()
    if not token:
        session.add(SessionToken(token=encoded_jwt, user=user))
    else:
        token.token = encoded_jwt
    session.commit()
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = {'result': 'error', 'code': 401}

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return credentials_exception

    except JWTError:
        return credentials_exception

    user = get_user_by_username(username)
    if user is None:
        return credentials_exception

    return user


def delete_token(token: str):
    token = session.query(SessionToken).filter(SessionToken.token == token).first()
    if token:
        session.delete(token)
        session.commit()
    return 'Token deleted'


def delete_user(token: str, password: str):
    user = get_user_by_token(token)
    hashed_password = session.query(User).filter(User.username == user.username).first().hashed_password
    user = session.query(User).filter(User.username == user.username).first()
    if verify_password(password, hashed_password):
        session.delete(user.get_profile())
        session.delete(user.get_token())
        session.delete(user)
        session.commit()
        delete_icon(token)
        return f'User {user.username} - ({user.id}) deleted'
    else:
        return '401'


"""
Профили
"""


def get_profile(app_id: str):
    profile = session.query(Profile).filter(Profile.app_id == app_id).first()
    return profile


def profile_patch(token: str, new_id: str = None, full_name: str = None, do_search: bool = None, description: str = None):
    user = get_user_by_token(token)
    profile = session.query(Profile).filter(Profile.user_id == user.id).first()
    profile.full_name = full_name if full_name else profile.full_name
    profile.description = description if description else profile.description
    profile.do_search = bool(do_search) if do_search is not None else profile.do_search
    if new_id:
        profile_update_app_id(profile, new_id)
    session.commit()
    return user.get_profile()


def profile_update_app_id(profile, new_id):
    old_id = profile.app_id
    teams_owned = get_my_teams_by_profile(profile)
    profile.set_app_id(new_id)
    for team in teams_owned:
        team.update_owner(profile)
    teams_membered = get_membered_teams(old_id)
    for team in teams_membered:
        team.update_member(old_id, new_id)
    if os.path.exists(f'user_files/{old_id}'):
        os.rename(f'user_files/{old_id}', f'user_files/{new_id}')

        avatar_file_type = ''
        a = False
        for i in profile.avatar_url:
            if a:
                avatar_file_type += i
            elif i == '.':
                a = True

        profile.set_avatar(f'user_files/{new_id}/user-icon.{avatar_file_type}')
    print(os.path.exists(f'user_files/{old_id}'), f'user_files/{old_id}')
    session.commit()
    return get_my_teams_by_profile(profile)


"""
Команды
"""


def get_membered_teams(app_id):
    teams = session.query(Team).filter(Team.members.contains(app_id))
    return [team for team in teams]


def create_team(token: str, title: str, app_id: str):
    if session.query(Team).filter(Team.app_id == app_id).first():
        return 409
    profile = get_user_by_token(token).get_profile()
    team = Team(title=title, app_id=app_id, profile=profile, members=profile.app_id)
    session.add(team)
    session.commit()
    return get_my_teams_by_profile(profile)


def delete_team(token: str, team_id: str):
    profile = get_user_by_token(token).get_profile()
    team = session.query(Team).filter(Team.app_id == team_id).first()
    if team in [t for t in get_my_teams_by_profile(profile)]:
        session.delete(team)
        session.commit()
        return f'Team {team_id} - ({team.title}) deleted'
    return '404'


def get_team(app_id):
    team = session.query(Team).filter(Team.app_id == app_id).first()
    if team:
        return team
    else:
        return False


def get_my_teams(token):
    profile = get_user_by_token(token).get_profile()
    teams = session.query(Team).filter(Team.owner_id == profile.app_id)
    return [team for team in teams]


def get_my_teams_by_profile(profile):
    teams = session.query(Team).filter(Team.owner_id == profile.app_id)
    return [team for team in teams]


def add_team_member(token: str, team_id: str, member_id: str):
    member = get_profile(member_id)
    owned_teams = get_my_teams(token)
    if member and team_id in [team.app_id for team in owned_teams]:
        team = get_team(team_id)
        team.add_member(member_id)
        session.commit()
        return team.members
    return 'No team or member found'


def delete_team_member(token: str, team_id: str, member_id: str):
    member = get_profile(member_id)
    owned_teams = get_my_teams(token)
    team = get_team(team_id)
    if member.app_id and member.app_id in team.members and team_id in [t.app_id for t in owned_teams]:
        team.remove_member(member_id)
        session.commit()
        return team.members
    return 'No team or member found'


"""
Специфические функции получения чего-то
"""


def save_icon(file, token):
    profile = get_user_by_token(token).get_profile()
    if not os.path.exists(f'user_files/{profile.app_id}'):
        os.mkdir(f'user_files/{profile.app_id}')
    with open(f'user_files/{profile.app_id}/user-icon.{file.content_type[6:]}', 'wb') as f:
        f.write(file.file.read())
        return profile.set_avatar(f.name)


def update_icon(token, file):
    profile = get_user_by_token(token).get_profile()
    old_file = profile.avatar_url
    if os.path.exists(old_file):
        os.remove(old_file)
    return save_icon(file, token)


def delete_icon(token):
    profile = get_user_by_token(token).get_profile()
    avatar_url = profile.avatar_url
    profile.delete_avatar()
    if os.path.exists(avatar_url):
        os.remove(avatar_url)
        return f'User {profile.app_id} - Icon deleted'
    return 'File deleted'


"""
Чаты
"""


def create_chat(token: str, app_id: str, is_group: bool = False):
    profile = get_user_by_token(token).get_profile()
    chat = Chat(is_group=is_group, members=profile.app_id)
    chat.add_member(app_id)
    if session.query(Chat).filter(Chat.members == chat.members).first() is not None:
        return False
    else:
        session.add(chat)
        session.commit()
        return get_chat(chat.id)


def get_chat(chat_id: str) -> Chat or False:
    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    if chat:
        return chat
    else:
        return False


def get_chat_messages(chat_id: str):
    messages = session.query(Message).filter(Message.chat_id == chat_id).order_by(Message.send_time)
    return [message for message in messages]


def save_message(token: str, chat_id: str, text: str):
    profile = get_user_by_token(token).get_profile()
    chat = get_chat(chat_id)
    if chat and chat.is_member(profile.app_id):
        message = Message(content=text, send_time=datetime.now(), chat=chat, sender=profile)
        session.add(message)
        session.commit()
        return message
    return 'No chat or not a member'


def get_chat_list(token):
    profile = get_user_by_token(token).get_profile()
    chats = session.query(Chat).filter(Chat.members.contains(profile.app_id))
    return [chat for chat in chats]


def run_chat(chat_id):
    chat = get_chat(chat_id)
    if chat:
        chat.run()
