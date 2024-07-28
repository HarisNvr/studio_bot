from os import getenv

from sqlalchemy import String, ForeignKey, create_engine
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship)
from dotenv import load_dotenv

load_dotenv()

DB_USER = getenv('POSTGRES_USER')
DB_PASS = getenv('POSTGRES_PASSWORD')
DB_HOST = getenv('DB_HOST')
DB_NAME = getenv('POSTGRES_DB')

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

engine = create_engine(DATABASE_URL, echo=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(String(32))
    last_tarot_date: Mapped[str] = mapped_column(String(20))

    messages = relationship('Message', back_populates='user')


class Message(Base):
    __tablename__ = 'Message_ids'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))
    message_id: Mapped[int] = mapped_column()
    date_added: Mapped[str] = mapped_column(String(20))

    user = relationship('User', back_populates='messages')
