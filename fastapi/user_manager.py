from datetime import datetime
from datetime import timedelta
from typing import Optional

from fastapi import Depends
from jose import JWTError, jwt

from database import User, session, Profile, SessionToken, Team
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
        if not app_id: app_id = user.id
        session.add(Profile(user=user, app_id=app_id))
        session.commit()
        return True
    else:
        return None


def get_user(username: str):
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
    user = get_user(username)
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
        session.commit()
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

    user = get_user(username)
    if user is None:
        return credentials_exception

    return user


def delete_token(token):
    token = session.query(SessionToken).filter(SessionToken.token == token).first()
    if token:
        session.delete(token)
        session.commit()
    return 'Token deleted'


def delete_user(user, password: str):
    hashed_password = session.query(User).filter(User.username == user.username).first().hashed_password
    user = session.query(User).filter(User.username == user.username).first()
    if verify_password(password, hashed_password):
        session.delete(user.get_profile())
        session.delete(user.get_token())
        session.delete(user)
        session.commit()
        return f'User {user.username} - ({user.id}) deleted'
    else:
        return '401'


"""
Профили
"""


def get_profile(app_id: str = Depends(oauth2_scheme)):
    return session.query(Profile).filter(Profile.app_id == app_id).first()


def profile_patch(user, full_name: str = None, do_search: bool = None, description: str = None):
    profile = user.get_profile()
    profile.full_name = full_name if full_name else profile.full_name
    profile.description = description if description else profile.description
    profile.do_search = bool(do_search) if do_search is not None else profile.do_search
    session.commit()
    return user.get_profile()


"""
Команды
"""


def create_team(owner, title, app_id):
    profile = owner.get_profile()
    team = profile.get_owned_team()
    if not team:
        team = Team(profile=profile, title=title, app_id=app_id, members=profile.app_id)
        session.add(team)
        session.commit()
        return profile.get_owned_team()
    else:
        return False


def delete_team(owner):
    profile = owner.get_profile()
    team = profile.get_owned_team()
    if team:
        session.delete(team)
        session.commit()
        return 'Team deleted'
    else:
        return 'No team found'


def get_team(app_id):
    team = session.query(Team).filter(Team.app_id == app_id).first()
    if team:
        return team
    else:
        return False
