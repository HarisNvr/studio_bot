import random
import telebot
from telebot import types
import time
import glob
from datetime import datetime
import sqlite3


# bot = telebot.TeleBot('6136773109:AAHkoWKgd8TspwQr_-9RQ6iuT10iXoLIrTE') # @CraftStudioBot
bot = telebot.TeleBot('6301286378:AAH6rwbVlOIeEtZkKQKqA2RykhD2E-oXq8g')  # @CraftStudioBotJr

tarot_debug_start = {} # Словарь для корректного удаления сообщения после Таро

# Словарь для хранения случайных карт для каждого пользователя
user_random_cards = {}

broadcast_admin_id = None  # Админ, который сейчас бродкастит
broadcast_message = None  # Тело рассылаемого сообщения

del_time = 0.8  # Задержка между сообщениями бота


@bot.message_handler(commands=['start', 'help'])  # Запуск бота по комманде /start и вызов главного меню по /help
def start(message):

    user = message.from_user.first_name  # Имя пользователя в базе SQL
    chat_id = message.chat.id  # ID чата с пользователем в базе SQL
    user_id = message.from_user.id  # ID пользователя в базе SQL

    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    time_full = datetime.now().time()  # Время сейчас
    hour = str(time_full).split(':')[0]  # Час сейчас в формате str

    markup = types.InlineKeyboardMarkup()  # Кнопки
    btn_socseti = types.InlineKeyboardButton(text='#МыВСети \U0001F4F1', callback_data='socseti')
    btn_shop = types.InlineKeyboardButton(text='Наш магазин  \U0001F6CD', callback_data='shop')
    btn_studia = types.InlineKeyboardButton(text='О студии \U0001F393', callback_data='studia')
    btn_viezd = types.InlineKeyboardButton(text='Выездные МК  \U0001F30D', callback_data='viezd')
    btn_tarot = types.InlineKeyboardButton(text='Карты ТАРО \U00002728', callback_data='tarot')
    btn_clean = types.InlineKeyboardButton(text=f'Очистить чат \U0001F9F9', callback_data='clean')
    markup.row(btn_studia, btn_shop)
    markup.row(btn_viezd, btn_socseti)
    markup.row(btn_tarot, btn_clean)

    admin_ids = [154395483, 1019826386]  # Проверка админов для вывода спец кнопки
    if chat_id in admin_ids:
        btn_admin = types.InlineKeyboardButton('\U0001F60E Кнопка администратора \U0001F60E', callback_data='admin')
        markup.row(btn_admin)

    if message.text == '/start':  # Обработка команды /start
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, message.message_id))  # Сохранение id сообщения от пользователя
        UsersBD.commit()

        cursor.execute('SELECT * FROM polzovately WHERE chat_id = ?', (chat_id,))
        row = cursor.fetchone()

        if row is None:  # Если имени пользователя нет в БД
            cursor.execute('INSERT INTO polzovately (chat_id, user_id, username) VALUES (?, ?, ?)', (chat_id, user_id, user))
        else:
            cursor.execute('UPDATE polzovately SET username = ? WHERE chat_id = ?', (user, chat_id))

        if int(hour) in range (6, 12):
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f'<b>Доброе утро, <u>{message.from_user.first_name}!</u> \U0001F642'
                                          f'\nМеня зовут CraftStudioBot.</b>'
                                          f'\nЧем я могу вам помочь?', parse_mode='html', reply_markup=markup).message_id))
        elif int(hour) in range (12, 18):
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f'<b>Добрый день, <u>{message.from_user.first_name}!</u> \U0001F642'
                                          f'\nМеня зовут CraftStudioBot.</b>'
                                          f'\nЧем я могу вам помочь?', parse_mode='html', reply_markup=markup).message_id))
        elif int(hour) in range (18, 23):
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f'<b>Добрый вечер, <u>{message.from_user.first_name}!</u> \U0001F642'
                                          f'\nМеня зовут CraftStudioBot.</b>'
                                          f'\nЧем я могу вам помочь?', parse_mode='html', reply_markup=markup).message_id))
        else:
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f'<b>Доброй ночи, <u>{message.from_user.first_name}!</u> \U0001F642'
                                          f'\nМеня зовут CraftStudioBot.</b>'
                                          f'\nЧем я могу вам помочь?', parse_mode='html', reply_markup=markup).message_id))
    else:

        if tarot_debug_start.get(chat_id) == 1:
            del tarot_debug_start[chat_id]
        else:
            bot.delete_message(message.chat.id, message.id)

        time.sleep(del_time)

        lang = random.randint(1, 1000)
        if lang == int(900):
            cursor.execute("SELECT username FROM polzovately WHERE chat_id = ?", (chat_id,))
            user_name = cursor.fetchone()[0]
            revers = ''.join(reversed(user_name))
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, f'<b>?ьчомоп мав угом я меч, <u>{revers}</u></b> \U0001F642', parse_mode='html' ,reply_markup=markup).message_id))
        elif lang == int(901):
            cursor.execute("SELECT username FROM polzovately WHERE chat_id = ?", (chat_id,))
            user_name = cursor.fetchone()[0]
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, f'<b>नमस्ते <u>{user_name}</u>, मैं आपकी कैसे मदद कर सकता हूँ?</b> \U0001F642', parse_mode='html' ,reply_markup=markup).message_id))
        elif lang == int(902):
            cursor.execute("SELECT username FROM polzovately WHERE chat_id = ?", (chat_id,))
            user_name = cursor.fetchone()[0]
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, f'<b>Greetings <u>{user_name}</u>, how can I help you?</b> \U0001F642', parse_mode='html' ,reply_markup=markup).message_id))
        elif lang == int(903):
            cursor.execute("SELECT username FROM polzovately WHERE chat_id = ?", (chat_id,))
            user_name = cursor.fetchone()[0]
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, f'<b>¡Hola! <u>{user_name}</u>, ¿le puedo ayudar en algo?</b> \U0001F642', parse_mode='html' ,reply_markup=markup).message_id))
        elif lang == int(904):
            cursor.execute("SELECT username FROM polzovately WHERE chat_id = ?", (chat_id,))
            user_name = cursor.fetchone()[0]
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, f'<b>你好 <u>{user_name}</u>, 我怎么帮你？</b> \U0001F642', parse_mode='html' ,reply_markup=markup).message_id))
        elif lang == int(999):
            cursor.execute("SELECT username FROM polzovately WHERE chat_id = ?", (chat_id,))
            user_name = cursor.fetchone()[0]
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, f'<b>Γειά σας <u>{user_name}</u>, πώς μπορώ να σε βοηθήσω?</b> \U0001F642', parse_mode='html' ,reply_markup=markup).message_id))
        else:
            cursor.execute("SELECT username FROM polzovately WHERE chat_id = ?", (chat_id,))
            user_name = cursor.fetchone()[0]
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, f'<b><u>{user_name}</u>, чем я могу вам помочь?</b> \U0001F642', parse_mode='html' ,reply_markup=markup).message_id))

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


@bot.message_handler(commands=['clean'])
def clean(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_da = types.InlineKeyboardButton(text = 'Да', callback_data = 'delete_message')
    btn_net = types.InlineKeyboardButton(text = 'Нет', callback_data = 'help')
    markup.row(btn_da, btn_net)
    bot.delete_message(message.chat.id, message.id)
    time.sleep(0.5)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                   (message.chat.id, bot.send_message(message.chat.id, f"Вы хотите полностью очистить этот чат?"
                                                                       f"\n"
                                                                       f"\n*Сообщения, отправленные более 48ч. назад и рассылка удалены не будут", reply_markup=markup).message_id))

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def delete_message(message):

    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()
    cursor.execute('SELECT message_id FROM message_ids WHERE chat_id = ?', (message.chat.id,))
    message_ids = cursor.fetchall()
    chat_id = message.chat.id

    #clean_delete_debug_start[chat_id] = 1

    bot.delete_message(message.chat.id, message.id)
    sent_message = bot.send_message(message.chat.id, f"<b>Идёт очистка чата</b> \U0001F9F9", parse_mode = 'html')

    for message_id in message_ids:
        try:
            bot.delete_message(message.chat.id, message_id[0])
            cursor.execute('DELETE FROM message_ids WHERE chat_id = ? AND message_id = ?', (message.chat.id, message_id[0]))
            UsersBD.commit()
            time.sleep(0.05)
        except Exception:
            cursor.execute('DELETE FROM message_ids WHERE chat_id = ? AND message_id = ?', (message.chat.id, message_id[0]))
            UsersBD.commit()

    cursor.close()
    UsersBD.close()

    bot.delete_message(sent_message.chat.id, sent_message.message_id)

    #start(message)


