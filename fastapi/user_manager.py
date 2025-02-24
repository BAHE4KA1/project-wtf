from datetime import datetime
from datetime import timedelta
from typing import Optional, List
import os
from fastapi import Depends
from jose import JWTError, jwt

from database import User, Profile, session, SessionToken, Team, Chat, Message, Invite, Event
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
            app_id = user.username
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


def search_profiles(filters: str):
    query = session.query(Profile)
    profiles = []
    filters = filters.split(', ')
    for f in filters:
        profiles.append(query.filter(Profile.do_search and Profile.roles.icontains(f)).first())
    return profiles


def get_profile(app_id: str):
    profile = session.query(Profile).filter(Profile.app_id == app_id).first()
    return profile


def profile_patch(token: str, new_id: str = None, full_name: str = None, do_search: bool = None, description: str = None, stack: str = None, roles: str = None):
    user = get_user_by_token(token)
    profile = session.query(Profile).filter(Profile.user_id == user.id).first()
    profile.stack = stack if stack else profile.stack
    profile.set_roles(roles.split(', ') if roles else profile.roles if profile.roles else [])
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
    messages = session.query(Message).filter(Message.sender_id == old_id).all()
    for m in messages:
        m.sender_id = new_id
    session.commit()
    profile = session.query(Profile).filter(Profile.app_id == new_id).first()
    return profile


"""
Команды
"""


def search_teams(filters: str):
    teams = []
    filters = filters.split(', ')
    for f in filters:
        teams.append(session.query(Team).filter(Team.missing_roles.icontains(f)).first())
    return teams


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
    chat = create_chat(token, app_id=app_id, is_group=True)
    session.add(chat)
    session.commit()
    return get_my_teams_by_profile(profile)


def patch_team(token: str, team_id: str, new_id: str = None, title: str = None, description: str = None, missing_roles: str = None):
    team = session.query(Team).filter(Team.app_id == team_id).first()
    if team in get_my_teams(token):
        if team:
            team.set_missing_roles(missing_roles.split(', ') if missing_roles else team.missing_roles if team.missing_roles else [])
            team.app_id = new_id if new_id else team.app_id
            team.title = title if title else team.title
            team.description = description if description else team.description
            session.commit()
            return get_team(team_id)
        return '404'
    return '403'


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
    if is_group:
        team = get_team(app_id)
        chat = Chat(is_group=is_group, members=team.members, team=team)
        session.add(chat)
        session.commit()
        return get_chat(chat.id, token)
    if profile.app_id != app_id:
        chat = Chat(is_group=is_group, members=profile.app_id)
        chat.add_member(app_id)
        if session.query(Chat).filter(Chat.members == chat.members).first() is not None:
            return False
        else:
            session.add(chat)
            session.commit()
            return get_chat(chat.id, token)
    return False


def get_chat(chat_id: str, token) -> Chat or False:
    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    if get_user_by_token(token).get_profile().app_id not in chat.members:
        return False
    if chat:
        return chat
    return False


async def save_message(token: str, chat_id: str, text: str, is_invite: bool = False) -> str or dict:
    profile = get_user_by_token(token).get_profile()
    chat = get_chat(chat_id, token)
    if chat.is_member(profile) and not is_invite:
        message = Message(content=text, send_time=datetime.now(), chat=chat, sender=profile, is_invite=False)
        session.add(message)
        session.commit()
        return message
    elif chat.is_member(profile) and not chat.is_group and is_invite:
        for m in chat.members.split(', '):
            if m != profile.app_id:
                message = Message(content=text, send_time=datetime.now(), chat=chat, sender=profile, is_invite=True)
                session.add(message)
                session.commit()
                invite = create_invite(m, message)
                return [message, invite]
    return 'No chat or not a member'


def get_chat_list(token) -> List[dict]:
    profile = get_user_by_token(token).get_profile()
    chats = session.query(Chat).filter(Chat.members.contains(profile.app_id))
    return [chat for chat in chats]


def get_last_messages(chat_id: str, page: int, single: bool, token: str) -> List[dict] or False:
    sender = get_user_by_token(token).get_profile().app_id
    chat = get_chat(chat_id, token)
    if sender not in chat.members:
        return False
    if not single:
        messages = session.query(Message).filter(Message.chat_id == chat_id).order_by(Message.send_time.desc()).limit(20).offset((page-1)*20)
        return [m for m in messages]
    else:
        return session.query(Message).filter(Message.chat_id == chat_id).order_by(Message.send_time.desc()).first()


"""
Приглашения
"""


def create_invite(receiver_id: str, message) -> dict or bool:
    receiver = get_profile(receiver_id)
    team = get_team(message.content)
    invite = Invite(receiver=receiver, message=message, team=team)
    session.add(invite)
    session.commit()
    invite = session.query(Invite).filter(Invite.message_id == message.id).first()
    return invite


def get_invites(token: str):
    profile = get_user_by_token(token).get_profile()
    invites = session.query(Invite).filter(Invite.receiver_id == profile.app_id)
    return [i for i in invites]


def invite_status(token: str, invite_id: str, status: bool):
    invite = session.query(Invite).filter(Invite.id == invite_id).first()
    if invite.receiver_id == get_user_by_token(token).get_profile().app_id:
        invite.status = status
        session.commit()
        if invite.status == True:
            invite.do_invite()
            return session.query(Invite).filter(Invite.id == invite_id).first()
        return session.query(Invite).filter(Invite.id == invite_id).first()
    return 'No invite found'


def cancel_invite(token: str, invite_id: str):
    invite = session.query(Invite).filter(Invite.id == invite_id).first()
    message = invite.get_message()
    sender = get_user_by_token(token).get_profile()
    if invite.get_sender() == sender and invite.status is not None:
        invite.delete()
        message.delete()
        session.commit()
        return True
    return False


"""
Календарь
"""


def get_calendar(month: str = datetime.now().month):
    events = session.query(Event).filter(Event.date_time.month == month).all()
    return [event for event in events]
