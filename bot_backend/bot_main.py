from bot_funcs.admin_only import admin, proportions, send_user_count
from bot_funcs.broadcast import start_broadcast
from bot_funcs.shop_delivery import shop, catalog, ordering, payment, shipment
from bot_funcs.studio_and_directions import (
    candles_info, custom_cloth, gips_info, epoxy,
    sketching, tie_dye_info, directions, studio, offsite_workshops
)
from bot_funcs.user_funcs import (
    clean, delete_user_messages, soc_profiles, start_help, tarot_start, chepuha
)
from bot_parts.constants import BOT
from bot_parts.wrappers import check_bd_chat_id, check_is_admin, sub_check
from sql_orm import (
    record_message_id_to_db, get_user_db_id, morning_routine
)

morning_routine()


@BOT.message_handler(commands=['proportions', 'users', 'broadcast'])
@check_bd_chat_id
@check_is_admin
def admin_commands(message):
    if message.text == '/proportions':
        proportions(message)
    elif message.text == '/users':
        send_user_count(message)
    elif message.text == '/broadcast':
        start_broadcast(message)


@BOT.message_handler(commands=['start', 'help', 'clean', 'studio', 'mk',
                               'shop', 'soc_profiles'])
@check_bd_chat_id
@sub_check
def user_commands(message):
    if message.text in ['/start', '/help']:
        start_help(message)
    elif message.text == '/clean':
        clean(message)
    elif message.text == '/studio':
        studio(message)
    elif message.text == '/mk':
        offsite_workshops(message)
    elif message.text == '/shop':
        shop(message)
    elif message.text == '/soc_profiles':
        soc_profiles(message)


@BOT.message_handler(content_types=['text', 'photo'])
@check_bd_chat_id
@sub_check
def message_input(message):
    chat_id = message.chat.id
    user_db_id = get_user_db_id(chat_id)
    flag = False

    record_message_id_to_db(user_db_id, message.message_id)

    if message.text.lower() == 'акуна':
        sent_message = BOT.send_message(
            chat_id,
            text='Матата!'
        )
        flag = True
    elif message.text.lower() == 'матата':
        sent_message = BOT.send_message(
            chat_id,
            text='Акуна!'
        )
        flag = True
    elif 'матата акуна' in message.text.lower():
        sent_message = BOT.send_message(
            chat_id,
            text='\U0001F417 \U0001F439'
        )
        flag = True
    elif 'акуна матата' in message.text.lower():
        with open('easter_eggs/Akuna.jpg', 'rb') as img_akuna:
            sent_message = BOT.send_photo(
                chat_id,
                img_akuna,
                caption=f'<b>Акуна Матата!</b>',
                parse_mode='html'
            )
        flag = True
    elif message.text == '\U0001F346':
        with open('easter_eggs/bolt.png', 'rb') as img_bolt:
            sent_message = BOT.send_photo(
                chat_id,
                img_bolt
            )
        flag = True
    elif 'hello world' in message.text.lower():
        with open('easter_eggs/Hello-World.jpeg', 'rb') as HW_img:
            sent_message = BOT.send_photo(
                chat_id,
                HW_img
            )
        flag = True

    if flag:
        record_message_id_to_db(user_db_id, sent_message.message_id)
    else:
        chepuha(message)


@BOT.callback_query_handler(func=lambda callback: True)
def handle_callback(callback):
    callback_functions = {
        'admin': admin,
        'another_proportion': lambda message: proportions(
            message,
            True
        ),
        'candles': lambda message: candles_info(
            message
        ),
        'candles_offsite': lambda message: candles_info(
            message,
            offsite=True
        ),
        'catalog': lambda message: catalog(
            message
        ),
        'clean': clean,
        'custom_cloth': lambda message: custom_cloth(
            message
        ),
        'delete_message': delete_user_messages,
        'directions': directions,
        'directions_offsite': lambda message: directions(
            message,
            offsite=True
        ),
        'epoxy': lambda message: epoxy(
            message
        ),
        'gips': lambda message: gips_info(
            message
        ),
        'gips_offsite': lambda message: gips_info(
            message,
            offsite=True
        ),
        'help': start_help,
        'offsite_workshops': offsite_workshops,
        'order': ordering,
        'pay': payment,
        'shipment': shipment,
        'shop': shop,
        'sketching': lambda message: sketching(
            message
        ),
        'soc_profiles': soc_profiles,
        'studio': studio,
        'tarot': tarot_start,
        'tie_dye': lambda message: tie_dye_info(
            message
        ),
        'tie_dye_offsite': lambda message: tie_dye_info(
            message,
            offsite=True
        )
    }

    BOT.answer_callback_query(callback.id)
    callback_functions[callback.data](callback.message)


BOT.infinity_polling()