def admin(message): #Админское меню
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='help')
    markup.row(btn_Nazad)
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, '<b>Добро пожаловать в админское меню!</b>'
                                           '\n'
                                           '\n/broadcast - Начать процедуру рассылки'
                                           '\n'
                                           '\n/users - Узнать сколько пользователей в БД'
                                           '\n'
                                           '\n/proportions - Калькулятор пропорций', parse_mode='html', reply_markup=markup).message_id))

    UsersBD.commit()
    cursor.close()
    UsersBD.close()

#Начало админских комманд
@bot.message_handler(commands=['proportions'])
def proportions(message, debug = None):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    if message.chat.id in [154395483, 1019826386]:
        if debug == None:
            bot.delete_message(message.chat.id, message.id)
            time.sleep(del_time)
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f'Введите через пробел:\nПропорции компонентов <b>A</b> и <b>B</b>, и общую массу - <b>C</b>', parse_mode='html').message_id))
        bot.register_next_step_handler(message, calculate_proportions)
    else:
        chepuha(message)

    UsersBD.commit()
    cursor.close()
    UsersBD.close()

def calculate_proportions(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, message.message_id)) #Сохранение id сообщения от пользователя
    UsersBD.commit()

    markup = types.InlineKeyboardMarkup()
    btn_another_one = types.InlineKeyboardButton('Другая пропорция', callback_data='another_proportion')
    markup.add(btn_another_one)

    if len(message.text.split()) == 3:
        try:
            prop_input_split = message.text.replace(',', '.').split()

            A = float(prop_input_split[0])
            B = float(prop_input_split[1])
            C = float(prop_input_split[2])

            A_gr = (C / (A + B)) * A
            B_gr = (C / (A + B)) * B

            A_num = int(str(A_gr).split('.')[1])
            B_num = int(str(B_gr).split('.')[1])
            C_num = int(str(C).split('.')[1])

            if A_num == 0:
                A_new = int(A_gr)
            else:
                A_new = (str(round(A_gr, 2))).replace('.', ',')

            if B_num == 0:
                B_new = int(B_gr)
            else:
                B_new = (str(round(B_gr, 2))).replace('.', ',')

            if C_num == 0:
                C_new = int(C)
            else:
                C_new = str(C).replace('.', ',')


            cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.reply_to(message, f'Для раствора массой: <b>{C_new} гр.\nНеобходимо:</b>\n<b>{A_new} гр.</b> Компонента <b>A</b>\n<b>{B_new} гр.</b> Компонента <b>B</b>', reply_markup = markup,parse_mode='html').message_id))
        except:
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f"Неверный формат данных.\nПожалуйста, введите числа по образцу:\n<b>A B C</b>", parse_mode='html').message_id))
    else:
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f"Неверный формат данных.\nПожалуйста, введите числа по образцу:\n<b>A B C</b>", parse_mode='html').message_id))

    UsersBD.commit()
    cursor.close()
    UsersBD.close()

@bot.message_handler(commands=['users'])
def usersDB(message): #Обработка команды, которая возвращает кол-во пользователей из БД (Хоть раз взаимодействовали с ботом)
    if message.from_user.id in [154395483, 1019826386]:
        UsersBD = sqlite3.connect('UsersDB.sql')
        cursor = UsersBD.cursor()
        cursor.execute("SELECT COUNT(username) FROM polzovately")
        count = cursor.fetchone()[0]

        sent_message = bot.send_message(message.chat.id, f"Количество пользователей в БД: {count}")
        bot.delete_message(message.chat.id, message.id)

        cursor.close()
        UsersBD.close()

        time.sleep(3.5)

        bot.delete_message(sent_message.chat.id, sent_message.message_id)
    else:
        chepuha(message)


@bot.message_handler(commands=['broadcast'])
def start_broadcast(message):

    UsersBD = sqlite3.connect('UsersDB.sql')
    cursor = UsersBD.cursor()

    global broadcast_announce_1_id
    global broadcast_admin_id

    if message.from_user.id in [154395483, 1019826386] and broadcast_admin_id is None:
        broadcast_admin_id = message.from_user.id
        broadcast_announce_1 = bot.send_message(message.chat.id, "Отправьте сообщение для рассылки")
        broadcast_announce_1_id = broadcast_announce_1.message_id
        bot.delete_message(message.chat.id, message.id)
    elif message.from_user.id in [154395483, 1019826386] and broadcast_admin_id is not None:
        new_message_id = str(bot.send_message(message.chat.id, "Сейчас идёт рассылка другого администратора").message_id)
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, new_message_id))
    else:
        chepuha(message)

    UsersBD.commit()
    cursor.close()
    UsersBD.close()



@bot.message_handler(func=lambda message: message.from_user.id == broadcast_admin_id, content_types=['photo']) #Ввод фотографии для рассылки
def photo_broadcast(message):
    global broadcast_announce_2_id
    global broadcast_announce_3_id

    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    broadcast_announce_2_id = message.message_id

    global broadcast_message
    broadcast_message = message

    markup = types.InlineKeyboardMarkup()
    btn_send_broadcast = types.InlineKeyboardButton('Разослать', callback_data='send_broadcast_photo')
    btn_cancel_broadcast = types.InlineKeyboardButton('Отменить', callback_data='cancel')
    markup.add(btn_send_broadcast, btn_cancel_broadcast)
    broadcast_announce_3 = bot.send_message(message.chat.id, "Разослать сообщение?", reply_markup=markup)
    broadcast_announce_3_id = broadcast_announce_3.message_id

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def send_broadcast_photo(message):
    global broadcast_admin_id
    global broadcast_message
    global broadcast_announce_1_id
    global broadcast_announce_2_id
    global broadcast_announce_3_id
    n = 0

    chat_id_sql = sqlite3.connect('UsersDB.sql')
    cursor = chat_id_sql.cursor()
    cursor.execute("SELECT chat_id FROM polzovately")
    chat_ids = cursor.fetchall()

    bot.delete_message(message.chat.id, broadcast_announce_1_id)
    bot.delete_message(message.chat.id, broadcast_announce_2_id)
    bot.delete_message(message.chat.id, broadcast_announce_3_id)

    broadcast_announce_1_id = None
    broadcast_announce_2_id = None
    broadcast_announce_3_id = None

    today = str(datetime.now())
    today_new = today.split('.')[0]

    sent_message = bot.send_message(message.chat.id, text='Рассылка начата')

    for chat_id in chat_ids:
        if str(chat_id[0]) == str(broadcast_admin_id):
            pass
        else:
            try:
                bot.send_photo(chat_id[0], broadcast_message.photo[-1].file_id, caption=broadcast_message.caption)
                n += 1
                time.sleep(3)
            except Exception:
                pass

    bot.delete_message(sent_message.chat.id, sent_message.message_id)

    if str(n)[-1] in ['2', '3', '4'] and str(n) not in ['12', '13', '14']:
        bot.send_message(message.chat.id, text=f'Рассылка от {today_new} закончена, {n} пользователя её получили')
    elif str(n)[-1] == '1' and str(n) not in ['11']:
        bot.send_message(message.chat.id, text=f'Рассылка от {today_new} закончена, {n} пользователь её получил')
    else:
        bot.send_message(message.chat.id, text=f'Рассылка от {today_new} закончена, {n} пользователей её получили')

    bot.send_photo(message.chat.id, broadcast_message.photo[-1].file_id, caption=broadcast_message.caption)

    chat_id_sql.commit()
    cursor.close()
    chat_id_sql.close()

    broadcast_admin_id = None
    broadcast_message = None


