from datetime import datetime, timedelta
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import String, ForeignKey, create_engine, select, func, delete
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship, Session)

load_dotenv()

DB_USER = getenv('DB_USER')
DB_PASSWORD = getenv('DB_PASSWORD')
DB_NAME = getenv('DB_NAME')
DB_HOST = getenv('DB_HOST')

DATABASE_URL = (f'postgresql+psycopg2://'
                f'{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

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
