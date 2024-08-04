from datetime import datetime, timedelta
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import String, ForeignKey, create_engine, select, func, delete, \
    update
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, Session
)

load_dotenv()

POSTGRES_USER = getenv('POSTGRES_USER')
POSTGRES_PASSWORD = getenv('POSTGRES_PASSWORD')
POSTGRES_DB = getenv('POSTGRES_DB')
DB_HOST = getenv('DB_HOST')

DATABASE_URL = (f'postgresql+psycopg2://'
                f'{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}/{POSTGRES_DB}')

engine = create_engine(
    DATABASE_URL,
    echo=getenv('ENGINE_ECHO', '').lower() == 'true'
)


def current_time():
    """
    :return: Current time in format %Y-%m-%d %H:%M:%S
    """

    return str(datetime.now()).split('.')[0]


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

    messages = relationship(
        'Message',
        back_populates='user',
        cascade='all, delete-orphan'
    )


class Message(Base):
    __tablename__ = 'Message_ids'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))
    message_id: Mapped[int] = mapped_column()
    date_added: Mapped[str] = mapped_column(
        default=current_time
    )

    user = relationship('User', back_populates='messages')


def check_bd_chat_id(function):
    """
    Decorator to check if a user's chat ID exists in the database.
    If not found, it suggests the user to press
    /start to initialize their chat session.

    :param function: The function to be decorated.
    :return: The decorated function.
    """

    def wrapper(message, *args):
        chat_id = message.chat.id
        user_first_name = message.chat.first_name
        username = message.chat.username

        with Session(engine) as session:
            stmt = select(User).where(User.chat_id == chat_id)
            result = session.execute(stmt).scalar()

        if result:
            if (result.username != username or
                    result.user_first_name != user_first_name):
                session.execute(
                    update(User).where(User.chat_id == chat_id).values(
                        username=username,
                        user_first_name=user_first_name
                    )
                )

            return function(message, *args)
        else:
            with Session(engine) as session:
                user_record = User(
                    chat_id=chat_id,
                    username=username,
                    user_first_name=user_first_name
                )
                session.add(user_record)
                session.commit()

                record_message_id_to_db(user_record.id, message.message_id)
                return function(message, *args)

    return wrapper


def morning_routine():
    """
    Delete old message IDs from the DB. Telegram's policy doesn't allow bots
    to delete messages that are older than 48 hours.
    :return: Nothing
    """

    threshold = datetime.now() - timedelta(hours=51)

    with Session(engine) as session:
        stmt = delete(Message).where(
            Message.date_added < threshold.strftime('%Y-%m-%d %H:%M:%S'))

        session.execute(stmt)
        session.commit()


def get_user_db_id(chat_id: int):
    """
    Retrieves the user's primary key from the database using the chat id.
    :param chat_id:
    :return: User's primary key - ID
    """

    with Session(engine) as session:
        stmt = select(User).where(User.chat_id == chat_id)
        result = session.execute(stmt).scalar()

    return result.id


def get_users_count():
    """
    Counts the number of users in the database.
    :return: User's count
    """

    with Session(engine) as session:
        count = session.query(func.count(User.id)).scalar()

    return count


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
