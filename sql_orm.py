from datetime import datetime
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import String, ForeignKey, create_engine
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship, Session)

load_dotenv()

DB_USER = getenv('POSTGRES_USER')
DB_PASS = getenv('POSTGRES_PASSWORD')
DB_NAME = getenv('POSTGRES_DB')
DB_HOST = getenv('DB_HOST')

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

engine = create_engine(DATABASE_URL)


def current_time():
    """
    :return: Current time in format %Y-%m-%d %H:%M:%S
    """
    datetime_now_split = str(datetime.now()).split('.')
    return datetime_now_split[0]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(String(32))
    user_first_name: Mapped[str] = mapped_column(String(32))
    last_tarot_date: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        default=None
    )

    messages = relationship('Message', back_populates='user')


class Message(Base):
    __tablename__ = 'Message_ids'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))
    message_id: Mapped[int] = mapped_column()
    date_added: Mapped[str] = mapped_column(
        default=current_time
    )

    user = relationship('User', back_populates='messages')


def record_message_id_to_db(chat_id: int, message_id: int):
    """
    Record message id's to DB, for 'clean' func.
    :return: Nothing
    """
    with Session(engine) as session:
        session.add(
            Message(
                chat_id=chat_id,
                message_id=message_id,
            )
        )

        session.commit()
