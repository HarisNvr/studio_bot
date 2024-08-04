from os import getenv

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from bot_funcs.admin_only import admin, proportions, send_user_count
from bot_funcs.broadcast import start_broadcast
from bot_funcs.shop_delivery import shop, catalog, ordering, payment, shipment
from bot_funcs.studio_and_directions import (
    candles_info, custom_cloth, gips_info, epoxy,
    sketching, tie_dye_info, directions, studio, offsite_workshops
)
from bot_funcs.user_funcs import (
    clean, delete_user_messages, soc_profiles, start_help, tarot_start
)
from bot_parts.constants import ADMIN_IDS, BOT
from sql_orm import (
    engine, record_message_id_to_db, User, get_user_db_id, morning_routine
)

load_dotenv()

morning_routine()

for ADMIN_ID in (getenv('ADMIN_IDS').split(',')):
    ADMIN_IDS.append(int(ADMIN_ID))


def check_bd_chat_id(func):
    """
    Decorator to check if a user's chat ID exists in the database.
    If not found, it suggests the user to press
    /start to initialize their chat session.

    :param func: The function to be decorated.
    :return: The decorated function.
    """

    def wrapper(message, *args):
        chat_id = message.chat.id

        with Session(engine) as session:
            stmt = select(User).where(User.chat_id == chat_id)
            result = session.execute(stmt).scalar()

        if result:
            return func(message, *args)
        else:
            return chepuha(message, new_user=True)

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


@BOT.message_handler(commands=['proportions', 'users', 'broadcast'])
@check_bd_chat_id
@check_is_admin
def admin_commands(message):
    if message.text == '/proportions':
        proportions(message)
    elif message.text == '/users':
        send_user_count(message)
    elif message.text == '/broadcast':
        start_broadcast(message)


@BOT.message_handler(commands=['start', 'help', 'clean', 'studio', 'mk',
                               'shop', 'soc_profiles'])
@check_bd_chat_id
def user_commands(message):
    if message.text == ('/start' or '/help'):
        start_help(message)
    elif message.text == '/clean':
        clean(message)
    elif message.text == '/studio':
        studio(message)
    elif message.text == '/mk':
        offsite_workshops(message)
    elif message.text == '/shop':
        shop(message)
    elif message.text == '/soc_profiles':
        soc_profiles(message)


@BOT.message_handler(content_types=['text', 'photo'])
@check_bd_chat_id
def message_input(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)
    flag = False

    record_message_id_to_db(user_db_id, message.message_id)

    if message.text.lower() == 'акуна':
        sent_message = BOT.send_message(
            chat_id,
            text='Матата!'
        )
        flag = True
    elif message.text.lower() == 'матата':
        sent_message = BOT.send_message(
            chat_id,
            text='Акуна!'
        )
        flag = True
    elif 'матата акуна' in message.text.lower():
        sent_message = BOT.send_message(
            chat_id,
            text='\U0001F417 \U0001F439'
        )
        flag = True
    elif 'акуна матата' in message.text.lower():
        with open('easter_eggs/Akuna.jpg', 'rb') as img_akuna:
            sent_message = BOT.send_photo(
                chat_id,
                img_akuna,
                caption=f'<b>Акуна Матата!</b>',
                parse_mode='html'
            )
        flag = True
    elif message.text == '\U0001F346':
        with open('easter_eggs/bolt.png', 'rb') as img_bolt:
            sent_message = BOT.send_photo(
                chat_id,
                img_bolt
            )
        flag = True
    elif 'hello world' in message.text.lower():
        with open('easter_eggs/Hello-World.jpeg', 'rb') as HW_img:
            sent_message = BOT.send_photo(
                chat_id,
                HW_img
            )
        flag = True

    if flag:
        record_message_id_to_db(user_db_id, sent_message.message_id)
    else:
        chepuha(message)


def chepuha(message, new_user: bool = False):
    chat_id = message.chat.id
    user_first_name = message.chat.first_name
    username = message.chat.username

    def chepuha_message(command: str):
        text = (
            f'Извините <u>{user_first_name}</u>, '
            f'я вас не понимаю. '
            f'\n'
            f'\nПопробуйте написать '
            f'{command} для возврата в '
            f'главное меню или воспользуйтесь '
            f'кнопкой "Меню" '
            f'около окна ввода сообщения'
        )

        return text

    if not new_user:
        user_db_id = get_user_db_id(chat_id)

        sent_message = BOT.send_message(
            message.chat.id,
            text=chepuha_message('/help'),
            parse_mode='html'
        )

        record_message_id_to_db(user_db_id, sent_message.message_id)
    else:
        sent_message = BOT.send_message(
            message.chat.id,
            text=chepuha_message('start'),
            parse_mode='html'
        )

        with Session(engine) as session:
            user_record = User(
                chat_id=chat_id,
                username=username,
                user_first_name=user_first_name
            )
            session.add(user_record)
            session.commit()

            record_message_id_to_db(user_record.id, message.message_id)
            record_message_id_to_db(user_record.id, sent_message.message_id)


@BOT.callback_query_handler(func=lambda callback: True)
def handle_callback(callback):
    callback_functions = {
        'admin': admin,
        'another_proportion': lambda message: proportions(
            message,
            True
        ),
        'candles': lambda message: candles_info(
            message
        ),
        'candles_offsite': lambda message: candles_info(
            message,
            offsite=True
        ),
        'catalog': lambda message: catalog(
            message
        ),
        'clean': clean,
        'custom_cloth': lambda message: custom_cloth(
            message
        ),
        'delete_message': delete_user_messages,
        'directions': directions,
        'directions_offsite': lambda message: directions(
            message,
            offsite=True
        ),
        'epoxy': lambda message: epoxy(
            message
        ),
        'gips': lambda message: gips_info(
            message
        ),
        'gips_offsite': lambda message: gips_info(
            message,
            offsite=True
        ),
        'help': start_help,
        'offsite_workshops': offsite_workshops,
        'order': ordering,
        'pay': payment,
        'shipment': shipment,
        'shop': shop,
        'sketching': lambda message: sketching(
            message
        ),
        'soc_profiles': soc_profiles,
        'studio': studio,
        'tarot': tarot_start,
        'tie_dye': lambda message: tie_dye_info(
            message
        ),
        'tie_dye_offsite': lambda message: tie_dye_info(
            message,
            offsite=True
        )
    }

    BOT.answer_callback_query(callback.id)
    callback_functions[callback.data](callback.message)


BOT.infinity_polling()