@bot.message_handler(func=lambda message: message.from_user.id == broadcast_admin_id, content_types=['text']) #Ввод текста для рассылки
def text_broadcast(message):
    global broadcast_announce_2_id
    global broadcast_announce_3_id

    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    broadcast_announce_2_id = message.message_id

    global broadcast_message
    broadcast_message = message
    markup = types.InlineKeyboardMarkup()
    btn_send_broadcast = types.InlineKeyboardButton('Разослать', callback_data='send_broadcast_text')
    btn_cancel_broadcast = types.InlineKeyboardButton('Отменить', callback_data='cancel')
    markup.add(btn_send_broadcast, btn_cancel_broadcast)
    broadcast_announce_3 = bot.send_message(message.chat.id, "Разослать сообщение?", reply_markup=markup)
    broadcast_announce_3_id = broadcast_announce_3.message_id

    UsersBD.commit()
    cursor.close()
    UsersBD.close()



def send_broadcast_text(message):
    global broadcast_admin_id
    global broadcast_message
    global broadcast_announce_1_id
    global broadcast_announce_2_id
    global broadcast_announce_3_id
    n = 0

    chat_id_sql = sqlite3.connect('UsersDB.sql')
    cursor = chat_id_sql.cursor()
    cursor.execute("SELECT chat_id FROM polzovately")
    chat_ids = cursor.fetchall()

    bot.delete_message(message.chat.id, broadcast_announce_1_id)
    bot.delete_message(message.chat.id, broadcast_announce_2_id)
    bot.delete_message(message.chat.id, broadcast_announce_3_id)

    broadcast_announce_1_id = None
    broadcast_announce_2_id = None
    broadcast_announce_3_id = None

    today = str(datetime.now())
    today_new = today.split('.')[0]

    sent_message = bot.send_message(message.chat.id, text='Рассылка начата')

    for chat_id in chat_ids:
        if str(chat_id[0]) == str(broadcast_admin_id):
            pass
        else:
            try:
                bot.send_message(chat_id[0], broadcast_message.text)
                n += 1
                time.sleep(3)
            except Exception:
                pass

    bot.delete_message(sent_message.chat.id, sent_message.message_id)

    if str(n)[-1] in ['2', '3', '4'] and str(n) not in ['12', '13', '14']:
        bot.send_message(message.chat.id, text=f'Рассылка от {today_new} закончена, {n} пользователя её получили')
    elif str(n)[-1] == '1' and str(n) not in ['11']:
        bot.send_message(message.chat.id, text=f'Рассылка от {today_new} закончена, {n} пользователь её получил')
    else:
        bot.send_message(message.chat.id, text=f'Рассылка от {today_new} закончена, {n} пользователей её получили')

    bot.send_message(message.chat.id, broadcast_message.text)

    chat_id_sql.commit()
    cursor.close()
    chat_id_sql.close()

    broadcast_admin_id = None
    broadcast_message = None


def cancel_broadcast(message):
    global broadcast_admin_id
    global broadcast_message
    global broadcast_announce_1_id
    global broadcast_announce_2_id
    global broadcast_announce_3_id

    bot.delete_message(message.chat.id, broadcast_announce_1_id)
    bot.delete_message(message.chat.id, broadcast_announce_2_id)
    bot.delete_message(message.chat.id, broadcast_announce_3_id)

    broadcast_admin_id = None
    broadcast_message = None

    broadcast_announce_1_id = None
    broadcast_announce_2_id = None
    broadcast_announce_3_id = None

    sent_message = bot.send_message(message.chat.id, text='Рассылка отменена')
    time.sleep(5)
    bot.delete_message(sent_message.chat.id, sent_message.message_id)

#Конец админских комманд


def tarot_start(message): #Проверка условий для Таро

    chat_id = message.chat.id
    today = datetime.now().date()
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()
    cursor.execute("SELECT last_tarrot_date FROM polzovately WHERE chat_id = ?", (chat_id,))
    last_tarrot_date = cursor.fetchone()[0]

    admin_ids = [154395483, 1019826386]  # Проверка админов

    if chat_id in admin_ids:
        bot.delete_message(message.chat.id, message.id)
        tarot_debug_start[chat_id] = 1
        time.sleep(0.5)
        get_random_tarot_cards(message)
        start(message)
    else:
        if last_tarrot_date is None or last_tarrot_date == '':
            last_tarrot_date = today
            cursor.execute("UPDATE polzovately SET last_tarrot_date = ? WHERE chat_id = ?",
                           (last_tarrot_date.strftime("%Y-%m-%d"), chat_id))
            UsersBD.commit()
            bot.delete_message(message.chat.id, message.id)
            tarot_debug_start[chat_id] = 1
            time.sleep(0.5)
            get_random_tarot_cards(message)
            start(message)
        else:
            last_tarrot_date = datetime.strptime(last_tarrot_date, "%Y-%m-%d")
            if last_tarrot_date.date() == today:
                cursor.execute("SELECT username FROM polzovately WHERE chat_id = ?", (chat_id,))
                user_name = cursor.fetchone()[0]
                cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                               (message.chat.id, bot.send_message(message.chat.id, f'<u>{user_name}</u>, вы уже сегодня получили расклад, попробуйте завтра!', parse_mode='html').message_id))
                UsersBD.commit()

            else:
                cursor.execute("UPDATE polzovately SET last_tarrot_date = ? WHERE chat_id = ?", (today, chat_id))
                UsersBD.commit()
                bot.delete_message(message.chat.id, message.id)
                tarot_debug_start[chat_id] = 1
                time.sleep(0.5)
                get_random_tarot_cards(message)
                start(message)

    cursor.close()
    UsersBD.close()

def get_random_tarot_cards(message):
    OS_type = 1 # 1 = Windows, else = Ubuntu
    tarot_delay = 2.5 # Задержка между картами Таро

    if OS_type == 1:
        path = 'C:/Users/wwwha/PycharmProjects/CraftStudioBot/Tarot'
        cards = glob.glob(f'{path}/*.jpg')
    else:
        path = '/home/CSBot/Tarot'
        cards = glob.glob(f'{path}/*.jpg')

    user_id = message.chat.id
    UsersBD = sqlite3.connect('UsersDB.sql')
    cursor = UsersBD.cursor()

    user_random_cards[user_id] = []

    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, '<b>Расклад Таро - это всего лишь инструмент для ознакомления и развлечения. Расклад карт Таро не является истиной и не должен использоваться для принятия важных решений.</b>'
                          '\n'
                          '\n<u>CraftStudioArt</u> и его сотрудники не несут ответственности за любые действия и их последствия, которые повлекло использование данного расклада карт Таро.', parse_mode='html').message_id))

    UsersBD.commit()
    time.sleep(tarot_delay)

    if OS_type == 1:
        while len(user_random_cards[user_id]) < 3:
            card = random.choice(cards)
            card_num = int(card.split('\\')[-1].split('.')[0])

            if card_num not in [int(c.split('\\')[-1].split('.')[0]) for c in user_random_cards[user_id]]:
                if card_num % 2 == 1 and card_num + 1 not in [int(c.split('\\')[-1].split('.')[0]) for c in user_random_cards[user_id]]:
                    user_random_cards[user_id].append(card)
                elif card_num % 2 == 0 and card_num - 1 not in [int(c.split('\\')[-1].split('.')[0]) for c in user_random_cards[user_id]]:
                    user_random_cards[user_id].append(card)
    else:
        while len(user_random_cards[user_id]) < 3:
            card = random.choice(cards)
            card_num = int(card.split('/')[-1].split('.')[0])

            if card_num not in [int(c.split('/')[-1].split('.')[0]) for c in user_random_cards[user_id]]:
                if card_num % 2 == 1 and card_num + 1 not in [int(c.split('/')[-1].split('.')[0]) for c in
                                                              user_random_cards[user_id]]:
                    user_random_cards[user_id].append(card)
                elif card_num % 2 == 0 and card_num - 1 not in [int(c.split('/')[-1].split('.')[0]) for c in
                                                                user_random_cards[user_id]]:
                    user_random_cards[user_id].append(card)

    captions = ['Прошлое', 'Настоящее', 'Будущее']

    for card, caption in zip(user_random_cards[user_id], captions):
        with open(card, 'rb') as photo:
            with open(f'{card[:-4]}.txt', 'r', encoding='utf-8') as text:
                description = text.read()
            cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                               (message.chat.id, bot.send_photo(message.chat.id, photo, caption=f'<b>{caption}</b>: {description}', parse_mode='html').message_id))
            UsersBD.commit()
            time.sleep(tarot_delay)

    cursor.close()
    UsersBD.close()


