from datetime import datetime
from glob import glob
from os import getenv, path, getcwd
from random import choice
from sys import platform
from time import sleep

from dotenv import load_dotenv
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from telebot import types

from bot_backend.bot_funcs.admin_only import (
    admin, proportions, send_user_count
)
from bot_backend.bot_funcs.shop_delivery import (
    shop, catalog, ordering, payment, shipment
)
from bot_backend.bot_funcs.user_funcs import (
    clean, delete_user_messages, soc_profiles
)
from bot_funcs.broadcast import start_broadcast
from bot_parts.constants import ADMIN_IDS, BOT, DEL_TIME, ORG_NAME
from bot_parts.dicts import get_lang_greet_text
from bot_funcs.studio_and_directions import (
    candles_info, custom_cloth, gips_info, epoxy,
    sketching, tie_dye_info, directions, studio, offsite_workshops
)
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


@BOT.message_handler(commands=['start', 'help'])
def start_help(message, keep_last_msg: bool = False):
    user_first_name = message.chat.first_name
    chat_id = message.chat.id
    username = message.chat.username

    markup = types.InlineKeyboardMarkup()
    btn_soc_profiles = types.InlineKeyboardButton(
        text='#МыВСети \U0001F4F1',
        callback_data='soc_profiles'
    )
    btn_shop = types.InlineKeyboardButton(
        text='Наш магазин  \U0001F6CD',
        callback_data='shop'
    )
    btn_studio = types.InlineKeyboardButton(
        text='О студии \U0001F393',
        callback_data='studio'
    )
    btn_offsite = types.InlineKeyboardButton(
        text='Выездные МК  \U0001F30D',
        callback_data='offsite_workshops'
    )
    btn_tarot = types.InlineKeyboardButton(
        text='Карты ТАРО \U00002728',
        callback_data='tarot'
    )
    btn_clean = types.InlineKeyboardButton(
        text=f'Очистить чат \U0001F9F9',
        callback_data='clean'
    )
    markup.row(btn_studio, btn_shop)
    markup.row(btn_offsite, btn_soc_profiles)
    markup.row(btn_tarot, btn_clean)

    if chat_id in ADMIN_IDS:
        btn_admin = types.InlineKeyboardButton(
            '\U0001F60E Кнопка администратора \U0001F60E',
            callback_data='admin'
        )
        markup.row(btn_admin)

    with Session(engine) as session:
        try:
            user_record = session.execute(
                select(User).where(User.chat_id == chat_id)).scalar_one()

            if (user_record.username != username or
                    user_record.user_first_name != user_first_name):
                session.execute(
                    update(User).where(User.chat_id == chat_id).values(
                        username=username,
                        user_first_name=user_first_name
                    )
                )
        except NoResultFound:
            user_record = User(
                chat_id=chat_id,
                username=username,
                user_first_name=user_first_name
            )
            session.add(user_record)
            session.commit()

        user_db_id = user_record.id

    record_message_id_to_db(user_record.id, message.message_id)

    if message.text == '/start':
        sent_message = BOT.send_message(
            chat_id,
            f'<b>Здравствуйте, <u>{user_first_name}</u>! \U0001F642'
            f'\nМеня зовут {BOT.get_me().username}.</b>'
            f'\nЧем я могу вам помочь?',
            parse_mode='html',
            reply_markup=markup
        )

        record_message_id_to_db(user_record.id, sent_message.message_id)
    else:
        if not keep_last_msg:
            BOT.delete_message(chat_id, message.id)
        else:
            pass
        sleep(DEL_TIME)

        sent_message = BOT.send_message(
            chat_id,
            get_lang_greet_text(user_first_name),
            parse_mode='html',
            reply_markup=markup
        )

        record_message_id_to_db(user_db_id, sent_message.message_id)


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


@BOT.message_handler(commands=['clean', 'studio', 'mk', 'shop',
                               'soc_profiles'])
@check_bd_chat_id
def user_commands(message):
    if message.text == '/clean':
        clean(message)
    elif message.text == '/studio':
        studio(message)
    elif message.text == '/mk':
        offsite_workshops(message)
    elif message.text == '/shop':
        shop(message)
    elif message.text == '/soc_profiles':
        soc_profiles(message)


def tarot_start(message):
    chat_id = message.chat.id
    user_first_name = message.chat.first_name

    with Session(engine) as session:
        stmt = select(User).where(User.chat_id == chat_id)
        user = session.execute(stmt).scalar()
    last_tarot_date = user.last_tarot_date

    today = datetime.today().date().strftime('%d-%m-%Y')

    if chat_id in ADMIN_IDS:
        BOT.delete_message(chat_id, message.id)
        sleep(DEL_TIME)
        tarot_main(message)
        start_help(message, True)
    else:
        if last_tarot_date == today:
            sent_message = BOT.send_message(
                message.chat.id,
                f'<u>{user_first_name}</u>, '
                f'вы уже сегодня получили расклад, попробуйте завтра!',
                parse_mode='html'
            )

            record_message_id_to_db(user.id, sent_message.message_id)
        else:
            with Session(engine) as session:
                session.execute(
                    update(User).where(
                        User.chat_id == chat_id
                    ).values(
                        last_tarot_date=today
                    )
                )
                session.commit()

            BOT.delete_message(chat_id, message.id)
            sleep(DEL_TIME)

            tarot_main(message)

            start_help(message, True)


def tarot_main(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)
    tarot_delay = 1.5

    if platform == 'win32':
        tarot_path = 'Tarot'
        char = '\\'
    else:
        tarot_path = path.join(getcwd(), 'Tarot')
        char = '/'

    sent_message = BOT.send_message(
        message.chat.id,
        '<b>Расклад Таро - это всего лишь инструмент для '
        'ознакомления и развлечения. '
        'Расклад карт Таро не является истиной и не должен '
        'использоваться для принятия важных решений.</b>'
        '\n'
        f'\n<u>{ORG_NAME}</u> и его сотрудники не несут '
        'ответственности за любые действия и их последствия, '
        'которые повлекло использование данного расклада карт Таро.',
        parse_mode='html'
    )
    sleep(tarot_delay)

    record_message_id_to_db(user_db_id, sent_message.message_id)

    cards = glob(f'{tarot_path}/*.jpg')
    user_random_cards = []

    while len(user_random_cards) < 3:
        card = choice(cards)
        card_num = int(card.split(char)[-1].split('.')[0])

        if (card_num not in
                [int(c.split(char)[-1].split('.')[0]) for c in
                 user_random_cards]):

            if (card_num % 2 == 1 and card_num + 1 not in
                    [int(c.split(char)[-1].split('.')[0]) for c in
                     user_random_cards]):
                user_random_cards.append(card)

            elif (card_num % 2 == 0 and card_num - 1 not in
                  [int(c.split(char)[-1].split('.')[0]) for c in
                   user_random_cards]):
                user_random_cards.append(card)

    captions = ['Прошлое', 'Настоящее', 'Будущее']

    for card, caption in zip(user_random_cards, captions):
        with open(card, 'rb') as photo:
            with open(f'{card[:-4]}.txt', encoding='utf-8') as text:
                description = text.read()

            tarot_message = BOT.send_photo(
                message.chat.id, photo,
                caption=f'<b>{caption}</b>: {description}',
                parse_mode='html'
            )

            record_message_id_to_db(user_db_id, tarot_message.message_id)

            sleep(tarot_delay)


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
