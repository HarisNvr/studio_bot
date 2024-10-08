#  Бот-помощник для студии Eleni_Workshop 

## Ссылка на бота: https://t.me/Eleni_WS_Bot

## Что умеет?

**Перенаправлять на соц.сети, рассказывать о направлениях студии, информировать о ценах и раскладывать Таро.**

### Используемые технологии

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://pypi.org/project/pyTelegramBotAPI/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-000000?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-7D4698?style=for-the-badge&logo=alembic&logoColor=white)](https://alembic.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

### Развернуть проект на удаленном сервере:

**Предполагается, что на вашей машине уже установлен Docker с плагином Docker-compose!**

Официальный гайд по установке: https://docs.docker.com/engine/install/

- Клонировать репозиторий и перейти в него:
```
git clone https://github.com/HarisNvr/studio_bot.git
cd studio_bot
```
- Настраиваем переменные окружения:
```
sudo nano .env
```
```
# ПРИМЕР ФАЙЛА .env (шаблон в формате txt есть в корне проекта)

#Global Vars
ADMIN_IDS=  # Telegram_ID администраторов

#BOT_TOKENS
BOT=  # Telegram_API_bot_token

#Postgre_Stuff
POSTGRES_USER=  # Имя пользователя для доступа к БД
DB_PASSWORD=  # Пароль для доступа к БД
POSTGRES_DB=  # Имя БД
DB_HOST=postgres  # Имя контейнера с БД
DB_PORT=5432  # Порт контейнера с БД
ENGINE_ECHO=True/False  # Вывод отладки БД в консоль

#Alembic_Stuff
MIGRATE=True/False  # Создание и применение миграций при запуске бота
COMMIT_MESSAGE=Test!  # Название коммита миграций Алембика
TZ=Europe/Moscow  # Тайм-зона, которая будет задана для БД

#Soc_Profiles
INSTAGRAM=https://instagram.com/yourprofile  # Ссылка на Instagram профиль
VK=https://vk.com/yourprofile  # Ссылка на VK профиль
TG_DM=https://t.me/yourusername  # Ссылка для прямого сообщения в Telegram
TG_CHANNEL=https://t.me/yourchannel  # Ссылка на Telegram канал
WA=https://wa.me/1234567890  # Ссылка для общения в WhatsApp
YA_DISK=https://disk.yandex.ru/yourdisk  # Ссылка на Яндекс.Диск
SUPPORT=https://support.yoursite.com  # Ссылка на страницу поддержки

#Some_stuff
ORG_NAME=ACME_CORP  # Название вашей организации
CHANNEL_ID=  # Telegram_ID вашего канала
```
#### Помочь узнать нужные ID может: https://t.me/getmyid_bot
**Бот при запуске умеет сам создавать и применять миграции Alembic. Они будут хранится в томе "alembic_data", сама БД хранится в "postgres_data"**
- При первом запуске необходимо присвоить переменным из раздела "Alembic_Stuff" следующие значения:
```
# .env

...

#Alembic_Stuff
MIGRATE=True
COMMIT_MESSAGE=Initial commit!

...
```
- После успешного применения миграций, необходимо присвоить переменной "MIGRATE" значение False, **иначе бот будет при каждом перезапуске создавать миграции.** После смены значения с True на False бота перезапускать не обязательно!


#### Если вы будете менять модели в ORM, то необходимо создать и применить новые миграции - снова присвоить переменной "MIGRATE" значение True, а переменной "COMMIT_MESSAGE" название вашего коммита. После применения миграций присвойте переменной "MIGRATE" значение False, также как вы это делали во время первой миграции.


- Запускаем Docker композицию:
```
docker compose up -d
# Бот выжидает 2,5 секунды, после подключается к контейнеру с БД.
# После выполнения 'Утренних процедур' Бот выжидает ещё 2,5 секунды и готов к работе!
```
## Команды, вводимые через '/' в чате:
```
start - Запуск бота
help - Главное меню
studio - Подробнее о студии
mk - Выездные МК
shop - Наш магазин
soc_profiles - Наши профили в соц.сетях
clean - Очистить чат
```