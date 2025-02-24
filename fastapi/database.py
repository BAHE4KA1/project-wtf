from sqlalchemy import String, create_engine, ForeignKey, Boolean, DateTime, func, Integer
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker, relationship

from config import DATABASE_URL as db_url


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    token = relationship("SessionToken", back_populates="user")
    profile = relationship("Profile", back_populates="user")

    def get_profile(self):
        profile = session.query(Profile).filter(Profile.user_id == self.id).first()
        return profile

    def get_token(self):
        token = session.query(SessionToken).filter(SessionToken.user_id == self.id).first()
        return token if token else 'Not authorized'


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    app_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("users.id"))

    full_name: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    description: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    do_search: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=False)
    stack: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    roles: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    achievements: Mapped[str] = mapped_column(String(), default='0, 0, 0')

    avatar_url: Mapped[str] = mapped_column(String(), nullable=True, default=None)

    messages = relationship('Message', back_populates='sender')
    user = relationship("User", back_populates='profile')
    team_connection = relationship("Team", back_populates='profile')
    invite = relationship("Invite", back_populates='receiver')

    def set_roles(self, roles: list[str]):
        self.roles = ', '.join(roles)
        session.commit()
        return self.roles.split(', ')

    def get_roles(self):
        return self.roles.split(', ')

    def get_achievements(self):
        return self.achievements.split(', ')

    def set_achievements(self, fst: int = None, snd: int = None, trd: int = None):
        a = self.achievements.split(', ')
        self.achievements = f'{fst if fst else a[0]}, {snd if snd else a[1]}, {trd if trd else a[2]}'
        session.commit()
        return self.achievements.split(', ')

    def set_avatar(self, filename: str):
        self.avatar_url = filename
        session.commit()
        return {'avatar': filename}

    def delete_avatar(self):
        self.avatar_url = None
        session.commit()
        return {'avatar': None}

    def get_user(self):
        user = session.query(User).filter(User.id == self.user_id).first()
        return user

    def set_app_id(self, new_id):
        if not session.query(Profile).filter(Profile.app_id == new_id).first():
            self.app_id = new_id
            session.commit()
            return True
        else:
            return False


