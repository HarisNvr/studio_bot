from os import getenv

from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()

BOT = TeleBot(getenv('BOT'))

ORG_NAME = getenv('ORG_NAME')

DEL_TIME = 0.5
'''Time between deleting old message and sending a new one'''

ADMIN_IDS = []
