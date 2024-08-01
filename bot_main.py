from datetime import datetime
from glob import glob
from os import getenv, path, getcwd
from random import choice
from sys import platform
from time import sleep

from dotenv import load_dotenv
from sqlalchemy import delete, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from telebot import TeleBot, types
from telebot.apihelper import ApiTelegramException

from dicts import get_lang_greet_text
from sql_orm import (
    engine, record_message_id_to_db, Message, User, get_user_db_id,
    get_users_count, morning_routine
)

load_dotenv()

morning_routine()

BOT = TeleBot(getenv('BOT'))
ORG_NAME = getenv('ORG_NAME')

DEL_TIME = 0.5
'''Time between deleting old message and sending a new one'''

BROADCAST_ADMIN_ID = None
BROADCAST_MESSAGE = None
BROADCAST_FUNC_MESSAGES_IDS = []

ADMIN_IDS = []
for ADMIN_ID in (getenv('ADMIN_IDS').split(',')):
    ADMIN_IDS.append(int(ADMIN_ID))


# .env exports data only as <str>, chat_id in pyTelegramBotAPI preferably <int>


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
    btn_soc_profiles = types.InlineKeyboardButton(text='#МыВСети \U0001F4F1',
                                                  callback_data='soc_profiles')
    btn_shop = types.InlineKeyboardButton(text='Наш магазин  \U0001F6CD',
                                          callback_data='shop')
    btn_studio = types.InlineKeyboardButton(text='О студии \U0001F393',
                                            callback_data='studio')
    btn_offsite = types.InlineKeyboardButton(text='Выездные МК  \U0001F30D',
                                             callback_data='offsite_workshops')
    btn_tarot = types.InlineKeyboardButton(text='Карты ТАРО \U00002728',
                                           callback_data='tarot')
    btn_clean = types.InlineKeyboardButton(text=f'Очистить чат \U0001F9F9',
                                           callback_data='clean')
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


