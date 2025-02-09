from sqlalchemy import String, create_engine, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker, relationship
from sqlalchemy.sql.sqltypes import SchemaType

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
        return session.query(Profile).filter(Profile.user_id == self.id).first()

    def get_token(self):
        return session.query(SessionToken).filter(SessionToken.user_id == self.id).first()


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

    user = relationship("User", back_populates='profile')
    team_connection = relationship("Team", back_populates='profile')

    def get_owned_team(self):
        return session.query(Team).filter(Team.owner_id == self.id).first()

    def get_user(self):
        return session.query(User).filter(User.id == self.user_id).first()

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
        return session.query(User).filter(User.id == self.user_id).first()


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    app_id: Mapped[int] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[int] = mapped_column(String(255), ForeignKey("profiles.id"))
    title: Mapped[str] = mapped_column(String())
    members: Mapped[int] = mapped_column()

    profile = relationship('Profile', back_populates='team_connection')

    def get_owner(self):
        return session.query(Profile).filter(Profile.id == self.owner_id).first()

    def add_member(self, member):
        members_list = self.members.split(', ')
        if member not in members_list:
            print(member, members_list)
            members_list.append(member)
            self.members = ', '.join(members_list)
            print(self.members)
            session.commit()
        else:
            return self

    def get_members(self):
        members_list = self.members.split(',')
        return [member.strip() for member in members_list if member.strip()]


engine = create_engine(db_url)
Base.metadata.create_all(engine)
session = sessionmaker(engine)()