@bot.message_handler(commands=['studia'])
def studia(message): #Вкладка студии
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_napravleniya = types.InlineKeyboardButton('Подробнее о направлениях', callback_data='napravleniya')
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='help')
    btn_2gis = types.InlineKeyboardButton(text='Наша студия в 2GIS', url='https://go.2gis.com/8od46')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Записаться на МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_napravleniya)
    markup.row(btn_bronirovanie)
    markup.row(btn_2gis)
    markup.row(btn_Nazad)
    img_studia = open('IMG_5377.PNG', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                   (message.chat.id, bot.send_photo(message.chat.id, img_studia, caption=f'<b>Наша мастерская</b> – это то место, где вы сможете раскрыть свой потенциал и реализовать идеи в разных направлениях: свечеварение, эпоскидная смола, рисование, роспись одежды и многое другое. '
                                                        '\n'
                                                        '\n\U0001F4CD<u>Наши адреса:'
                                                        '\n</u><b>\U00002693 г. Новороссийск, с. Цемдолина, ул. Цемесская, д. 10'
                                                        '\n\U00002600 г. Анапа, с. Витязево, ул. Курганная, д. 29</b>', parse_mode='html', reply_markup=markup).message_id))
    img_studia.close()
    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def napravleniya(message): #Кнопки с описаниями занятий для вкладки СТУДИЯ
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Smola = types.InlineKeyboardButton(text='Эпоксидная смола', callback_data='Smola')
    btn_Gips = types.InlineKeyboardButton (text='Гипс', callback_data='Gips')
    btn_Sketching = types.InlineKeyboardButton (text='Скетчинг', callback_data='Sketching')
    btn_TieDye = types.InlineKeyboardButton (text='Тай-Дай', callback_data='TieDye')
    btn_CustomCloth = types.InlineKeyboardButton (text='Роспись одежды', callback_data='CustomCloth')
    btn_Svechi = types.InlineKeyboardButton (text='Свечеварение', callback_data='Svechi')
    btn_Nazad = types.InlineKeyboardButton (text='Назад', callback_data='studia')
    markup.row(btn_Smola, btn_Gips)
    markup.row(btn_Sketching,btn_TieDye)
    markup.row(btn_CustomCloth, btn_Svechi)
    markup.row(btn_Nazad)
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f'<b>Выберите <u>направление,</u> о котором хотите узнать подробнее:</b>', parse_mode='html', reply_markup=markup).message_id))

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


@bot.message_handler(commands=['mk'])
def viezd(message): #Вкладка выездных МК
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='help')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Забронировать МК \U000026A1', url='https://t.me/elenitsa17')
    btn_napravleniya_2 = types.InlineKeyboardButton('Подробнее о направлениях', callback_data='napravleniya_2')
    markup.row(btn_napravleniya_2)
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_studia = open('IMG_5378.PNG', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, img_studia, caption='<b>Вы хотите удивить гостей творческим мастер–классом?</b> '
                                                        '\n'
                                                        '\n Наша студия готова приехать к вам с оборудованием и материалами по любой теме из нашего каталога: свечеварение, рисование, роспись одежды и другие. Мы обеспечим все необходимое для проведения МК в любом месте – в помещении или на свежем воздухе. '
                                                        '\n'
                                                        '\n <u>Все гости получат новые знания, навыки и подарки, сделанные своими руками!</u>' , parse_mode='html', reply_markup=markup).message_id))
    img_studia.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def napravleniya_2(message): #Кнопки с описаниями занятий для вкладки ВЫЕЗДНЫЕ МК
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Gips = types.InlineKeyboardButton (text='Гипс', callback_data='Gips_2')
    btn_TieDye = types.InlineKeyboardButton (text='Тай-Дай', callback_data='TieDye_2')
    btn_Svechi = types.InlineKeyboardButton (text='Свечеварение', callback_data='Svechi_2')
    btn_Nazad = types.InlineKeyboardButton (text='Назад', callback_data='viezd')
    markup.row(btn_Gips)
    markup.row(btn_TieDye)
    markup.row(btn_Svechi)
    markup.row(btn_Nazad)
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f'<b>Выберите <u>направление,</u> о котором хотите узнать подробнее:</b>', parse_mode='html', reply_markup=markup).message_id))

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


@bot.message_handler(commands=['shop'])
def shop(message): #Вкладка магазина
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_catalog_main = types.InlineKeyboardButton ('Каталог \U0001F50D', callback_data='catalog_1')
    btn_dostavka = types.InlineKeyboardButton ('Доставка \U0001F4E6', callback_data='dostavka')
    btn_zakaz = types.InlineKeyboardButton ('Как заказать \U00002705', callback_data='zakaz')
    btn_oplata = types.InlineKeyboardButton ('Оплата \U0001F4B3', callback_data='oplata')
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    btn_nazad = types.InlineKeyboardButton ('Назад', callback_data='help')
    markup.row(btn_zakaz, btn_catalog_main)
    markup.row(btn_oplata, btn_dostavka)
    markup.row(btn_vopros)
    markup.row(btn_nazad)
    shop_img = open('craft_shop.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, shop_img, caption=f'<b>Добро пожаловать в наш крафтовый магазин \U00002728</b>'
                                                     f'\n'
                                                     f'\n Здесь вы найдете уникальные и качественные изделия ручной работы, созданные с любовью и нежностью. Мы предлагаем вам широкий ассортимент товаров: декор для дома, подарки, украшения, сухоцветы и многое другое.'
                                                     f'\n'
                                                     f'\n <b>Мы гарантируем вам:</b> <u>высокое качество, индивидуальный подход и быструю отправку.</u>', parse_mode='html', reply_markup=markup).message_id))
    shop_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


