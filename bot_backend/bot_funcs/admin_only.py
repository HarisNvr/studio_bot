from time import sleep

from telebot import types

from bot_parts.constants import BOT, DEL_TIME
from sql_orm import (
    get_user_db_id, record_message_id_to_db, get_users_count
)


def admin(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data='help'
    )
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