class SessionToken(Base):
    __tablename__ = "session_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String(1023))

    user: Mapped[User] = relationship("User", back_populates="token")

    def get_user(self):
        user = session.query(User).filter(User.id == self.user_id).first()
        return user


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    app_id: Mapped[str] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[str] = mapped_column(String(255), ForeignKey("profiles.app_id"), nullable=True)

    title: Mapped[str] = mapped_column(String())
    members: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    missing_roles: Mapped[str] = mapped_column(String(), nullable=True, default=None)

    chat = relationship('Chat', back_populates='team')
    profile = relationship('Profile', back_populates='team_connection')
    invite = relationship("Invite", back_populates='team')

    def get_chat(self):
        chat = session.query(Chat).filter(Chat.team_id == self.app_id).first()
        return chat

    def set_missing_roles(self, roles: list[str] = None):
        if roles:
            self.missing_roles = ', '.join(roles)
            session.commit()
        return self.missing_roles.split(', ')

    def get_missing_roles(self):
        return self.missing_roles.split(', ')

    def get_owner(self):
        owner = session.query(Profile).filter(Profile.id == self.owner_id).first()
        return owner

    def update_owner(self, new):
        self.profile = new
        session.commit()
        return self.owner_id

    def add_member(self, member: str):
        members_list = self.members.split(', ')
        if member not in members_list:
            members_list.append(member)
            self.members = ', '.join(members_list)
            chat = self.get_chat()
            chat.members = self.members
            session.commit()
        return self

    def update_member(self, member: str, new: str):
        members_list = self.members.split(', ')
        if member in members_list:
            members_list[members_list.index(member)] = new
            self.members = ', '.join(members_list)
            session.commit()
            return 200
        else:
            return 404

    def remove_member(self, member):
        members_list = self.members.split(', ')
        if member != self.owner_id:
            if member in members_list:
                members_list.remove(member)
                self.members = ', '.join(members_list)
                session.commit()
                return 205
            else:
                return 404
        return 405

    def get_members(self) -> list:
        members_list = self.members.split(',')
        return [member.strip() for member in members_list if member.strip()]


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True)
    is_group: Mapped[bool] = mapped_column(Boolean())
    team_id: Mapped[str] = mapped_column(String(), ForeignKey('teams.app_id'), nullable=True)
    members: Mapped[str] = mapped_column(String(1023))

    team = relationship('Team', back_populates='chat')
    messages = relationship('Message', back_populates='chat')

    def get_team(self):
        team = session.query(Team).filter(Team.id == self.team_id).first()
        return team

    async def add_message(self, sender, content):
        new_message = Message(sender=sender, content=content, chat_id=self.id)
        session.add(new_message)
        session.commit()
        return {'message': content}

    def is_member(self, profile):
        members_list = self.members.split(', ')
        return profile.app_id in members_list

    def add_member(self, member):
        if not self.is_group:
            members_list = self.members.split(', ')
            if member not in members_list and len(members_list) < 2:
                members_list.append(member)
                self.members = ', '.join(members_list)
                session.commit()
                return True
            else:
                return False
        else:
            members_list = self.members.split(', ')
            if member not in members_list:
                members_list.append(member)
                self.members = ', '.join(members_list)
                session.commit()
                return True
            else:
                return False

    def remove_member(self, member):
        if self.is_group:
            members_list = self.members.split(', ')
            if member in members_list:
                members_list.remove(member)
                self.members = ', '.join(members_list)
                session.commit()
                return True
            else:
                return False
        else:
            session.delete(self)
            session.commit()
            return True


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(String(255), ForeignKey("chats.id"))
    sender_id: Mapped[str] = mapped_column(String(255), ForeignKey("profiles.app_id"))
    send_time: Mapped[str] = mapped_column(DateTime, default=func.now())
    content: Mapped[str] = mapped_column(String(1023))
    is_invite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    chat = relationship('Chat', back_populates='messages')
    sender = relationship('Profile', back_populates='messages')
    invite = relationship('Invite', back_populates='message')

    def get_sender(self):
        sender = session.query(Profile).filter(Profile.id == self.sender_id).first()
        return sender


class Invite(Base):
    __tablename__ = 'invites'
    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[str] = mapped_column(String(255), ForeignKey("messages.id"))
    receiver_id: Mapped[str] = mapped_column(String(255), ForeignKey("profiles.app_id"))
    team_id: Mapped[str] = mapped_column(String(255), ForeignKey("teams.app_id"))

    status: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)

    receiver = relationship('Profile', back_populates='invite')
    message = relationship('Message', back_populates='invite')
    team = relationship('Team', back_populates='invite')

    def get_status(self):
        if self.status is not None:
            if self.status:
                return True
            else:
                return False
        return None

    def do_invite(self):
        if self.status == True:
            team_id = self.team_id
            team = session.query(Team).filter(Team.app_id == team_id).first()
            if team:
                team.add_member(member=self.receiver_id)
            return team
        return False

    def get_sender(self):
        return self.message.sender_id

    def get_receiver(self):
        receiver = session.query(Profile).filter(Profile.app_id == self.receiver_id).first()
        return receiver

    def get_message(self):
        message = session.query(Message).filter(Message.id == self.message_id).first()
        return message


class Event(Base):
    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(primary_key=True)
    date_time: Mapped[str] = mapped_column(DateTime)
    holding_time: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1023), nullable=True, default=None)
    link: Mapped[str] = mapped_column(String(255), nullable=True, default=None)


engine = create_engine(db_url, echo=False)
Base.metadata.create_all(engine)
session = sessionmaker(engine)()