#Начало страниц каталога
def catalog_main(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_catalog_str1 = types.InlineKeyboardButton('1', callback_data='catalog_1')
    btn_catalog_str2 = types.InlineKeyboardButton('2', callback_data='catalog_2')
    btn_catalog_str3 = types.InlineKeyboardButton('3', callback_data='catalog_3')
    btn_catalog_str4 = types.InlineKeyboardButton('4', callback_data='catalog_4')
    btn_catalog_str5 = types.InlineKeyboardButton('5', callback_data='catalog_5')
    btn_catalog_str6 = types.InlineKeyboardButton('6', callback_data='catalog_6')
    btn_catalog_str7 = types.InlineKeyboardButton('7', callback_data='catalog_7')
    btn_catalog_exit = types.InlineKeyboardButton('Выйти из каталога', callback_data='shop')
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_catalog_str1,btn_catalog_str2,btn_catalog_str3)
    markup.row(btn_catalog_str4,btn_catalog_str5,btn_catalog_str6)
    markup.row(btn_catalog_str7, btn_catalog_exit)
    markup.row(btn_vopros)
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, '<b>Пожалуйста, выберите страницу каталога, которая вас интересует:</b>', parse_mode='html', reply_markup=markup).message_id))

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def catalog_1(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_sled = types.InlineKeyboardButton('Следующая', callback_data='catalog_2')
    btn_catalog_main = types.InlineKeyboardButton('Выбрать страницу:', callback_data='catalog_main')
    btn_catalog_exit = types.InlineKeyboardButton('Выйти из каталога', callback_data='shop')
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_sled)
    markup.row(btn_catalog_main)
    markup.row(btn_vopros)
    markup.row(btn_catalog_exit)
    cat_1_img = open('cat_1.png','rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, cat_1_img, caption=f'<b>Страница №1</b>', parse_mode = 'html', reply_markup=markup).message_id))
    cat_1_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def catalog_2(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_sled = types.InlineKeyboardButton('Следующая', callback_data='catalog_3')
    btn_pred = types.InlineKeyboardButton('Предыдущая', callback_data='catalog_1')
    btn_catalog_main = types.InlineKeyboardButton('Выбрать страницу:', callback_data='catalog_main')
    btn_catalog_exit = types.InlineKeyboardButton('Выйти из каталога', callback_data='shop')
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_pred,btn_sled)
    markup.row(btn_catalog_main)
    markup.row(btn_vopros)
    markup.row(btn_catalog_exit)
    cat_2_img = open('cat_2.png','rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, cat_2_img, caption=f'<b>Страница №2</b>', parse_mode = 'html', reply_markup=markup).message_id))
    cat_2_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def catalog_3(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_sled = types.InlineKeyboardButton('Следующая', callback_data='catalog_4')
    btn_pred = types.InlineKeyboardButton('Предыдущая', callback_data='catalog_2')
    btn_catalog_main = types.InlineKeyboardButton('Выбрать страницу:', callback_data='catalog_main')
    btn_catalog_exit = types.InlineKeyboardButton('Выйти из каталога', callback_data='shop')
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_pred,btn_sled)
    markup.row(btn_catalog_main)
    markup.row(btn_vopros)
    markup.row(btn_catalog_exit)
    cat_3_img = open('cat_3.png','rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, cat_3_img, caption=f'<b>Страница №3</b>', parse_mode = 'html', reply_markup=markup).message_id))
    cat_3_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def catalog_4(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_sled = types.InlineKeyboardButton('Следующая', callback_data='catalog_5')
    btn_pred = types.InlineKeyboardButton('Предыдущая', callback_data='catalog_3')
    btn_catalog_main = types.InlineKeyboardButton('Выбрать страницу:', callback_data='catalog_main')
    btn_catalog_exit = types.InlineKeyboardButton('Выйти из каталога', callback_data='shop')
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_pred,btn_sled)
    markup.row(btn_catalog_main)
    markup.row(btn_vopros)
    markup.row(btn_catalog_exit)
    cat_4_img = open('cat_4.png','rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, cat_4_img, caption=f'<b>Страница №4</b>', parse_mode = 'html', reply_markup=markup).message_id))
    cat_4_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def catalog_5(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_sled = types.InlineKeyboardButton('Следующая', callback_data='catalog_6')
    btn_pred = types.InlineKeyboardButton('Предыдущая', callback_data='catalog_4')
    btn_catalog_main = types.InlineKeyboardButton('Выбрать страницу:', callback_data='catalog_main')
    btn_catalog_exit = types.InlineKeyboardButton('Выйти из каталога', callback_data='shop')
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_pred,btn_sled)
    markup.row(btn_catalog_main)
    markup.row(btn_vopros)
    markup.row(btn_catalog_exit)
    cat_5_img = open('cat_5.png','rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, cat_5_img, caption=f'<b>Страница №5</b>', parse_mode = 'html', reply_markup=markup).message_id))
    cat_5_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def catalog_6(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_sled = types.InlineKeyboardButton('Следующая', callback_data='catalog_7')
    btn_pred = types.InlineKeyboardButton('Предыдущая', callback_data='catalog_5')
    btn_catalog_main = types.InlineKeyboardButton('Выбрать страницу:', callback_data='catalog_main')
    btn_catalog_exit = types.InlineKeyboardButton('Выйти из каталога', callback_data='shop')
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_pred, btn_sled)
    markup.row(btn_catalog_main)
    markup.row(btn_vopros)
    markup.row(btn_catalog_exit)
    cat_6_img = open('cat_6.png','rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, cat_6_img, caption=f'<b>Страница №6</b>', parse_mode = 'html', reply_markup=markup).message_id))
    cat_6_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def catalog_7(message):
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_pred = types.InlineKeyboardButton('Предыдущая', callback_data='catalog_6')
    btn_catalog_main = types.InlineKeyboardButton('Выбрать страницу:', callback_data='catalog_main')
    btn_catalog_exit = types.InlineKeyboardButton('Выйти из каталога', callback_data='shop')
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_pred)
    markup.row(btn_catalog_main)
    markup.row(btn_vopros)
    markup.row(btn_catalog_exit)
    cat_7_img = open('cat_7.png','rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, cat_7_img, caption=f'<b>Страница №7</b>', parse_mode = 'html', reply_markup=markup).message_id))
    cat_7_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()
#Конец страниц каталога


def dostavka(message): #Вкладка "Доставка"
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_vopros= types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    btn_nazad = types.InlineKeyboardButton('Назад', callback_data='shop')
    markup.row(btn_vopros)
    markup.row(btn_nazad)
    dostavka_img = open('dostavka.jpg', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, dostavka_img, caption='<b>После изготовления вашего заказа, на следующий рабочий день мы начинаем процесс доставки, который включает в себя следующее:</b>'
                                                          '\n'
                                                          '\n <u>ШАГ 1</u>: Бережно и надёжно упакуем ваш заказ '
                                                          '\n'
                                                          '\n <u>ШАГ 2</u>: Отвезем его в выбранную вами транспортную компанию (СДЕК, DPD, Boxberry, почта России)'
                                                          '\n'
                                                          '\n <u>ШАГ 3</u>: В течение нескольких дней вы сможете получить ваш заказ'
                                                          '\n'
                                                          '\n Если у вас остались какие-либо вопросы, касательно процесса доставки - вы всегда можете написать нам!', parse_mode='html', reply_markup=markup).message_id))
    dostavka_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def oplata(message): #Вкладка "Оплата"
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    btn_nazad = types.InlineKeyboardButton('Назад', callback_data='shop')
    markup.row(btn_vopros)
    markup.row(btn_nazad)
    oplata_img = open('oplata.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, oplata_img, caption='<u>После выбора товаров и их характеристик, а также согласования с мастером - вам будет предложено оплатить заказ.</u>'
                                                        '\n'
                                                        '\n<b>Обращаем ваше внимание, что наша студия работает только по 100% предоплате!</b>'
                                                        '\n'
                                                        '\n Мы принимаем банковские переводы на карту или по СБП, если вам необходим чек для отчётности - мы вам его предоставим. После получения оплаты мы начинаем изготовление вашего заказа в рамках согласованного заранее срока', parse_mode='html', reply_markup=markup).message_id))
    oplata_img.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def zakaz(message): #Вкладка "Как заказать"
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_vopros = types.InlineKeyboardButton(text='\U000026A1 Связаться с нами \U000026A1', url='https://t.me/elenitsa17')
    btn_nazad = types.InlineKeyboardButton('Назад', callback_data='shop')
    markup.row(btn_vopros)
    markup.row(btn_nazad)
    img_zakaz = open('zakaz.jpg' ,'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id,img_zakaz, caption='<b>Заказать красивое изделие ручной работы очень просто! Вам потребуется:</b>'
                                            '\n'
                                            '\n1) Выбрать из каталога товар, который вам понравился.'
                                            '\n'
                                            '\n2) Запомнить порядковый номер этого товара.'
                                            '\n'
                                            '\n3) Написать нам номер или несколько номеров товаров, которые вы хотели бы заказать. Наш мастер подскажет, какие цвета/ароматы доступны для данного типа товара, а также ответит на интересующие вопросы.'
                                            '\n'
                                            '\n<u>Фотографии из каталога являются исключительно ознакомительными. Мы не гарантируем 100% повторения изделия с фото, т.к. каждое изделие изготавливается вручную "с нуля".</u>', parse_mode='html', reply_markup=markup).message_id))
    img_zakaz.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


