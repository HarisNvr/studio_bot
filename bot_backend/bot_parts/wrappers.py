from time import sleep

from sqlalchemy import update, select
from sqlalchemy.orm import Session
from telebot import types
from telebot.apihelper import ApiTelegramException

from bot_funcs.user_funcs import chepuha
from bot_parts.constants import (
    ADMIN_IDS, BOT, CHANNEL_ID, TG_CHANNEL, DEL_TIME
)
from sql_orm import record_message_id_to_db, engine, User, get_user_db_id


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


def check_is_admin(function):
    """
    A decorator that checks whether the user is an admin.

    :param function: The function to be decorated.
    :return: The decorated function.
    """

    def wrapper(message, *args):
        chat_id = message.chat.id
        if chat_id in ADMIN_IDS:
            return function(message, *args)
        else:
            return chepuha(message)

    return wrapper


def sub_check(function):
    """
    Checks if a user is subscribed to a telegram channel and sends a message
    if they are not.

    This decorator function wraps around another function (e.g., a command
    handler) to check if the user who triggered the command is subscribed to
    a specific Telegram channel. If the user is not subscribed and the
    command is '/start', it sends a message prompting them to subscribe to
    the channel. It also records the message ID in the database for future
    reference.

    Parameters: function (Callable): The function to be wrapped. This should
    be a command handler or any other function that takes a `message` object
    as its argument.

    Returns: Callable: A new function that checks subscription status and
    optionally sends a subscription prompt before calling the original
    function.
    """

    def wrapper(message):
        chat_id = message.chat.id
        user_db_id = get_user_db_id(chat_id)

        markup_unsubscribed = types.InlineKeyboardMarkup()
        btn_tg_channel = types.InlineKeyboardButton(
            text='Наш канал в Telegram',
            url=TG_CHANNEL
        )
        markup_unsubscribed.row(btn_tg_channel)

        try:
            result = BOT.get_chat_member(CHANNEL_ID, chat_id)

            if result.status in ['member', 'administrator', 'creator']:
                is_subscribed = True
            else:
                is_subscribed = False
        except ApiTelegramException:
            is_subscribed = False

        with Session(engine) as session:
            session.execute(
                update(User).where(
                    User.chat_id == chat_id
                ).values(
                    is_subscribed=is_subscribed
                )
            )
            session.commit()

        if not is_subscribed and message.text == '/start':
            sent_message = BOT.send_message(
                chat_id,
                '<b>Я заметил, что вы не подписаны на наш ТГ канал, '
                'это никак не повлияет на мою работу, но мы были бы '
                'рады вас видеть в нашем крафт-сообществе</b> \U00002665',
                parse_mode='html',
                reply_markup=markup_unsubscribed
            )
            record_message_id_to_db(user_db_id, sent_message.message_id)
            sleep(DEL_TIME)

        return function(message)

    return wrapper
