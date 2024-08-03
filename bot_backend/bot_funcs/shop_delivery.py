from pathlib import Path
from time import sleep

from telebot import types

from bot_backend.bot_parts.constants import DEL_TIME, BOT
from bot_backend.sql_orm import record_message_id_to_db, get_user_db_id


def relative_path(img_name):
    current_dir = Path(__file__).resolve().parent

    relative_path_to_image = (current_dir / '..' / 'shop_delivery'
                              / f'{img_name}')

    return relative_path_to_image.resolve()


def shop(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_catalog_main = types.InlineKeyboardButton(
        'Каталог \U0001F50D',
        callback_data='catalog'
    )
    btn_shipment = types.InlineKeyboardButton(
        'Доставка \U0001F4E6',
        callback_data='shipment'
    )
    btn_order = types.InlineKeyboardButton(
        'Как заказать \U00002705',
        callback_data='order'
    )
    btn_pay = types.InlineKeyboardButton(
        'Оплата \U0001F4B3',
        callback_data='pay'
    )
    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Связаться с нами \U000026A1',
        url='https://t.me/elenitsa17'
    )
    btn_back = types.InlineKeyboardButton(
        'Назад',
        callback_data='help'
    )
    markup.row(btn_order, btn_catalog_main)
    markup.row(btn_pay, btn_shipment)
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("craft_shop.png")}', 'rb') as shop_img:
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


def catalog(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    relative_path_to_image = (Path(__file__).resolve().parent / '..' /
                              'catalog' / f'CSA_catalog.pdf')

    catalog_path = relative_path_to_image.resolve()

    with open(f'{catalog_path}', 'rb') as catalog_pdf:
        sent_message = BOT.send_document(
            chat_id,
            catalog_pdf,
            caption='Представляем наш каталог в формате PDF!'
                    '\n\n<u>Не является публичной офертой! '
                    '\nАктуальные цены уточняйте у сотрудников студии.</u>'
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
    btn_back = types.InlineKeyboardButton(
        'Назад',
        callback_data='shop'
    )
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("shipment.jpg")}', 'rb') as shipment_img:
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

    btn_back = types.InlineKeyboardButton(
        'Назад',
        callback_data='shop'
    )
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("payment.png")}', 'rb') as pay_img:
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

    btn_back = types.InlineKeyboardButton(
        'Назад',
        callback_data='shop'
    )
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("ordering.jpg")}', 'rb') as img_order:
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
