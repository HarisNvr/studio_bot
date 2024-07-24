#  Бот-помощник для студии Eleni_Workshop 

## Ссылка на бота: https://t.me/Eleni_WS_Bot

## Что умеет?

**Перенаправлять на соц.сети, рассказывать о направлениях студии, информировать о ценах и раскладывать Таро.**

### Технологии:

Python, pyTelegramBotAPI, SQLite3

### Развернуть проект на удаленном сервере:

- Клонировать репозиторий и перейти в него:
```
git clone https://github.com/HarisNvr/EleniWS_BOT.git
cd studio_bot
```
- Настраиваем переменные окружения:
```
sudo nano .env
```
```
# ПРИМЕР ФАЙЛА .env

# Global Vars
ADMIN_IDS=12345678,87654321  # Идентификаторы администраторов через запятую

# BOT_TOKENS
BOT=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ-abcdefghijklmnopqrstuvwxyz  # Токен вашего бота от BotFather

# Soc_Profiles
INSTAGRAM=https://instagram.com/yourprofile  # Ссылка на Instagram профиль
VK=https://vk.com/yourprofile  # Ссылка на VK профиль
TG_DM=https://t.me/yourusername  # Ссылка для прямого сообщения в Telegram
TG_CHANNEL=https://t.me/yourchannel  # Ссылка на Telegram канал
WA=https://wa.me/1234567890  # Ссылка для общения в WhatsApp
YA_DISK=https://disk.yandex.ru/yourdisk  # Ссылка на Яндекс.Диск
SUPPORT=https://support.yoursite.com  # Ссылка на страницу поддержки

# Some_stuff
ORG_NAME=ACME_CORP # Название вашей организации

```
- Установим и создадим виртуально окружение, установим зависимости:
```
python -m pip install --upgrade pip 
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```
- Пропишем следующую команду для настройки беспрерывной работы нашего бота:
```
nano /lib/systemd/system/НазваниеБота.service
```
```
[Unit]
Description=Описание вашего бота
After=network.target

[Service]
EnvironmentFile=/etc/environment
ExecStart=/home/studio_bot/venv/bin/python bot_main.py
ExecReload=/home/studio_bot/venv/bin/python bot_main.py
WorkingDirectory=/home/studio_bot/
KillMode=process
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
- Запускаем нашего бота, но уже с беспрерывной работой.
```
sudo systemctl enable НазваниеБота
sudo systemctl start НазваниеБота
```