@bot.message_handler(commands=['socseti'])
def socseti(message): #Кнопки с соц.сетями в 2-м уровне меню
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_VK = types.InlineKeyboardButton (text='Группа VK', url='https://vk.com/elenitsa_custom') #Кнопка VK
    btn_Instagram = types.InlineKeyboardButton (text= 'Instagram' , url= 'https://instagram.com/craft_studio_art') #Кнопка Instagram
    btn_TG = types.InlineKeyboardButton (text= 'Наш канал в Telegram', url= 'http://t.me/craft_studio_art') #Кнопка Telegram
    btn_WA = types.InlineKeyboardButton (text= 'WhatsApp', url='https://wa.me/79186365539') #Кнопка WhatsApp
    btn_Nazad = types.InlineKeyboardButton (text= 'Назад', callback_data='help')
    btn_raboty = types.InlineKeyboardButton('Примеры работ на Я.Диск', url='https://disk.yandex.ru/d/Fg1AHRy9DQPQhQ')
    btn_Telega = types.InlineKeyboardButton(text='Telegram', url='https://t.me/elenitsa17')
    btn_support = types.InlineKeyboardButton(text='Тех. поддержка БОТА', url='https://t.me/HarisNvrsk')
    markup.row(btn_Instagram, btn_VK)
    markup.row(btn_Telega, btn_WA)
    markup.row(btn_TG)
    markup.row(btn_raboty)
    markup.row(btn_support)
    markup.row(btn_Nazad)
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, f'<b>Какая <u>соц.сеть</u>, вас интересует:</b>', parse_mode='html', reply_markup=markup).message_id))

    UsersBD.commit()
    cursor.close()
    UsersBD.close()

#Начало описания направлений
def Smola(message): #Описание занятия по смоле в студии
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='napravleniya')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Записаться на МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_Smola = open('Smola_img.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id,img_Smola , caption=f'<b>Эпоксидная смола</b> - это универсальный материал, который позволяет создавать разнообразные изделия и декоративные элементы.'
                                                    f'\n'
                                                    f'\n На нашем занятии вы научитесь основам заливки. Мы покажем вам различные техники, а также расскажем о тонкостях при работе со смолой. Вы сможете создать свои уникальные и неповторимые изделия из смолы.'
                                                    f'\n'
                                                    f'\n Смола застывает в течении 24 часов. Своё изделие вы сможете забрать уже на следующий день. После отвердевания, смола становится безвредной и может контактировать с холодными продуктами (орешки, сухофрукты, конфеты и прочее).'
                                                    f'\n'
                                                    f'\n Мы обеспечим вам необходимую защитную экипировку: перчатки, респираторы и фартуки. Занятия проводятся в хорошо проветриваемом помещении.'
                                                    f'\n'
                                                    f'\n<b>Стоимость:</b> от 700\U000020BD за изделие'
                                                    f'\n'
                                                    f'\n<u>Уточняйте актуальное расписание, перечень изделий и наличие мест у мастера!</u>',parse_mode='html', reply_markup=markup).message_id))
    img_Smola.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def Gips(message): #Описание занятия по Гипсу в студии
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='napravleniya')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Записаться на МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_Gips = open('Gips_img.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id,img_Gips ,caption=f'<b>Гипс</b> - это универсальный и простой в работе материал, из которого можно создавать различные предметы декора и подарки. '
                                                     f'\n'
                                                     f'\n  На нашем занятии вы познакомитесь с основами литья из гипса и узнаете, как изготавливать гипсовые изделия своими руками. Мы научим вас правильно замешивать гипсовый раствор, расскажем о секретах получения крепкого, ровного изделия с минимальным количеством пузырей. '
                                                     f'\n'
                                                     f'\n  Вы сможете создать свои неповторимые изделия и украсить дом. Так же гипсовые изделия – это отличный подарок, сделанный своими руками.'
                                                     f'\n'
                                                     f'\n<b>Стоимость:</b> от 500\U000020BD за человека'
                                                     f'\n'
                                                     f'\n<u>Уточняйте актуальное расписание и наличие мест у мастера!</u>',parse_mode='html', reply_markup=markup).message_id))
    img_Gips.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def Gips_2(message): #Описание занятия по Гипсу на выезд
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='napravleniya_2')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Забронировать МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_Gips = open('Gips_img.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id,img_Gips ,caption=f'<b>Гипс</b> - это универсальный и простой в работе материал, из которого можно создавать различные предметы декора и подарки. '
                                                     f'\n'
                                                     f'\n  На нашем занятии вы познакомитесь с основами литья из гипса и узнаете, как изготавливать гипсовые изделия своими руками. Мы научим вас правильно замешивать гипсовый раствор, расскажем о секретах получения крепкого, ровного изделия с минимальным количеством пузырей. '
                                                     f'\n'
                                                     f'\n  Вы сможете создать свои неповторимые изделия и украсить дом. Так же гипсовые изделия – это отличный подарок, сделанный своими руками.'
                                                     f'\n'
                                                     f'\n<b>Стоимость:</b> от 600\U000020BD за человека'
                                                     f'\n'
                                                     f'\n<u>Минимальное количество человек и стоимость выезда на локацию проведения уточняйте у мастера!</u>',parse_mode='html', reply_markup=markup).message_id))
    img_Gips.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def Sketching(message): #Описание занятия по Скетчингу в студии
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='napravleniya')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Записаться на МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_Sketching = open('Sketching_img.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, img_Sketching, caption='<b>Скетчинг</b> - это техника быстрого рисования набросков и эскизов, которая помогает визуализировать идеи, эмоции и впечатления. На нашем занятии вы узнаете, как рисовать скетчи от руки с помощью разных материалов: карандашей, маркеров, пастели. '
                                                           '\n'
                                                           '\n  Вы научитесь выбирать подходящие объекты для скетчинга, определять перспективу и светотень, создавать композицию и цветовую гамму. Мы покажем вам различные стили и техники скетчинга. '
                                                           '\n'
                                                           '\n  Вы сможете создать свои уникальные скетчи на любые темы: природа, архитектура, мода и многое другое.'
                                                           '\n'
                                                           '\n<b>Стоимость:</b> от 600\U000020BD за человека'
                                                           '\n'
                                                           '\n<u>Уточняйте актуальное расписание и наличие мест у мастера!</u>',parse_mode='html', reply_markup=markup).message_id))
    img_Sketching.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def TieDye(message): #Описание занятия по Тай-Дай
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='napravleniya')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Записаться на МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_TieDye = open('TieDye_photo.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, img_TieDye, caption=f'<b>Тай-дай</b> - это техника окрашивания ткани при помощи скручивания, которая позволяет создавать яркие и оригинальные узоры. На нашем занятии вы узнаете, как делать тай-дай своими руками. Вы научитесь выбирать подходящие красители и способы завязывания ткани для получения разных эффектов. '
                                                        f'\n'
                                                        f'\n  Мы покажем вам различные стили и техники тай-дай: от классического спирального до современного мраморного. Вы сможете создать свои уникальные вещи в стиле тай-дай: футболки, платья, джинсы, шопперы и другое. '
                                                        f'\n'
                                                        f'\n<b>А также при помощи тай-дай можно подарить вторую жизнь своей любимой вещи.</b>'
                                                        f'\n'
                                                        f'\n<b>Стоимость:</b>'
                                                        f'\nот 500\U000020BD за человека, без предоставления футболки'
                                                        f'\nот 900\U000020BD за человека, с предоставлением футболки'
                                                        f'\n'
                                                        f'\n<u>Уточняйте актуальное расписание и наличие мест у мастера!</u>', parse_mode='html', reply_markup=markup).message_id))
    img_TieDye.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def TieDye_2(message): #Описание занятия по Тай-Дай на выезд
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='napravleniya_2')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Забронировать МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_TieDye = open('TieDye_photo.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, img_TieDye, caption=f'<b>Тай-дай</b> - это техника окрашивания ткани при помощи скручивания, которая позволяет создавать яркие и оригинальные узоры. На нашем занятии вы узнаете, как делать тай-дай своими руками. Вы научитесь выбирать подходящие красители и способы завязывания ткани для получения разных эффектов. '
                                                        f'\n'
                                                        f'\n  Мы покажем вам различные стили и техники тай-дай: от классического спирального до современного мраморного. Вы сможете создать свои уникальные вещи в стиле тай-дай: футболки, платья, джинсы, шопперы и другое. '
                                                        f'\n'
                                                        f'\nА также при помощи тай-дай можно подарить вторую жизнь своей любимой вещи.'
                                                        f'\n'
                                                        f'\n<b>Стоимость:</b>'
                                                        f'\nот 500\U000020BD за человека, без предоставления футболки'
                                                        f'\nот 900\U000020BD за человека, с предоставлением футболки'
                                                        f'\n'
                                                        f'\n<u>Минимальное количество человек и стоимость выезда на локацию проведения уточняйте у мастера!</u>', parse_mode='html', reply_markup=markup).message_id))
    img_TieDye.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def CustomCloth(message): #Описание занятия по Кастому одежды в студии
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='napravleniya')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Записаться на МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_CustomCloth = open('CustomCloth_img.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, img_CustomCloth, caption='<b>Роспись одежды</b> - это творческий способ преобразить свои вещи и сделать их уникальными. На нашем занятии вы узнаете, как рисовать на ткани акриловыми красками и какие материалы, инструменты для этого нужны. '
                                                             '\n'
                                                             '\n  Вы научитесь выбирать подходящие рисунки и узоры, переносить их на одежду, а также использовать разные техники: от простых надписей, до полноценных картин. Мы покажем вам различные стили росписи: от классических цветочных мотивов до современных абстрактных рисунков. Вы сможете разрисовать свою одежду в соответствии со своим вкусом и стилем. '
                                                             '\n'
                                                             '\n  Мы используем специальные краски, которые не смываются с ткани. Поэтому расписанная вещь будет радовать вас очень долго.'
                                                             '\n'
                                                             '\n<b>Стоимость:</b>'
                                                             '\nРоспись футболки (футболку не предоставляем) - от 1000\U000020BD/шт'
                                                             '\nРоспись шоппера (шоппер предоставим) - от 1500\U000020BD/шт'
                                                             '\n'
                                                             '\n<u>Уточняйте актуальное расписание и наличие мест у мастера!</u>', parse_mode='html', reply_markup=markup).message_id))
    img_CustomCloth.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def Svechi(message): #Описание занятия по Свечеварению в студии
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='napravleniya')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Записаться на МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_svechi = open('Svechi_photo.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, img_svechi, caption=f'\n  <b>Ароматические свечи</b> - это не только красивый и уютный элемент декора, но и способ создать особую атмосферу в доме. '
                                                        f'\n'
                                                        f'\n  На нашем занятии вы создадите свечу своими руками из натуральных ингредиентов: соевого воска, эфирных масел, хлопкового или деревянного фитиля. Вы сможете выбрать ароматы по своему вкусу (более 20 различных ароматов), украсить свечу сухоцветами, шиммером. Мы расскажем вам о тонкостях процесса изготовления свечей, а также о том, как правильно использовать и хранить их. '
                                                        f'\n'
                                                        f'\n  Вы получите не только полезные знания и навыки, но и удовольствие от творчества и релаксации. '
                                                        f'\n'
                                                        f'\n  По окончании занятия вы сможете забрать с собой свои уникальные аромасвечи и украсить свой дом, или подарить близкому человеку.'
                                                        f'\n'
                                                        f'\n<b>Стоимость:</b>'
                                                        f'\nСвеча в кокосе - 1000\U000020BD/шт'
                                                        f'\nСвеча 50мл – 500\U000020BD/шт'
                                                        f'\nСвеча в баночке 120мл – 800\U000020BD/шт'
                                                        f'\nСвеча в банке 200 мл – 900\U000020BD/шт'
                                                        f'\nСвеча в банке 250мл – 1200\U000020BD/шт'
                                                        f'\n'
                                                        f'<u>Уточняйте актуальное расписание и наличие мест у мастера!</u>',parse_mode='html', reply_markup=markup).message_id))
    img_svechi.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


