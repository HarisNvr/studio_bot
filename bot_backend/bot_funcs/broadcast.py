from datetime import datetime
from time import sleep

from sqlalchemy import select
from sqlalchemy.orm import Session
from telebot import types
from telebot.apihelper import ApiTelegramException

from bot_backend.bot_parts.constants import DEL_TIME, BOT
from bot_backend.sql_orm import (
    get_user_db_id, record_message_id_to_db, engine, User
)

BROADCAST_ADMIN_ID = None
BROADCAST_MESSAGE = None
BROADCAST_FUNC_MESSAGES_IDS = []


def start_broadcast(message):
    global BROADCAST_ADMIN_ID
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_cancel_broadcast = types.InlineKeyboardButton(
        'Отменить',
        callback_data='cancel'
    )
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

    broadcast_success = (
        f'<b>{send_count}</b> {users_get} рассылку от:'
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
