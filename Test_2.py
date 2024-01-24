import telebot
from telebot import types

bot = telebot.TeleBot('6301286378:AAH6rwbVlOIeEtZkKQKqA2RykhD2E-oXq8g') #@CraftStudioBotJr

new_text = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = create_menu()
    bot.send_message(message.chat.id, 'Привет!', reply_markup=markup)

def create_menu():
    markup = types.InlineKeyboardMarkup()
    btn_socseti = types.InlineKeyboardButton(text='1', callback_data='button1')
    btn_shop = types.InlineKeyboardButton(text='2', callback_data='button2')
    markup.row(btn_shop, btn_socseti)
    return markup

def button_1(message):
    new_text[message.chat.id] = 'Вы нажали на первую кнопку'
    bot.send_photo(message.chat.id, photo=open('bolt.png', 'rb'))  # Замените 'photo_A.jpg' на путь к вашему фото A

def button_2(message):
    new_text[message.chat.id] = "Вы нажали вторую кнопку"
    bot.send_photo(message.chat.id, photo=open('Akuna.jpg', 'rb'))  # Замените 'photo_B.jpg' на путь к вашему фото B

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    markup = create_menu()
    if call.data == "button1":
        bot.answer_callback_query(call.id)
        button_1(call.message)
    elif call.data == "button2":
        bot.answer_callback_query(call.id)
        button_2(call.message)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_text[call.message.chat.id], reply_markup=markup)

bot.infinity_polling()