def Svechi_2(message): #Описание занятия по Свечеварению в студии
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    markup = types.InlineKeyboardMarkup()
    btn_Nazad = types.InlineKeyboardButton(text='Назад', callback_data='napravleniya_2')
    btn_bronirovanie = types.InlineKeyboardButton(text='\U000026A1 Забронировать МК \U000026A1', url='https://t.me/elenitsa17')
    markup.row(btn_bronirovanie)
    markup.row(btn_Nazad)
    img_svechi = open('Svechi_photo.png', 'rb')
    bot.delete_message(message.chat.id, message.id)
    time.sleep(del_time)
    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_photo(message.chat.id, img_svechi, caption=f'\n  <b>Ароматические свечи</b> - это не только красивый и уютный элемент декора, но и способ создать особую атмосферу в доме. '
                                                        f'\n'
                                                        f'\n  На нашем занятии вы создадите свечу своими руками из натуральных ингредиентов: соевого воска, эфирных масел, хлопкового или деревянного фитиля. Вы сможете выбрать ароматы по своему вкусу (более 20 различных ароматов), украсить свечу сухоцветами, шиммером. Мы расскажем вам о тонкостях процесса изготовления свечей, а также о том, как правильно использовать и хранить их. '
                                                        f'\n'
                                                        f'\n  Вы получите не только полезные знания и навыки, но и удовольствие от творчества и релаксации. '
                                                        f'\n'
                                                        f'\n  По окончании занятия вы сможете забрать с собой свои уникальные аромасвечи и украсить свой дом, или подарить близкому человеку.'
                                                        f'\n'
                                                        f'\n<b>Стоимость:</b>'
                                                        f'\nСвеча в кокосе - 1000\U000020BD/шт'
                                                        f'\nСвеча 50мл – 500\U000020BD/шт'
                                                        f'\nСвеча в баночке 120мл – 800\U000020BD/шт'
                                                        f'\nСвеча в банке 200 мл – 900\U000020BD/шт'
                                                        f'\nСвеча в банке 250мл – 1200\U000020BD/шт'
                                                        f'\n'
                                                        f'\n<u>Минимальное количество человек и стоимость выезда на локацию проведения уточняйте у мастера!</u>',parse_mode='html', reply_markup=markup).message_id))
    img_svechi.close()

    UsersBD.commit()
    cursor.close()
    UsersBD.close()
#Конец описания направлений


def chepuha(message): #Обработка чепухи и направление на помощь
    user = message.from_user.first_name  # Имя пользователя в базе SQL
    chat_id = message.chat.id  # ID чата с пользователем в базе SQL
    user_id = message.from_user.id  # ID пользователя в базе SQL
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()
    cursor.execute("SELECT username FROM polzovately WHERE chat_id = ?", (chat_id,))
    user_name = cursor.fetchone()[0]

    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, bot.send_message(message.chat.id, text=f'Извините {user_name}, я вас не понимаю. '
                                           f'\n'
                                           f'\nПопробуйте написать /help для возврата в главное меню или воспользуйтесь кнопкой "Меню" около окна ввода сообщения').message_id))

    UsersBD.commit()
    cursor.close()
    UsersBD.close()


