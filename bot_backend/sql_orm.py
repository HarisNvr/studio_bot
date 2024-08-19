import subprocess
from datetime import datetime, timedelta
from os import getenv
from time import sleep

from dotenv import load_dotenv
from sqlalchemy import (
    String, ForeignKey, create_engine, select, func, delete, Boolean,
    TIMESTAMP
)
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


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(String(32))
    user_first_name: Mapped[str] = mapped_column(String(32))
    last_tarot_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
    )
    is_subscribed: Mapped[bool] = mapped_column(
        Boolean,
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
    message_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now,
        nullable=False,
    )

    user = relationship('User', back_populates='messages')


def morning_routine():
    """
    Delete old message IDs from the DB. Telegram's policy doesn't allow bots
    to delete messages that are older than 48 hours. Wake's up a little bit
    slow, to give the database time to fully load.
    :return: Nothing
    """
    bd_access_delay = 2.5
    sleep(bd_access_delay)

    if getenv('MIGRATE', '').lower() == 'true':
        subprocess.run(
            f'alembic revision --autogenerate -m "{getenv("COMMIT_MESSAGE")}"',
            shell=True
        )
        subprocess.run('alembic upgrade head', shell=True)
    else:
        threshold = datetime.now() - timedelta(hours=48)
        stmt = delete(Message).where(
            Message.message_date < threshold
        )

        with Session(engine) as session:
            session.execute(stmt)
            session.commit()

    sleep(bd_access_delay)


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
