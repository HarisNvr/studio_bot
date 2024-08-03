from os import getenv
from time import sleep

from dotenv import load_dotenv
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from telebot import types
from telebot.apihelper import ApiTelegramException

from bot_backend.bot_parts.constants import BOT, DEL_TIME
from bot_backend.sql_orm import (
    get_user_db_id, record_message_id_to_db, Message, engine
)


load_dotenv()


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