@bot.message_handler(content_types=['text']) #Стоит в конце, т.к. должен исполняться последним, чтобы не было конфликтов
def easter_eggs(message): #Пасхалки
    UsersBD = sqlite3.connect('UsersDB.sql')  # База данных SQL с ID и Именем пользователя
    cursor = UsersBD.cursor()

    cursor.execute('INSERT INTO message_ids VALUES (?, ?)', (message.chat.id, message.message_id)) #Сохранение id сообщения от пользователя
    UsersBD.commit()

    if message.text.lower() =='акуна': #Пасхалка король лев_1
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, text='Матата!').message_id))
        UsersBD.commit()
    elif message.text.lower() =='матата': #Пасхалка король лев_2
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, text='Акуна!').message_id))
        UsersBD.commit()
    elif message.text.lower() == 'матата акуна': #Пасхалка король лев_3
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_message(message.chat.id, text='\U0001F417 \U0001F439').message_id))
        UsersBD.commit()
    elif message.text.lower() =='акуна матата': #Пасхалка король лев_4
        img_akuna = open('Akuna.jpg', 'rb')
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_photo(message.chat.id, img_akuna, caption=f'<b>Акуна Матата!</b>', parse_mode='html').message_id))
        UsersBD.commit()
        img_akuna.close()
    elif message.text == '\U0001F346': #Пасхалка бот_пик
        img_bolt = open('bolt.png', 'rb')
        cursor.execute('INSERT INTO message_ids VALUES (?, ?)',
                       (message.chat.id, bot.send_photo(message.chat.id, img_bolt).message_id))
        UsersBD.commit()
        img_bolt.close()
    else:
        chepuha(message)

    cursor.close()
    UsersBD.close()


@bot.callback_query_handler(func=lambda callback: True) #Обработка функции callback
def buttons(callback):
    if callback.data == 'help': # Все кнопки "назад", которые возвращают в 1-й уровень меню из 2-го
        bot.answer_callback_query(callback.id)
        start(callback.message)
    elif callback.data == 'clean': # Очистка чата_вопрос
        bot.answer_callback_query(callback.id)
        clean(callback.message)
    elif callback.data == 'delete_message': # Очистка чата_действие
        bot.answer_callback_query(callback.id)
        delete_message(callback.message)
    elif callback.data == 'admin': # Админская кнопка
        bot.answer_callback_query(callback.id)
        admin(callback.message)
    elif callback.data == 'another_proportion': # Пропорции
        bot.answer_callback_query(callback.id)
        proportions(callback.message, 1)
    elif callback.data == 'socseti': # Кнопка "Ссылки на наши профили в соц.сетях" в 1-м уровне меню
        bot.answer_callback_query(callback.id)
        socseti(callback.message)
    elif callback.data == 'tarot': # Таро
        bot.answer_callback_query(callback.id)
        tarot_start(callback.message)
    elif callback.data == 'napravleniya': # Кнопка с выбором направлений из вклдаки "Подробнее о студии и направлениях"
        bot.answer_callback_query(callback.id)
        napravleniya(callback.message)
    elif callback.data == 'napravleniya_2': # Кнопка с выбором направлений из вклдаки "Выездные мастер-классы"
        bot.answer_callback_query(callback.id)
        napravleniya_2(callback.message)
    elif callback.data == 'studia': # Кнопка "Подробнее о студии и направлениях" в 1-м уровне меню
        bot.answer_callback_query(callback.id)
        studia(callback.message)
    elif callback.data == 'Smola': # Кнопка "Эпоксидная смола" в направлениях студии
        bot.answer_callback_query(callback.id)
        Smola(callback.message)
    elif callback.data == 'Gips': # Кнопка "Гипс" в направлениях студии
        bot.answer_callback_query(callback.id)
        Gips(callback.message)
    elif callback.data == 'Gips_2': # Кнопка "Гипс" в направлениях выездных МК
        bot.answer_callback_query(callback.id)
        Gips_2(callback.message)
    elif callback.data == 'Sketching': # Кнопка "Скетчинг" в направлениях студии
        bot.answer_callback_query(callback.id)
        Sketching(callback.message)
    elif callback.data == 'TieDye': # Кнопка "Тай-Дай" в направлениях студии
        bot.answer_callback_query(callback.id)
        TieDye(callback.message)
    elif callback.data == 'TieDye_2': # Кнопка "Тай-Дай" в направлениях выездных МК
        bot.answer_callback_query(callback.id)
        TieDye_2(callback.message)
    elif callback.data == 'CustomCloth': # Кнопка "Роспись одежды" в направлениях студии
        bot.answer_callback_query(callback.id)
        CustomCloth(callback.message)
    elif callback.data == 'Svechi': # Кнопка "Свечеварение" в направлениях студии
        bot.answer_callback_query(callback.id)
        Svechi(callback.message)
    elif callback.data == 'Svechi_2': # Кнопка "Свечеварение" в направлениях выездных МК
        bot.answer_callback_query(callback.id)
        Svechi_2(callback.message)
    elif callback.data == 'shop': # Кнопка "Магазин" в 1-м уровне меню
        bot.answer_callback_query(callback.id)
        shop(callback.message)
    elif callback.data == 'catalog_main': # Кнопка "Каталог" во вкладке магазина
        bot.answer_callback_query(callback.id)
        catalog_main(callback.message)
    elif callback.data == 'catalog_1': # Страница 1 в каталоге
        bot.answer_callback_query(callback.id)
        catalog_1(callback.message)
    elif callback.data == 'catalog_2': # Страница 2 в каталоге
        bot.answer_callback_query(callback.id)
        catalog_2(callback.message)
    elif callback.data == 'catalog_3': # Страница 3 в каталоге
        bot.answer_callback_query(callback.id)
        catalog_3(callback.message)
    elif callback.data == 'catalog_4': # Страница 4 в каталоге
        bot.answer_callback_query(callback.id)
        catalog_4(callback.message)
    elif callback.data == 'catalog_5': # Страница 5 в каталоге
        bot.answer_callback_query(callback.id)
        catalog_5(callback.message)
    elif callback.data == 'catalog_6': # Страница 6 в каталоге
        bot.answer_callback_query(callback.id)
        catalog_6(callback.message)
    elif callback.data == 'catalog_7': # Страница 7 в каталоге
        bot.answer_callback_query(callback.id)
        catalog_7(callback.message)
    elif callback.data == 'oplata': # Кнопка "Оплата" в меню Магазина
        bot.answer_callback_query(callback.id)
        oplata(callback.message)
    elif callback.data == 'dostavka': # Кнопка "О доставке" в меню Магазина
        bot.answer_callback_query(callback.id)
        dostavka(callback.message)
    elif callback.data == 'zakaz': # Кнопка "Как заказать" в меню Магазина
        bot.answer_callback_query(callback.id)
        zakaz(callback.message)
    elif callback.data == 'viezd': # Кнопка "Выездные мастер-классы" в 1-м уровне меню
        bot.answer_callback_query(callback.id)
        viezd(callback.message)
    elif callback.data == "send_broadcast_photo": # Отправка рассылки фото после подтверждения
        bot.answer_callback_query(callback.id)
        send_broadcast_photo(callback.message)
    elif callback.data == "send_broadcast_text": # Отправка рассылки текст после подтверждения
        bot.answer_callback_query(callback.id)
        send_broadcast_text(callback.message)
    elif callback.data == "cancel": # Отмена рассылки
        bot.answer_callback_query(callback.id)
        cancel_broadcast(callback.message)


bot.infinity_polling() # Постоянная работа бота
