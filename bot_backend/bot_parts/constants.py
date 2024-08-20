from os import getenv

from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()

BOT = TeleBot(getenv('BOT'))
'''
An instance of the Telegram bot initialized with the bot token 
retrieved from environment variables.
'''

INSTAGRAM = getenv('INSTAGRAM')
VK = getenv('VK')
TG_DM = getenv('TG_DM')
TG_CHANNEL = getenv('TG_CHANNEL')
WA = getenv('WA')
YA_DISK = getenv('YA_DISK')
SUPPORT = getenv('SUPPORT')
ORG_NAME = getenv('ORG_NAME')
CHANNEL_ID = int(getenv('CHANNEL_ID'))

DEL_TIME = 0.5
'''
Time interval (in seconds) between deleting an old message and 
sending a new one in the chat.
'''

ADMIN_IDS = []

for ADMIN_ID in (getenv('ADMIN_IDS').split(',')):
    ADMIN_IDS.append(int(ADMIN_ID))