@BOT.message_handler(commands=['clean'])
@check_bd_chat_id
def clean(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_da = types.InlineKeyboardButton(text='Да',
                                        callback_data='delete_message')
    btn_net = types.InlineKeyboardButton(text='Нет', callback_data='help')
    markup.row(btn_da, btn_net)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    sent_message = BOT.send_message(
        chat_id,
        f'Вы хотите полностью очистить этот чат?'
        f'\n\n*Сообщения, отправленные более 48ч. назад и рассылка '
        f'удалены не будут',
        reply_markup=markup
    )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def delete_message(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    with Session(engine) as session:
        message_ids = session.execute(
            select(
                Message.message_id
            ).where(
                Message.chat_id == user_db_id
            )
        ).scalars().all()

        BOT.delete_message(chat_id, message.id)

        sent_message = BOT.send_message(
            chat_id,
            f'<b>Идёт очистка чата</b> \U0001F9F9',
            parse_mode='html'
        )

        for msg_id in message_ids:
            try:
                BOT.delete_message(chat_id, msg_id)
                sleep(0.01)
            except ApiTelegramException:
                pass

            session.execute(
                delete(
                    Message
                ).where(
                    Message.chat_id == user_db_id,
                    Message.message_id == msg_id)
            )
            session.commit()

    BOT.delete_message(sent_message.chat.id, sent_message.message_id)


def admin(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(text='Назад', callback_data='help')
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    sent_message = BOT.send_message(
        chat_id,
        '<b>Добро пожаловать в админское меню!</b>'
        '\n'
        '\n/broadcast - Начать процедуру рассылки'
        '\n'
        '\n/users - Узнать сколько пользователей в БД'
        '\n'
        '\n/proportions - Калькулятор пропорций',
        parse_mode='html',
        reply_markup=markup
    )

    record_message_id_to_db(user_db_id, sent_message.message_id)


@BOT.message_handler(commands=['proportions'])
@check_is_admin
def proportions(message, keep_last_msg: bool = False):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    if not keep_last_msg:
        BOT.delete_message(chat_id, message.id)
        sleep(DEL_TIME)

    sent_message = BOT.send_message(
        chat_id,
        f'Введите через пробел: '
        f'\nПропорции компонентов '
        f'<b>A</b> и <b>B</b>, '
        f'и общую массу - <b>C</b>',
        parse_mode='html'
    )

    BOT.register_next_step_handler(message, calculate_proportions)

    record_message_id_to_db(user_db_id, sent_message.message_id)


def calculate_proportions(message):
    user_db_id = get_user_db_id(message.chat.id)

    record_message_id_to_db(user_db_id, message.message_id)

    markup = types.InlineKeyboardMarkup()
    btn_another_one = types.InlineKeyboardButton(
        'Другая пропорция',
        callback_data='another_proportion'
    )
    markup.add(btn_another_one)

    def is_number(item):
        try:
            float(item)
            return True
        except ValueError:
            return False

    prop_input_split = message.text.replace(',', '.').split()
    digit_check = all(is_number(item) for item in prop_input_split)

    if len(message.text.split()) == 3 and digit_check:
        a_input, b_input, c_input = map(float, prop_input_split)

        a_gr = (c_input / (a_input + b_input)) * a_input
        b_gr = (c_input / (a_input + b_input)) * b_input

        a_percent = 100 / (a_gr + b_gr) * a_gr
        b_percent = 100 / (a_gr + b_gr) * b_gr

        a_part_new = int(a_percent) if a_percent.is_integer() \
            else round(a_percent, 2)
        b_part_new = int(b_percent) if b_percent.is_integer() \
            else round(b_percent, 2)

        a_new = int(a_gr) if a_gr.is_integer() else round(a_gr, 2)
        b_new = int(b_gr) if b_gr.is_integer() else round(b_gr, 2)
        c_new = int(c_input) if c_input.is_integer() else round(c_input, 2)

        sent_message = BOT.reply_to(
            message,
            f'Для раствора массой: <b>{c_new} гр.'
            f'\nНеобходимо:</b>'
            f'\n<b>{a_new} гр.</b> Компонента <b>A</b> '
            f'({a_part_new} %)'
            f'\n<b>{b_new} гр.</b> Компонента <b>B</b> '
            f'({b_part_new} %)',
            reply_markup=markup,
            parse_mode='html'
        )
    else:
        sent_message = BOT.reply_to(
            message,
            f'Неверный формат данных.'
            f'\nПожалуйста, '
            f'введите числа по образцу:\n<b>A B C</b>',
            parse_mode='html'
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


@BOT.message_handler(commands=['users'])
@check_is_admin
def send_user_count(message):
    chat_id = message.chat.id
    count = get_users_count()

    BOT.delete_message(chat_id, message.id)

    sent_message = BOT.send_message(
        chat_id,
        f'Количество пользователей в БД: {count}'
    )

    sleep(3.5)
    BOT.delete_message(chat_id, sent_message.message_id)


@BOT.message_handler(commands=['broadcast'])
@check_is_admin
def start_broadcast(message):
    global BROADCAST_ADMIN_ID
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_cancel_broadcast = types.InlineKeyboardButton('Отменить',
                                                      callback_data='cancel')
    markup.add(btn_cancel_broadcast)

    if BROADCAST_ADMIN_ID is None:
        BROADCAST_ADMIN_ID = message.from_user.id
        BOT.delete_message(chat_id, message.id)
        sleep(DEL_TIME)

        sent_message = BOT.send_message(
            chat_id,
            'Отправьте сообщение для рассылки',
            reply_markup=markup
        )

        BROADCAST_FUNC_MESSAGES_IDS.append(sent_message.message_id)

        BOT.register_next_step_handler(message, confirm_broadcast)
    else:
        sent_message = BOT.send_message(
            chat_id,
            'Сейчас идёт рассылка другого администратора'
        )

        record_message_id_to_db(user_db_id, sent_message.message_id)


def confirm_broadcast(message):
    global BROADCAST_MESSAGE
    BROADCAST_MESSAGE = message
    BROADCAST_FUNC_MESSAGES_IDS.append(BROADCAST_MESSAGE.id)

    markup = types.InlineKeyboardMarkup()

    btn_send_broadcast = types.InlineKeyboardButton(
        'Разослать',
        callback_data='send_broadcast'
    )

    btn_cancel_broadcast = types.InlineKeyboardButton(
        'Отменить',
        callback_data='cancel'
    )

    markup.add(btn_send_broadcast, btn_cancel_broadcast)

    sent_message = BOT.send_message(
        message.chat.id,
        'Разослать сообщение?',
        reply_markup=markup
    )

    BROADCAST_FUNC_MESSAGES_IDS.append(sent_message.message_id)


@BOT.callback_query_handler(func=lambda call: call.data == 'send_broadcast')
def send_broadcast(call):
    global BROADCAST_MESSAGE
    global BROADCAST_ADMIN_ID
    global BROADCAST_FUNC_MESSAGES_IDS
    chat_id = call.message.chat.id

    BOT.answer_callback_query(call.id)

    with Session(engine) as session:
        chat_ids = session.execute(select(User.chat_id)).scalars().all()

    broadcast_type = BROADCAST_MESSAGE.content_type

    while BROADCAST_FUNC_MESSAGES_IDS:
        func_message_id = BROADCAST_FUNC_MESSAGES_IDS.pop(0)
        BOT.delete_message(chat_id, func_message_id)
        sleep(0.2)

    sleep(DEL_TIME)
    sent_message = BOT.send_message(
        chat_id,
        text='<b>РАССЫЛКА В ПРОЦЕССЕ</b>',
        parse_mode='html'
    )
    start_time = datetime.now().strftime('%d-%m-%Y %H:%M').split('.')[0]

    if broadcast_type == 'photo':
        broadcast_function = BOT.send_photo
        content_args = {'caption': BROADCAST_MESSAGE.caption}
        content_value = BROADCAST_MESSAGE.photo[-1].file_id
    else:
        broadcast_function = BOT.send_message
        content_args = {}
        content_value = BROADCAST_MESSAGE.text

    send_count = 0
    for chat_id in chat_ids:
        if chat_id != BROADCAST_ADMIN_ID:
            try:
                broadcast_function(chat_id, content_value, **content_args)
                send_count += 1
                sleep(0.1)
            except ApiTelegramException:
                pass

    BOT.delete_message(chat_id, sent_message.id)
    sleep(DEL_TIME)

    if (str(send_count)[-1] in ['2', '3', '4']
            and str(send_count) not in ['12', '13', '14']):
        users_get = 'пользователя получили'
    elif str(send_count)[-1] == '1' and str(send_count) not in ['11']:
        users_get = 'пользователь получил'
    else:
        users_get = 'пользователей получили'

    broadcast_success = (f'<b>{send_count}</b> {users_get} рассылку от:'
                         f'\n\n\U0001F4C7 {start_time.split()[0]}'
                         f'\n\n\U0000231A {start_time.split()[1]}'
                         )

    BOT.send_message(
        chat_id,
        f'{broadcast_success}'
        f'\n'
        f'\n\U00002B07 <b>Содержание</b> \U00002B07',
        parse_mode='html'
    )

    sleep(DEL_TIME)
    broadcast_function(chat_id, content_value, **content_args)

    BROADCAST_ADMIN_ID = None
    BROADCAST_MESSAGE = None


@BOT.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_broadcast(call):
    global BROADCAST_MESSAGE
    global BROADCAST_ADMIN_ID
    global BROADCAST_FUNC_MESSAGES_IDS
    chat_id = call.message.chat.id

    BOT.answer_callback_query(call.id)

    while BROADCAST_FUNC_MESSAGES_IDS:
        func_message_id = BROADCAST_FUNC_MESSAGES_IDS.pop(0)
        BOT.delete_message(call.message.chat.id, func_message_id)
        sleep(0.2)

    BROADCAST_ADMIN_ID = None
    BROADCAST_MESSAGE = None

    sleep(DEL_TIME)
    sent_message = BOT.send_message(
        chat_id,
        text='Рассылка отменена'
    )
    sleep(5)
    BOT.delete_message(chat_id, sent_message.id)


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


@BOT.message_handler(commands=['studio'])
@check_bd_chat_id
def studio(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_dirs = types.InlineKeyboardButton('Подробнее о направлениях',
                                          callback_data='directions')
    btn_back = types.InlineKeyboardButton(text='Назад', callback_data='help')
    btn_2gis = types.InlineKeyboardButton(text='Наша студия в 2GIS',
                                          url='https://go.2gis.com/8od46')
    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Записаться на МК \U000026A1',
        url='https://t.me/elenitsa17'
    )
    markup.row(btn_dirs)
    markup.row(btn_tg_dm)
    markup.row(btn_2gis)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/studio_img.PNG', 'rb') as img_studio:
        sent_message = BOT.send_photo(
            chat_id,
            img_studio,
            caption=f'<b>Наша мастерская</b> – это то место, '
                    f'где вы сможете раскрыть '
                    f'свой потенциал и '
                    f'реализовать идеи в разных направлениях: '
                    f'свечеварение, эпоскидная смола, '
                    f'рисование, '
                    f'роспись одежды и многое другое. '
                    '\n'
                    '\n\U0001F4CD<u>Наши адреса:'
                    '\n</u><b>\U00002693 г. Новороссийск, '
                    'с. Цемдолина, ул. Цемесская, д. 10'
                    '\n\U00002600 г. Анапа, с. Витязево, '
                    'ул. Курганная, д. 29</b>',
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def directions(message, offsite=False):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()

    btn_epoxy = types.InlineKeyboardButton(text='Эпоксидная смола',
                                           callback_data='epoxy')

    btn_gips = types.InlineKeyboardButton(text='Гипс',
                                          callback_data='gips'
                                          if not offsite
                                          else 'gips_offsite')

    btn_sketching = types.InlineKeyboardButton(text='Скетчинг',
                                               callback_data='sketching')

    btn_tie_dye = types.InlineKeyboardButton(text='Тай-Дай',
                                             callback_data='tie_dye'
                                             if not offsite
                                             else 'tie_dye_offsite')

    btn_custom_cloth = types.InlineKeyboardButton(text='Роспись одежды',
                                                  callback_data='custom_cloth')

    btn_candles = types.InlineKeyboardButton(text='Свечеварение',
                                             callback_data='candles'
                                             if not offsite
                                             else 'candles_offsite')

    btn_back = types.InlineKeyboardButton(text='Назад',
                                          callback_data='studio'
                                          if not offsite
                                          else 'offsite_workshops')

    if not offsite:
        markup.row(btn_epoxy, btn_gips)
        markup.row(btn_sketching, btn_tie_dye)
        markup.row(btn_custom_cloth, btn_candles)
    else:
        markup.row(btn_gips)
        markup.row(btn_tie_dye)
        markup.row(btn_candles)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    sent_message = BOT.send_message(
        chat_id,
        f'<b>Выберите <u>направление,</u> о котором хотите '
        f'узнать подробнее:</b>',
        parse_mode='html',
        reply_markup=markup
    )

    record_message_id_to_db(user_db_id, sent_message.message_id)


@BOT.message_handler(commands=['mk'])
@check_bd_chat_id
def offsite_workshops(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(text='Назад', callback_data='help')

    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Забронировать МК \U000026A1',
        url='https://t.me/elenitsa17'
    )

    btn_directions_offsite = types.InlineKeyboardButton(
        'Подробнее о направлениях',
        callback_data='directions_offsite'
    )

    markup.row(btn_directions_offsite)
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/offsite_workshops_img.PNG',
              'rb') as img_studio:
        sent_message = BOT.send_photo(
            chat_id,
            img_studio,
            caption='<b>Вы хотите удивить гостей '
                    'творческим мастер–классом?</b> '
                    '\n'
                    '\n Наша студия готова приехать к вам c '
                    'оборудованием и материалами '
                    'по любой теме '
                    'из нашего каталога: свечеварение, '
                    'рисование, '
                    'роспись одежды и другие. '
                    'Мы обеспечим все '
                    'необходимое для проведения МК в любом '
                    'месте – в помещении или '
                    'на свежем воздухе. '
                    '\n'
                    '\n <u>Все гости получат новые '
                    'знания, навыки '
                    'и подарки, сделанные своими руками!</u>',
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


@BOT.message_handler(commands=['shop'])
@check_bd_chat_id
def shop(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_catalog_main = types.InlineKeyboardButton('Каталог \U0001F50D',
                                                  callback_data='catalog')
    btn_shipment = types.InlineKeyboardButton('Доставка \U0001F4E6',
                                              callback_data='shipment')
    btn_order = types.InlineKeyboardButton('Как заказать \U00002705',
                                           callback_data='order')
    btn_pay = types.InlineKeyboardButton('Оплата \U0001F4B3',
                                         callback_data='pay')
    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Связаться с нами \U000026A1',
        url='https://t.me/elenitsa17')
    btn_back = types.InlineKeyboardButton('Назад', callback_data='help')
    markup.row(btn_order, btn_catalog_main)
    markup.row(btn_pay, btn_shipment)
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/craft_shop.png', 'rb') as shop_img:
        sent_message = BOT.send_photo(
            chat_id,
            shop_img,
            caption=f'<b>Добро пожаловать в наш '
                    f'крафтовый магазин \U00002728</b>'
                    f'\n'
                    f'\n Здесь вы найдете уникальные и '
                    f'качественные изделия ручной работы, '
                    f'созданные с любовью и нежностью. '
                    f'Мы предлагаем вам широкий ассортимент '
                    f'товаров: декор для дома, подарки, '
                    f'украшения, сухоцветы и многое другое.'
                    f'\n'
                    f'\n <b>Мы гарантируем вам:</b> '
                    f'<u>высокое качество, '
                    f'индивидуальный подход '
                    f'и быструю отправку.</u>',
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


@BOT.callback_query_handler(func=lambda call: call.data == "catalog")
def catalog(call):
    chat_id = call.message.chat.id
    user_db_id = get_user_db_id(chat_id)

    BOT.answer_callback_query(call.id)

    with open('catalog/CSA_catalog.pdf', 'rb') as catalog_pdf:
        sent_message = BOT.send_document(
            chat_id,
            catalog_pdf,
            caption='Представляем наш каталог в формате PDF!'
                    '\n\n<b>Редакция от 13.07.2023</b>',
            parse_mode='html'
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def shipment(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Связаться с нами \U000026A1',
        url='https://t.me/elenitsa17'
    )
    btn_back = types.InlineKeyboardButton('Назад', callback_data='shop')
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/shipment.jpg', 'rb') as shipment_img:
        sent_message = BOT.send_photo(
            chat_id,
            shipment_img,
            caption='<b>После изготовления вашего заказа, '
                    'на следующий рабочий день мы начинаем '
                    'процесс доставки, который '
                    'включает в себя следующее:</b>'
                    '\n'
                    '\n <u>ШАГ 1</u>: '
                    'Бережно и надёжно упакуем ваш заказ '
                    '\n'
                    '\n <u>ШАГ 2</u>: '
                    'Отвезем его в выбранную '
                    'вами транспортную '
                    'компанию (СДЕК, DPD, '
                    'Boxberry, почта России)'
                    '\n'
                    '\n <u>ШАГ 3</u>: В течение '
                    'нескольких дней '
                    'вы сможете получить ваш заказ'
                    '\n'
                    '\n Если у вас остались '
                    'какие-либо вопросы, '
                    'касательно процесса доставки - вы всегда '
                    'можете написать нам!',
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def payment(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()

    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Связаться с нами \U000026A1',
        url='https://t.me/elenitsa17'
    )

    btn_back = types.InlineKeyboardButton('Назад', callback_data='shop')
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/pay.png', 'rb') as pay_img:
        sent_message = BOT.send_photo(
            chat_id,
            pay_img,
            caption='<u>После выбора товаров '
                    'и их характеристик, '
                    'а также согласования с '
                    'мастером - вам будет '
                    'предложено оплатить заказ.</u>'
                    '\n'
                    '\n<b>Обращаем ваше внимание, '
                    'что наша студия '
                    'работает только по 100% предоплате!</b>'
                    '\n'
                    '\n Мы принимаем банковские '
                    'переводы на карту '
                    'или по СБП, если вам необходим чек '
                    'для отчётности - мы вам его предоставим. '
                    'После получения оплаты мы начинаем '
                    'изготовление вашего заказа в рамках '
                    'согласованного заранее срока',
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def ordering(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()

    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Связаться с нами \U000026A1',
        url='https://t.me/elenitsa17'
    )

    btn_back = types.InlineKeyboardButton('Назад', callback_data='shop')
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/order.jpg', 'rb') as img_order:
        sent_message = BOT.send_photo(
            chat_id,
            img_order,
            caption='<b>Заказать красивое '
                    'изделие ручной работы '
                    'очень просто! Вам потребуется:</b>'
                    '\n'
                    '\n1) Выбрать из каталога товар, '
                    'который вам понравился.'
                    '\n'
                    '\n2) Запомнить порядковый '
                    'номер этого товара.'
                    '\n'
                    '\n3) Написать нам номер/номера '
                    'товаров, которые вы хотели бы заказать. '
                    'Наш мастер подскажет, '
                    'какие цвета/ароматы '
                    'доступны для данного '
                    'типа товара, а также '
                    'ответит на интересующие вопросы.'
                    '\n'
                    '\n<u>Фотографии из каталога являются '
                    'исключительно ознакомительными. '
                    'Мы не гарантируем 100% повторения '
                    'изделия с фото, т.к. каждое изделие '
                    'изготавливается вручную "с нуля".</u>',
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


@BOT.message_handler(commands=['soc_profiles'])
@check_bd_chat_id
def soc_profiles(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()

    btn_vk = types.InlineKeyboardButton(
        text='Группа VK',
        url=getenv('VK')
    )

    btn_inst = types.InlineKeyboardButton(
        text='Instagram',
        url=getenv('INSTAGRAM')
    )

    btn_tg_channel = types.InlineKeyboardButton(
        text='Наш канал в Telegram',
        url=getenv('TG_CHANNEL')
    )

    btn_wa = types.InlineKeyboardButton(
        text='WhatsApp',
        url=getenv('WA')
    )

    btn_ya_disk = types.InlineKeyboardButton(
        text='Примеры работ на Я.Диск',
        url=getenv('YA_DISK')
    )

    btn_tg_dm = types.InlineKeyboardButton(
        text='Telegram',
        url=getenv('TG_DM')
    )

    btn_support = types.InlineKeyboardButton(
        text='Тех. поддержка БОТА',
        url=getenv('SUPPORT')
    )

    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data='help'
    )

    markup.row(btn_inst, btn_vk)
    markup.row(btn_tg_dm, btn_wa)
    markup.row(btn_tg_channel)
    markup.row(btn_ya_disk)
    markup.row(btn_support)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    sent_message = BOT.send_message(
        chat_id,
        f'<b>Какая <u>соц.сеть</u>, вас интересует:</b>',
        parse_mode='html',
        reply_markup=markup
    )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def epoxy(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(text='Назад',
                                          callback_data='directions')

    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Записаться на МК \U000026A1',
        url='https://t.me/elenitsa17'
    )

    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/epoxy_img.png', 'rb') as img_epoxy:
        sent_message = BOT.send_photo(
            chat_id,
            img_epoxy,
            caption=f'<b>Эпоксидная смола</b> - это '
                    f'универсальный '
                    f'материал, который позволяет '
                    f'создавать разнообразные изделия и '
                    f'декоративные элементы.'
                    f'\n'
                    f'\n На нашем занятии вы '
                    f'научитесь основам '
                    f'заливки. Мы покажем вам '
                    f'различные техники, '
                    f'а также расскажем о тонкостях '
                    f'при работе '
                    f'со смолой. Вы сможете создать свои '
                    f'уникальные и неповторимые '
                    f'изделия из смолы.'
                    f'\n'
                    f'\n Смола застывает в течении 24 часов. '
                    f'Своё изделие вы сможете забрать уже на '
                    f'следующий день. После отвердевания, '
                    f'смола становится безвредной и может '
                    f'контактировать с холодными продуктами.'
                    f'\n'
                    f'\n Мы обеспечим вам '
                    f'необходимую защитную '
                    f'экипировку: перчатки, респираторы и '
                    f'фартуки. Занятия проводятся в хорошо '
                    f'проветриваемом помещении.'
                    f'\n'
                    f'\n<u>Уточняйте актуальное расписание, '
                    f'перечень изделий и наличие '
                    f'мест у мастера!</u>',
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def gips_info(message, offsite=False):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    if offsite:
        btn_text = '\U000026A1 Забронировать МК \U000026A1'
        additional_info = (
            '<u>Минимальное количество человек, перечень '
            'изделий и стоимость выезда на локацию проведения '
            'уточняйте у мастера!</u>'
        )
        callback_data = 'directions_offsite'
    else:
        btn_text = '\U000026A1 Записаться на МК \U000026A1'
        additional_info = (
            '<u>Уточняйте актуальное расписание, '
            f'перечень изделий и наличие '
            f'мест у мастера!</u>'
        )
        callback_data = 'directions'

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(text='Назад',
                                          callback_data=callback_data)
    btn_tg_dm = types.InlineKeyboardButton(text=btn_text,
                                           url='https://t.me/elenitsa17')
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/gips_img.png', 'rb') as img_gips:
        caption = (
            f'<b>Гипс</b> - это универсальный '
            f'и простой в работе материал, '
            f'из которого можно создавать различные предметы декора и '
            f'подарки.'
            f'\n\n На нашем занятии вы познакомитесь с основами '
            f'литья из гипса и узнаете, как изготавливать гипсовые '
            f'изделия своими руками. '
            f'Мы научим вас правильно замешивать '
            f'гипсовый раствор, расскажем '
            f'о секретах получения крепкого, '
            f'ровного изделия с минимальным количеством пузырей.'
            f'\n\n Вы сможете создать свои неповторимые '
            f'изделия и украсить дом. Так же гипсовые изделия – это '
            f'отличный подарок, сделанный своими руками.'
            f'\n\n{additional_info}'
        )

        sent_message = BOT.send_photo(
            chat_id,
            img_gips,
            caption=caption,
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def sketching(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(text='Назад',
                                          callback_data='directions')

    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Записаться на МК \U000026A1',
        url='https://t.me/elenitsa17'
    )

    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/sketching_img.png',
              'rb') as img_sketching:
        sent_message = BOT.send_photo(
            chat_id,
            img_sketching,
            caption='<b>Скетчинг</b> - это техника быстрого '
                    'рисования набросков и эскизов, которая '
                    'помогает визуализировать идеи, эмоции и '
                    'впечатления. На нашем '
                    'занятии вы узнаете, '
                    'как рисовать скетчи от '
                    'руки с помощью разных '
                    'материалов: карандашей, '
                    'маркеров, пастели. '
                    '\n'
                    '\n  Вы научитесь выбирать '
                    'подходящие объекты '
                    'для скетчинга, определять перспективу и '
                    'светотень, создавать '
                    'композицию и цветовую '
                    'гамму. Мы покажем вам различные стили и '
                    'техники скетчинга. '
                    '\n'
                    '\n  Вы сможете создать свои уникальные '
                    'скетчи на любые темы: '
                    'природа, архитектура, '
                    'мода и многое другое.'
                    '\n'
                    '\n<u>Уточняйте актуальное расписание '
                    'и наличие мест у мастера!</u>',
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def tie_dye_info(message, offsite=False):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    if offsite:
        btn_text = '\U000026A1 Забронировать МК \U000026A1'
        additional_info = ('<u>Минимальное количество человек, перечень '
                           'изделий и стоимость выезда на локацию проведения '
                           'уточняйте у мастера!</u>')
        callback_data = 'directions_offsite'
    else:
        btn_text = '\U000026A1 Записаться на МК \U000026A1'
        additional_info = ('<u>Уточняйте актуальное расписание'
                           ' и наличие мест у мастера!</u>')
        callback_data = 'directions'

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(text='Назад',
                                          callback_data=callback_data)
    btn_tg_dm = types.InlineKeyboardButton(text=btn_text,
                                           url='https://t.me/elenitsa17')
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/tie_dye_photo.png', 'rb') as img_tie_dye:
        caption = (
            f'<b>Тай-дай</b> - это техника '
            f'окрашивания ткани при помощи '
            f'скручивания, которая позволяет '
            f'создавать яркие и '
            f'оригинальные узоры. На нашем '
            f'занятии вы узнаете, как делать '
            f'тай-дай своими руками. Вы научитесь выбирать подходящие '
            f'красители и способы завязывания '
            f'ткани для получения разных '
            f'эффектов.\n\n Мы покажем вам различные стили и техники '
            f'тай-дай: от классического спирального до современного '
            f'мраморного. Вы сможете создать '
            f'свои уникальные вещи в стиле '
            f'тай-дай: футболки, платья, джинсы, шопперы и '
            f'другое.\n\n<b>А также при помощи тай-дай можно подарить '
            f'вторую жизнь своей любимой '
            f'вещи.</b>'
            f'\n\n{additional_info}'
        )

        sent_message = BOT.send_photo(
            chat_id,
            img_tie_dye,
            caption=caption,
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def custom_cloth(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(text='Назад',
                                          callback_data='directions')
    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Записаться на МК \U000026A1',
        url='https://t.me/elenitsa17')
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/custom_cloth_img.png',
              'rb') as img_custom_cloth:
        sent_message = BOT.send_photo(
            chat_id,
            img_custom_cloth,
            caption='<b>Роспись одежды</b> - это творческий '
                    'способ преобразить свои '
                    'вещи и сделать их '
                    'уникальными. На нашем '
                    'занятии вы узнаете, '
                    'как рисовать на ткани акриловыми '
                    'красками и какие материалы, инструменты '
                    'для этого нужны. '
                    '\n'
                    '\n  Вы научитесь выбирать '
                    'подходящие рисунки '
                    'и узоры, переносить их '
                    'на одежду, а также '
                    'использовать разные техники: от простых '
                    'надписей, до полноценных картин. '
                    'Мы покажем '
                    'вам различные стили росписи: '
                    'от классических '
                    'цветочных мотивов до '
                    'современных абстрактных '
                    'рисунков. Вы сможете '
                    'разрисовать свою одежду '
                    'в соответствии со своим вкусом и стилем. '
                    '\n'
                    '\n  Мы используем специальные краски, '
                    'которые не смываются с ткани. Поэтому '
                    'расписанная вещь будет радовать '
                    'вас очень долго.'
                    '\n'
                    '\n<u>Уточняйте актуальное расписание, '
                    f'перечень изделий и наличие '
                    f'мест у мастера!</u>',
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


def candles_info(message, offsite=False):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    if offsite:
        btn_text = '\U000026A1 Забронировать МК \U000026A1'
        additional_info = ('<u>Минимальное количество человек, перечень '
                           'изделий и стоимость выезда на локацию проведения '
                           'уточняйте у мастера!</u>')
        callback_data = 'directions_offsite'
    else:
        btn_text = '\U000026A1 Записаться на МК \U000026A1'
        additional_info = ('<u>Уточняйте актуальное расписание, '
                           f'перечень изделий и наличие '
                           f'мест у мастера!</u>')
        callback_data = 'directions'

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(text='Назад',
                                          callback_data=callback_data)
    btn_tg_dm = types.InlineKeyboardButton(text=btn_text,
                                           url='https://t.me/elenitsa17')
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open('studio_and_directions/candles_photo.png', 'rb') as img_candles:
        caption = (
            f'<b>Ароматические свечи</b> - это не '
            f'только красивый и уютный '
            f'элемент декора, но и способ создать особую атмосферу в '
            f'доме.'
            f'\n\n На нашем занятии вы создадите свечу своими руками '
            f'из натуральных ингредиентов: соевого воска, '
            f'хлопкового или деревянного фитиля. '
            f'Вы сможете выбрать ароматы по своему вкусу '
            f'(более 20 различных ароматов). '
            f'Мы расскажем вам о '
            f'тонкостях процесса изготовления свечей, а также о том, '
            f'как правильно использовать и хранить их.'
            f'\n\n Вы получите не только полезные знания и навыки, '
            f'но и удовольствие от творчества и релаксации.'
            f'\n\n{additional_info}'
        )

        sent_message = BOT.send_photo(
            chat_id,
            img_candles,
            caption=caption,
            parse_mode='html',
            reply_markup=markup
        )

    record_message_id_to_db(user_db_id, sent_message.message_id)


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
        'another_proportion': lambda message: proportions(message, True),
        'candles': candles_info,
        'candles_offsite': lambda message: candles_info(message, offsite=True),
        'clean': clean,
        'custom_cloth': custom_cloth,
        'delete_message': delete_message,
        'directions': directions,
        'directions_offsite': lambda message: directions(message,
                                                         offsite=True),
        'epoxy': epoxy,
        'gips': gips_info,
        'gips_offsite': lambda message: gips_info(message, offsite=True),
        'help': start_help,
        'offsite_workshops': offsite_workshops,
        'order': ordering,
        'pay': payment,
        'shipment': shipment,
        'shop': shop,
        'sketching': sketching,
        'soc_profiles': soc_profiles,
        'studio': studio,
        'tarot': tarot_start,
        'tie_dye': tie_dye_info,
        'tie_dye_offsite': lambda message: tie_dye_info(message, offsite=True)
    }

    BOT.answer_callback_query(callback.id)
    callback_functions[callback.data](callback.message)


BOT.infinity_polling()
