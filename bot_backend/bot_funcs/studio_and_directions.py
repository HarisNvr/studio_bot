from pathlib import Path
from time import sleep

from telebot import types

from bot_backend.bot_parts.constants import DEL_TIME, BOT
from bot_backend.sql_orm import record_message_id_to_db, get_user_db_id

ADDITIONAL_INFO = (
    '<u>Уточняйте актуальное расписание, '
    f'перечень изделий и наличие '
    f'мест у мастера!</u>'
)
ADDITIONAL_INFO_OFFSITE = (
    '<u>Минимальное количество человек, перечень '
    'изделий и стоимость выезда на локацию проведения '
    'уточняйте у мастера!</u>'
)


def relative_path(img_name):
    current_dir = Path(__file__).resolve().parent

    relative_path_to_image = (current_dir / '..' / 'studio_and_directions'
                              / f'{img_name}')

    return relative_path_to_image.resolve()


def studio(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_dirs = types.InlineKeyboardButton(
        'Подробнее о направлениях',
        callback_data='directions'
    )
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data='help'
    )
    btn_2gis = types.InlineKeyboardButton(
        text='Наша студия в 2GIS',
        url='https://go.2gis.com/8od46'
    )
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

    with open(f'{relative_path("studio_img.png")}', 'rb') as img_studio:
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


def offsite_workshops(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data='help'
    )

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

    with open(f'{relative_path("offsite_workshops_img.png")}',
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


def directions(message, offsite=False):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_epoxy = types.InlineKeyboardButton(
        text='Эпоксидная смола',
        callback_data='epoxy'
    )
    btn_gips = types.InlineKeyboardButton(
        text='Гипс',
        callback_data='gips'
        if not offsite
        else 'gips_offsite'
    )
    btn_sketching = types.InlineKeyboardButton(
        text='Скетчинг',
        callback_data='sketching'
    )
    btn_tie_dye = types.InlineKeyboardButton(
        text='Тай-Дай',
        callback_data='tie_dye'
        if not offsite
        else 'tie_dye_offsite'
    )
    btn_custom_cloth = types.InlineKeyboardButton(
        text='Роспись одежды',
        callback_data='custom_cloth'
    )
    btn_candles = types.InlineKeyboardButton(
        text='Свечеварение',
        callback_data='candles'
        if not offsite
        else 'candles_offsite'
    )
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data='studio'
        if not offsite
        else 'offsite_workshops'
    )

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


def epoxy(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data='directions'
    )

    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Записаться на МК \U000026A1',
        url='https://t.me/elenitsa17'
    )

    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("epoxy_img.png")}', 'rb') as img_epoxy:
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
        additional_info = ADDITIONAL_INFO_OFFSITE
        callback_data = 'directions_offsite'
    else:
        btn_text = '\U000026A1 Записаться на МК \U000026A1'
        additional_info = ADDITIONAL_INFO
        callback_data = 'directions'

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data=callback_data
    )
    btn_tg_dm = types.InlineKeyboardButton(
        text=btn_text,
        url='https://t.me/elenitsa17'
    )
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("gips_img.png")}', 'rb') as img_gips:
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
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data='directions'
    )

    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Записаться на МК \U000026A1',
        url='https://t.me/elenitsa17'
    )

    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("sketching_img.png")}', 'rb') as img_sketching:
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
        additional_info = ADDITIONAL_INFO_OFFSITE
        callback_data = 'directions_offsite'
    else:
        btn_text = '\U000026A1 Записаться на МК \U000026A1'
        additional_info = ADDITIONAL_INFO
        callback_data = 'directions'

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data=callback_data
    )
    btn_tg_dm = types.InlineKeyboardButton(
        text=btn_text,
        url='https://t.me/elenitsa17'
    )
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("tie_dye_photo.png")}', 'rb') as img_tie_dye:
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
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data='directions'
    )
    btn_tg_dm = types.InlineKeyboardButton(
        text='\U000026A1 Записаться на МК \U000026A1',
        url='https://t.me/elenitsa17'
    )
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("custom_cloth_img.png")}',
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
        additional_info = ADDITIONAL_INFO_OFFSITE
        callback_data = 'directions_offsite'
    else:
        btn_text = '\U000026A1 Записаться на МК \U000026A1'
        additional_info = ADDITIONAL_INFO
        callback_data = 'directions'

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text='Назад',
        callback_data=callback_data
    )
    btn_tg_dm = types.InlineKeyboardButton(
        text=btn_text,
        url='https://t.me/elenitsa17'
    )
    markup.row(btn_tg_dm)
    markup.row(btn_back)

    BOT.delete_message(chat_id, message.id)
    sleep(DEL_TIME)

    with open(f'{relative_path("candles_photo.png")}', 'rb') as img_candles:
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
