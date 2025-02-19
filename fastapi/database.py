from typing import List
from sqlalchemy import String, create_engine, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker, relationship
from fastapi import WebSocket

from config import DATABASE_URL as db_url


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    active: Mapped[bool] = mapped_column(default=True)

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

    avatar_url: Mapped[str] = mapped_column(String(), nullable=True, default=None)

    stack: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    links: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    teams: Mapped[str] = mapped_column(String(), nullable=True, default=None)

    messages = relationship('Message', back_populates='sender')
    user = relationship("User", back_populates='profile')
    team_connection = relationship("Team", back_populates='profile')

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

    def get_links(self) -> list:
        links_list = self.links.split(',')
        return [link.strip() for link in links_list if link.strip()]

    def add_link(self, link: str) -> str:
        if not self.links:
            self.links = link
            session.commit()
            return 'Successfully set link'
        else:
            links = f'{self.links}, {link}'
            self.links = links
            session.commit()
            return 'Successfully added link'

    def remove_link(self, link: str) -> str:
        if self.links:
            links_list = self.links.split(',')
            new_links = [link.strip() for link in links_list if link.strip() != link]
            links = ', '.join(new_links)
            self.links = links
            session.commit()
            return f'Successfully removed link {link}'
        else:
            return 'No links to remove'


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
    app_id: Mapped[int] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[int] = mapped_column(String(255), ForeignKey("profiles.app_id"), nullable=True)
    title: Mapped[str] = mapped_column(String())
    members: Mapped[str] = mapped_column()

    profile = relationship('Profile', back_populates='team_connection')

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
    members: Mapped[str] = mapped_column(String(1023))

    messages = relationship('Message', back_populates='chat')

    async def add_message(self, sender, content):
        new_message = Message(sender=sender, content=content, chat_id=self.id)
        session.add(new_message)
        session.commit()
        return {'message': content}

    def is_member(self, profile):
        members_list = self.members.split(', ')
        return profile.id in members_list

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
    sender_id: Mapped[str] = mapped_column(String(255), ForeignKey("profiles.id"))
    send_time: Mapped[str] = mapped_column(DateTime, default=func.now())
    content: Mapped[str] = mapped_column(String(1023))

    chat = relationship('Chat', back_populates='messages')
    sender = relationship('Profile', back_populates='messages')


engine = create_engine(db_url, echo=False)
Base.metadata.create_all(engine)
session = sessionmaker(engine)()


# TODO: Finally do chat base
