from os import getenv

from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()

BOT = TeleBot(getenv('BOT'))

CHANNEL_ID = int(getenv('CHANNEL_ID'))

ORG_NAME = getenv('ORG_NAME')

DEL_TIME = 0.5
'''Time between deleting old message and sending a new one'''

ADMIN_IDS = []

for ADMIN_ID in (getenv('ADMIN_IDS').split(',')):
    ADMIN_IDS.append(int(ADMIN_ID))
