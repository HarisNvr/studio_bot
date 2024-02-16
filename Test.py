import random
import telebot
from telebot import types
import time
import glob
from datetime import datetime
import sqlite3


bot = telebot.TeleBot('6301286378:AAH6rwbVlOIeEtZkKQKqA2RykhD2E-oXq8g')  # @CraftStudioBotJr

del_time = 0.5  # Задержка между сообщениями бота

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



bot.infinity_polling() # Постоянная работа бота