from sqlalchemy import update, select
from sqlalchemy.orm import Session

from bot_funcs.user_funcs import chepuha
from bot_parts.constants import ADMIN_IDS
from sql_orm import record_message_id_to_db, engine, User


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


def check_is_admin(func):
    """
    A decorator that checks whether the user is an admin.

    :param func: The function to be decorated.
    :return: The decorated function.
    """

    def wrapper(message, *args):
        chat_id = message.chat.id
        if chat_id in ADMIN_IDS:
            return func(message, *args)
        else:
            return chepuha(message)

    return wrapper
