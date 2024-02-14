import random
import telebot
from telebot import types
import time
import glob
from datetime import datetime
import sqlite3


bot = telebot.TeleBot('6301286378:AAH6rwbVlOIeEtZkKQKqA2RykhD2E-oXq8g')  # @CraftStudioBotJr

del_time = 0.5  # Задержка между сообщениями бота

broadcast_admin_id = None  # Админ, который сейчас бродкастит
broadcast_message = None  # Тело рассылаемого сообщения
broadcast_func_messages_ids = [] #Словарь системных сообщений группы функций broadcast

@bot.message_handler(commands=['broadcast'])
def start_broadcast(message):
    global broadcast_admin_id

    UsersBD = sqlite3.connect('UsersDB.sql')
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_cancel_broadcast = types.InlineKeyboardButton('Отменить',
                                                      callback_data='cancel')
    markup.add(btn_cancel_broadcast)

    if message.from_user.id in [154395483, 1019826386] and broadcast_admin_id is None:
        broadcast_admin_id = message.from_user.id
        bot.delete_message(message.chat.id, message.id)
        time.sleep(del_time)
        broadcast_func_messages_ids.append((bot.send_message(message.chat.id, "Отправьте сообщение для рассылки", reply_markup=markup)).message_id)
        bot.register_next_step_handler(message, confirm_broadcast)
    elif message.from_user.id in [154395483, 1019826386] and broadcast_admin_id is not None:
        new_message_id = str(bot.send_message(message.chat.id, "Сейчас идёт рассылка другого администратора").message_id)
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, new_message_id))
    else:
        chepuha(message)

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def confirm_broadcast(message):
    global broadcast_message

    if broadcast_admin_id is not None:
        UsersBD = sqlite3.connect('UsersDB.sql')
        cursor = UsersBD.cursor()

        broadcast_message = message
        broadcast_func_messages_ids.append(broadcast_message.id)

        markup = types.InlineKeyboardMarkup()
        btn_send_broadcast = types.InlineKeyboardButton('Разослать',
                                                        callback_data='send_broadcast')
        btn_cancel_broadcast = types.InlineKeyboardButton('Отменить',
                                                          callback_data='cancel')
        markup.add(btn_send_broadcast, btn_cancel_broadcast)

        broadcast_func_messages_ids.append((bot.send_message(message.chat.id, 'Разослать сообщение?',
                                                             reply_markup=markup)).id)

        UsersBD.commit()
        cursor.close()
        UsersBD.close()

@bot.callback_query_handler(func=lambda call: call.data == "send_broadcast")
def send_broadcast(call):
    global broadcast_message
    global broadcast_admin_id
    global broadcast_func_messages_ids

    bot.answer_callback_query(call.id)

    UsersBD = sqlite3.connect('UsersDB.sql')
    cursor = UsersBD.cursor()
    cursor.execute("SELECT chat_id FROM polzovately")
    chat_ids = cursor.fetchall()
    cursor.close()
    UsersBD.close()

    for func_message_id in broadcast_func_messages_ids:
        time.sleep(0.2)
        bot.delete_message(call.message.chat.id, func_message_id)
    broadcast_func_messages_ids = []

    time.sleep(del_time)
    sent_message = bot.send_message(call.message.chat.id, text='<b>РАССЫЛКА В ПРОЦЕССЕ</b>', parse_mode='html')
    start_time = datetime.now().strftime("%d-%m-%Y %H:%M").split('.')[0]


    if broadcast_message.content_type == 'photo':
        content_function = bot.send_photo
        content_args = {'caption': broadcast_message.caption}
        content_value = broadcast_message.photo[-1].file_id
    elif broadcast_message.content_type == 'text':
        content_function = bot.send_message
        content_args = {}
        content_value = broadcast_message.text

    send_count = 0
    for chat_id in chat_ids:
        if str(chat_id[0]) != str(broadcast_admin_id):
            try:
                content_function(chat_id[0], content_value, **content_args)
                send_count += 1
                time.sleep(0.1)
            except:
                pass

    bot.delete_message(call.message.chat.id, sent_message.id)
    time.sleep(del_time)

    if str(send_count)[-1] in ['2', '3', '4'] and str(send_count) not in ['12', '13', '14']:
        users_get = 'пользователя получили'
    elif str(send_count)[-1] == '1' and str(send_count) not in ['11']:
        users_get = 'пользователь получил'
    else:
        users_get = 'пользователей получили'
    broadcast_success = f'<b>{send_count}</b> {users_get} рассылку от:\n\n\U0001F4C7 {start_time.split()[0]}\n\n\U0000231A {start_time.split()[1]}'

    bot.send_message(call.message.chat.id, f'{broadcast_success}'
                                           f'\n'
                                           f'\n\U00002B07 <b>Содержание</b> \U00002B07', parse_mode='html')
    time.sleep(del_time)
    content_function(call.message.chat.id, content_value, **content_args)

    broadcast_admin_id = None
    broadcast_message = None

@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_broadcast(call):
    global broadcast_message
    global broadcast_admin_id
    global broadcast_func_messages_ids

    bot.answer_callback_query(call.id)

    for func_message_id in broadcast_func_messages_ids:
        time.sleep(0.2)
        bot.delete_message(call.message.chat.id, func_message_id)

    broadcast_admin_id = None
    broadcast_message = None
    broadcast_func_messages_ids = []

    time.sleep(del_time)
    sent_message = bot.send_message(call.message.chat.id, text='Рассылка отменена')
    time.sleep(2)
    bot.delete_message(call.message.chat.id, sent_message.id)



bot.infinity_polling() # Постоянная работа бота