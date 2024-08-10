from datetime import datetime
from os import getenv
from pathlib import Path
from random import choice
from time import sleep

from dotenv import load_dotenv
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from telebot import types
from telebot.apihelper import ApiTelegramException

from bot_parts.constants import BOT, DEL_TIME, ORG_NAME, ADMIN_IDS, CHANNEL_ID
from bot_parts.dicts import get_lang_greet_text
from sql_orm import (
    get_user_db_id, record_message_id_to_db, Message, engine, User
)

load_dotenv()


def sub_check(chat_id):
    try:
        result = BOT.get_chat_member(CHANNEL_ID, chat_id)

        if result.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except ApiTelegramException:
        return False


def start_help(message, keep_last_msg: bool = False):
    user_first_name = message.chat.first_name
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    record_message_id_to_db(user_db_id, message.message_id)

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

    if message.text == '/start':
        sent_message = BOT.send_message(
            chat_id,
            f'<b>Здравствуйте, <u>{user_first_name}</u>! \U0001F642'
            f'\nМеня зовут {BOT.get_me().username}.</b>'
            f'\nЧем я могу вам помочь?',
            parse_mode='html',
            reply_markup=markup
        )
        record_message_id_to_db(user_db_id, sent_message.message_id)

        if not sub_check(chat_id):
            markup_unsubscribed = types.InlineKeyboardMarkup()
            btn_tg_channel = types.InlineKeyboardButton(
                text='Наш канал в Telegram',
                url=getenv('TG_CHANNEL')
            )
            markup_unsubscribed.row(btn_tg_channel)

            sleep(DEL_TIME)

            sent_message = BOT.send_message(
                chat_id,
                '<b>Я также заметил, что вы не подписаны на наш ТГ канал, '
                'это никак не повлияет на мою работу, но мы были бы '
                'рады вас видеть</b> \U00002665',
                parse_mode='html',
                reply_markup=markup_unsubscribed
            )
            record_message_id_to_db(user_db_id, sent_message.message_id)
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


def clean(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_da = types.InlineKeyboardButton(
        text='Да',
        callback_data='delete_message'
    )
    btn_net = types.InlineKeyboardButton(
        text='Нет',
        callback_data='help'
    )
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


def delete_user_messages(message):
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


def tarot_start(message):
    chat_id = message.chat.id
    user_first_name = message.chat.first_name

    with Session(engine) as session:
        stmt = select(User).where(User.chat_id == chat_id)
        user = session.execute(stmt).scalar()
    last_tarot_date = user.last_tarot_date

    today = datetime.today().date()

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

    tarot_path = Path(__file__).parent / '..' / 'Tarot'

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

    cards = list(tarot_path.glob('*.jpg'))
    user_random_cards = []

    while len(user_random_cards) < 3:
        card = choice(cards)
        card_num = int(card.stem)

        if card_num not in [int(c.stem) for c in user_random_cards]:
            if (card_num % 2 == 1 and card_num + 1 not in
                    [int(c.stem) for c in user_random_cards]):
                user_random_cards.append(card)
            elif (card_num % 2 == 0 and card_num - 1 not in
                  [int(c.stem) for c in user_random_cards]):
                user_random_cards.append(card)

    captions = ['Прошлое', 'Настоящее', 'Будущее']

    for card, caption in zip(user_random_cards, captions):
        with card.open('rb') as photo:
            text_file = card.with_suffix('.txt')
            with text_file.open(encoding='utf-8') as text:
                description = text.read()

            tarot_message = BOT.send_photo(
                message.chat.id, photo,
                caption=f'<b>{caption}</b>: {description}',
                parse_mode='html'
            )

            record_message_id_to_db(user_db_id, tarot_message.message_id)

            sleep(tarot_delay)


def chepuha(message):
    chat_id = message.chat.id
    user_first_name = message.chat.first_name

    user_db_id = get_user_db_id(chat_id)

    sent_message = BOT.send_message(
        message.chat.id,
        text=(
            f'Извините <u>{user_first_name}</u>, '
            'я вас не понимаю. '
            '\n'
            '\nПопробуйте написать '
            '/help для возврата в '
            'главное меню или воспользуйтесь '
            'кнопкой "Меню" '
            'около окна ввода сообщения'
        ),
        parse_mode='html'
    )

    record_message_id_to_db(user_db_id, sent_message.message_id)
