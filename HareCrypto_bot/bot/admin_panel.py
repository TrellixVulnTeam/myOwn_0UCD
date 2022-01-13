# IDEA: сделать также изменение фразы для команды /start

import sqlite3
import shelve

import pendulum
from aiogram.utils.json import json

import files
from extensions import Event
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity

import config
from defs import get_admin_list, log, user_logger, new_admin, get_state, del_id, get_moder_list, new_moder, mailing, \
    chat_logger, change_settings, change_phrase

creation_event = Event()
edition_event = Event()


async def first_launch(bot, chat_id):
    try:
        with open(files.working_log, encoding='utf-8') as f:
            return False
    except:
        await admin_panel(bot, chat_id, first__launch=True)
        return True


async def admin_panel(bot, message, first__launch=False):
    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.row('События')
    user_markup.row('Списки')
    user_markup.row('Настройки бота')
    if first__launch:
        await bot.send_message(message.chat.id, """Добро пожаловать в админ панель. Это первый запуск бота.\n 
        В следующий раз чтобы войти в админ панель введите команду '/adm'.
        """, parse_mode='MarkDown', reply_markup=user_markup)
        new_admin(message.chat.id, message.chat.username)
        await log(f'First launch admin panel of bot by admin {message.chat.id}')
    else:
        await bot.send_message(message.chat.id, """ Добро пожаловать в админ панель.
        """, parse_mode='MarkDown', reply_markup=user_markup)

        await log(f'Launch admin panel of bot by admin {message.chat.id}')


async def in_admin_panel(bot, settings, message):
    """
    Функция состоит из двух частей: в первой части обработка текстовых команд,
    во второй - обработка состояний переписки.

    При добавлении события учитываются состояния 1, 2, 3, 4:
    1 - выбор категории события,
    2 - ввод названия,
    3 - ввод описания,
    4 - ввод даты в формате

    При удалении события - состояние 6:
    6 - выбор события для удаления из существующих

    При редактировании события - состояния 7, 8, 9, 10, 11, 12:
    7 - выбор события для редактирования из существующих,
    8 - состояние изменения события,
    9 - изменение названия события,
    10 - изменение описания события,
    11 - изменение даты события в формате,
    11 - изменение типа события из предложенных категорий

    При работе со списком админов - состояния 21, 22:
    21 - добавление нового админа, где нужно ввести его id
    22 - удаление админа из списка

    При работе со списком модераторов - состояния 31, 32:
    31 - добавление нового модератора (может сделать только один из админов)
    32 - удаление модератора из списка (может сделать только один из админов)

    При настройке бота - состояние 41:
    41 - изменений выводной фразы по команде /help


    :param bot: Bot from aiogram
    :param settings: object class: Settings from hare_bot.py
    :param message: types.Message from aiogram
    :return: None
    """
    if message.chat.id in [message.chat.id for item in get_admin_list() if message.chat.id in item]:
        if message.text == 'Вернуться в главное меню' or message.text == '/adm':
            if get_state(message.chat.id) is True:
                with shelve.open(files.state_bd) as bd: del bd[str(message.chat.id)]
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('События')
            user_markup.row('Списки')
            user_markup.row('Настройки бота')

            await bot.send_message(message.chat.id, 'Вы вошли в админку бота!\nЧтобы выйти из неё, нажмите /start',
                                   reply_markup=user_markup)

        elif message.text == 'События':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Добавить новое событие', 'Удалить событие')
            user_markup.row('Редактирование событий')
            user_markup.row('Вернуться в главное меню')

            entity_list = []
            count_string_track = 19
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            events = 'Созданые события:\n\n'
            a = 0
            try:
                cursor.execute("SELECT name, description, date, name_entities, description_entities, "
                               "type_event FROM events;")
            except:
                cursor.execute("CREATE TABLE events (id INT, name TEXT, "
                               "description TEXT, date DATETIME, name_entities JSON, description_entities JSON, "
                               "type_event TEXT);")
            else:
                for name, description, date, name_entities, description_entities, type_event in cursor.fetchall():
                    a += 1
                    count_string_track += len(str(a)) + 2
                    name_entities = json.loads(name_entities)
                    description_entities = json.loads(description_entities)

                    if "entities" in name_entities:

                        for entity in name_entities["entities"]:
                            entity_values_list = list(entity.values())

                            if entity["type"] == "text_link":
                                entity = MessageEntity(type=entity_values_list[0],
                                                       offset=count_string_track + entity_values_list[1],
                                                       length=entity_values_list[2], url=entity_values_list[3])
                                entity_list.append(entity)
                            elif (entity["type"] == "mention") or (entity["type"] == "url") or \
                                    (entity["type"] == "hashtag") or (entity["type"] == "cashtag") or \
                                    (entity["type"] == "bot_command") or \
                                    (entity["type"] == "email") or (entity["type"] == "phone_number") or \
                                    (entity["type"] == "bold") or (entity["type"] == "italic") or \
                                    (entity["type"] == "underline") or (entity["type"] == "strikethrough") \
                                    or (entity["type"] == "code"):
                                entity = MessageEntity(type=entity_values_list[0],
                                                       offset=count_string_track + entity_values_list[1],
                                                       length=entity_values_list[2])
                                entity_list.append(entity)

                    count_string_track += len(name) + 3 + len(str(date)) + 7

                    if "entities" in description_entities:

                        for entity in description_entities["entities"]:
                            entity_values_list = list(entity.values())

                            if entity["type"] == "text_link":
                                entity = MessageEntity(type=entity_values_list[0],
                                                       offset=count_string_track + entity_values_list[1],
                                                       length=entity_values_list[2], url=entity_values_list[3])
                                entity_list.append(entity)
                            elif (entity["type"] == "mention") or (entity["type"] == "url") or \
                                    (entity["type"] == "hashtag") or (entity["type"] == "cashtag") or \
                                    (entity["type"] == "bot_command") or \
                                    (entity["type"] == "email") or (entity["type"] == "phone_number") or \
                                    (entity["type"] == "bold") or (entity["type"] == "italic") or \
                                    (entity["type"] == "underline") or (entity["type"] == "strikethrough") \
                                    or (entity["type"] == "code"):
                                entity = MessageEntity(type=entity_values_list[0],
                                                       offset=count_string_track + entity_values_list[1],
                                                       length=entity_values_list[2])
                                entity_list.append(entity)

                    count_string_track += len(description) + 3 + len(type_event) + 1

                    events += str(a) + '. ' + str(name) + ' - ' + str(date) + ' МСК - ' + str(description) + \
                              ' - ' + str(type_event) + '\n'

                    if a % 10 == 0:
                        await bot.send_message(message.chat.id, events, reply_markup=user_markup, entities=entity_list)
                        entity_list = []
                        count_string_track = 19
                        events = 'Созданые события:\n\n'

                con.close()

            if a == 0:
                events = "События не созданы!"
            else:
                pass

            await bot.send_message(message.chat.id, events, reply_markup=user_markup, entities=entity_list)

        elif message.text == 'Добавить новое событие':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('NFT mints', 'Token sales', 'Testnets')
            user_markup.row('Whitelist / Registration deadline')
            user_markup.row('Trend token')
            user_markup.row('Вернуться в главное меню')

            await bot.send_message(message.chat.id, 'Выберите тип события', reply_markup=user_markup)
            with shelve.open(files.state_bd) as bd:
                bd[str(message.chat.id)] = 1

        elif message.text == 'Редактирование событий':
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute("SELECT name, date FROM events;")
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for name, date in cursor.fetchall():
                a += 1
                user_markup.row(str(name))
            if a == 0:
                await bot.send_message(message.chat.id, 'Никаких событий ещё не создано!', reply_markup=user_markup)
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Какое событие хотите редактировать?',
                                       parse_mode='Markdown', reply_markup=user_markup)
                with shelve.open(files.state_bd) as bd:
                    bd[str(message.chat.id)] = 7
            con.close()

        elif message.text == 'Изменить название':
            if get_state(message.chat.id) is True:
                with shelve.open(files.state_bd) as bd:
                    state_num = bd[str(message.chat.id)]
                if state_num == 8:
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    a = 0
                    cursor.execute("SELECT name FROM events WHERE name = " + "'" + edition_event.name + "';")
                    for i in cursor.fetchall(): a += 1
                    if a == 0:
                        await bot.send_message(message.chat.id, 'События с таким названием нет!\nВыберите заново!')
                    else:
                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(message.chat.id, 'Введите новое название события',
                                               parse_mode='Markdown', reply_markup=user_markup)
                        with shelve.open(files.state_bd) as bd:
                            bd[str(message.chat.id)] = 9
                    con.close()

        elif message.text == 'Изменить описание':
            if get_state(message.chat.id) is True:
                with shelve.open(files.state_bd) as bd:
                    state_num = bd[str(message.chat.id)]
                if state_num == 8:
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    a = 0
                    cursor.execute("SELECT description FROM events WHERE name = " + "'" + edition_event.name + "';")
                    for i in cursor.fetchall(): a += 1
                    if a == 0:
                        await bot.send_message(message.chat.id, 'События с таким описанием нет!\nВыберите заново!')
                    else:
                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(message.chat.id, 'Введите новое описание события',
                                               parse_mode='Markdown', reply_markup=user_markup)
                        with shelve.open(files.state_bd) as bd:
                            bd[str(message.chat.id)] = 10
                    con.close()

        elif message.text == 'Изменить дату':
            if get_state(message.chat.id) is True:
                with shelve.open(files.state_bd) as bd:
                    state_num = bd[str(message.chat.id)]
                if state_num == 8:
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    a = 0
                    cursor.execute("SELECT date FROM events WHERE name = " + "'" + edition_event.name + "';")
                    for i in cursor.fetchall(): a += 1
                    if a == 0:
                        await bot.send_message(message.chat.id, 'События с такой датой нет!\nВыберите заново!')
                    else:
                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(message.chat.id, 'Введите новую дату события '
                                                                '(в формате ДД.ММ.ГГГГ ЧЧ:ММ или TBA)',
                                               parse_mode='Markdown', reply_markup=user_markup)
                        with shelve.open(files.state_bd) as bd:
                            bd[str(message.chat.id)] = 11
                    con.close()

        elif message.text == 'Изменить тип':
            if get_state(message.chat.id) is True:
                with shelve.open(files.state_bd) as bd:
                    state_num = bd[str(message.chat.id)]
                if state_num == 8:
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    a = 0
                    cursor.execute("SELECT type_event FROM events WHERE name = " + "'" + edition_event.name + "';")
                    for i in cursor.fetchall(): a += 1
                    if a == 0:
                        await bot.send_message(message.chat.id, 'События с таким типом нет!\nВыберите заново!')
                    else:
                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('NFT mints', 'Token sales', 'Testnets')
                        user_markup.row('Whitelist / Registration deadline')
                        user_markup.row('Trend token')
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(message.chat.id, 'Выберите новый тип события',
                                               parse_mode='Markdown', reply_markup=user_markup)
                        with shelve.open(files.state_bd) as bd:
                            bd[str(message.chat.id)] = 12
                    con.close()

        elif message.text == 'Удалить событие':
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute("SELECT name, date FROM events;")
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for name, date in cursor.fetchall():
                a += 1
                user_markup.row(str(name))
            if a == 0:
                await bot.send_message(message.chat.id, 'Никаких событий ещё не создано!', reply_markup=user_markup)
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Какое событие нужно удалить?',
                                       parse_mode='Markdown', reply_markup=user_markup)
                with shelve.open(files.state_bd) as bd:
                    bd[str(message.chat.id)] = 6
            con.close()

        elif message.text == 'Списки':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Список пользователей', 'Список групп')
            user_markup.row('Список модераторов', 'Список админов')
            user_markup.row('Вернуться в главное меню')

            await bot.send_message(message.chat.id, "Выберите список для отображения", reply_markup=user_markup)

        elif message.text == 'Список админов':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Добавить нового админа', 'Удалить админа')
            user_markup.row('Вернуться в главное меню')

            admins = "Список админов:\n\n"
            if len(get_admin_list()) != 0:
                for admin in get_admin_list():
                    admins += f"<a href='tg://user?id={admin[0]}'>{admin[0]}</a> - @{admin[1]}\n"

                await bot.send_message(message.chat.id, admins, reply_markup=user_markup, parse_mode="HTML")
            else:
                await bot.send_message(message.chat.id, "Админов еще нет", reply_markup=user_markup)

        elif message.text == 'Добавить нового админа':
            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton('Отменить и вернуться в главное меню админки',
                                         callback_data='Вернуться в главное меню админки'))
            await bot.send_message(message.chat.id, 'Введите id нового админа', reply_markup=key)
            with shelve.open(files.state_bd) as bd:
                bd[str(message.chat.id)] = 21

        elif message.text == 'Удалить админа':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for admin in get_admin_list():
                a += 1
                if int(admin[0]) != config.admin_id: user_markup.row(f"{str(admin[0])} - {admin[1]}")
            if a == 1:
                await bot.send_message(message.chat.id, 'Вы ещё не добавляли админов!')
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Выбери id админа, которого нужно удалить',
                                       reply_markup=user_markup)
                with shelve.open(files.state_bd) as bd:
                    bd[str(message.chat.id)] = 22

        elif message.text == 'Список модераторов':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Добавить нового модератора', 'Удалить модератора')
            user_markup.row('Вернуться в главное меню')

            moders = "Список модераторов:\n\n"
            if len(get_moder_list()) != 0:
                for moder in get_moder_list():
                    moders += f"<a href='tg://user?id={moder[0]}'>{moder[0]}</a> - @{moder[1]}\n"
                await bot.send_message(message.chat.id, moders, reply_markup=user_markup, parse_mode="HTML")
            else:
                await bot.send_message(message.chat.id, "Модераторов еще нет", reply_markup=user_markup)

        elif message.text == 'Добавить нового модератора':
            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton('Отменить и вернуться в главное меню админки',
                                         callback_data='Вернуться в главное меню админки'))
            await bot.send_message(message.chat.id, 'Введите id нового модератора', reply_markup=key)
            with shelve.open(files.state_bd) as bd:
                bd[str(message.chat.id)] = 31

        elif message.text == 'Удалить модератора':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for moder in get_moder_list():
                a += 1
                user_markup.row(f'{str(moder[0])} - {moder[1]}')
            if a == 0:
                await bot.send_message(message.chat.id, 'Вы ещё не добавляли модераторов!')
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Выбери id модератора, которого нужно удалить',
                                       reply_markup=user_markup)
                with shelve.open(files.state_bd) as bd:
                    bd[str(message.chat.id)] = 32

        elif message.text == 'Список пользователей':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Вернуться в главное меню')
            get_list = 0
            a = 0
            users = "Список пользователей:\n\n"
            for user in user_logger(get_list):
                a += 1
                users += f"{a}.<a href='tg://user?id={user[0]}'>{user[0]}</a> - {user[1]}\n"

                if a % 50 == 0:
                    await bot.send_message(message.chat.id, users, reply_markup=user_markup, parse_mode="HTML")
                    users = "Список пользователей:\n\n"

            await bot.send_message(message.chat.id, users, reply_markup=user_markup, parse_mode="HTML")

        elif message.text == 'Список групп':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Вернуться в главное меню')
            a = 0
            chats = "Список групп:\n\n"
            if len(chat_logger(0)) != 0:
                for chat in chat_logger(0):
                    a += 1

                    chats += f"{a}.{chat[0]} - {str(chat[1])} - {str(chat[2])}\n"

                    if a % 50 == 0:
                        await bot.send_message(message.chat.id, chats, reply_markup=user_markup, parse_mode="HTML")
                        chats = "Список групп:\n\n"

                await bot.send_message(message.chat.id, chats, reply_markup=user_markup, parse_mode="HTML")
            else:
                await bot.send_message(message.chat.id, "Групп еще нет", reply_markup=user_markup)

        elif message.text == 'Скачать лог файл':
            working_log = open(files.working_log, 'rb')
            await bot.send_document(message.chat.id, working_log)
            working_log.close()

        elif message.text == 'Настройки бота':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)

            new_event_setting = "Включено" if settings.new_event_setting else "Выключено"
            hot_event_setting = "Включено" if settings.hot_event_setting else "Выключено"

            user_markup.row(f'Уведомления о новом событии:{new_event_setting}')
            user_markup.row(f'Уведомления о приближающемся событии:{hot_event_setting}')
            user_markup.row('Изменить выводное сообщение команды /help')
            user_markup.row('Скачать лог файл')
            user_markup.row('Вернуться в главное меню')

            await bot.send_message(message.chat.id, "Вы вошли в настройки бота", reply_markup=user_markup,
                                   parse_mode="HTML")

        elif message.text == 'Уведомления о новом событии:Выключено':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)

            settings.new_event_setting = True
            change_settings(settings)

            new_event_setting = "Включено" if settings.new_event_setting else "Выключено"
            hot_event_setting = "Включено" if settings.hot_event_setting else "Выключено"

            user_markup.row(f'Уведомления о новом событии:{new_event_setting}')
            user_markup.row(f'Уведомления о приближающемся событии:{hot_event_setting}')
            user_markup.row('Изменить выводное сообщение команды /help')
            user_markup.row('Скачать лог файл')
            user_markup.row('Вернуться в главное меню')

            await bot.send_message(message.chat.id, "Уведомления о новом событии включены", reply_markup=user_markup)

        elif message.text == 'Уведомления о новом событии:Включено':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)

            settings.new_event_setting = False
            change_settings(settings)

            new_event_setting = "Включено" if settings.new_event_setting else "Выключено"
            hot_event_setting = "Включено" if settings.hot_event_setting else "Выключено"

            user_markup.row(f'Уведомления о новом событии:{new_event_setting}')
            user_markup.row(f'Уведомления о приближающемся событии:{hot_event_setting}')
            user_markup.row('Изменить выводное сообщение команды /help')
            user_markup.row('Скачать лог файл')
            user_markup.row('Вернуться в главное меню')

            await bot.send_message(message.chat.id, "Уведомления о новом событии выключены", reply_markup=user_markup)

        elif message.text == 'Уведомления о приближающемся событии:Выключено':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)

            settings.hot_event_setting = True
            change_settings(settings)

            new_event_setting = "Включено" if settings.new_event_setting else "Выключено"
            hot_event_setting = "Включено" if settings.hot_event_setting else "Выключено"

            user_markup.row(f'Уведомления о новом событии:{new_event_setting}')
            user_markup.row(f'Уведомления о приближающемся событии:{hot_event_setting}')
            user_markup.row('Изменить выводное сообщение команды /help')
            user_markup.row('Скачать лог файл')
            user_markup.row('Вернуться в главное меню')

            await bot.send_message(message.chat.id, "Уведомления о приближающемся событии включены",
                                   reply_markup=user_markup)

        elif message.text == 'Уведомления о приближающемся событии:Включено':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)

            settings.hot_event_setting = False
            change_settings(settings)

            new_event_setting = "Включено" if settings.new_event_setting else "Выключено"
            hot_event_setting = "Включено" if settings.hot_event_setting else "Выключено"

            user_markup.row(f'Уведомления о новом событии:{new_event_setting}')
            user_markup.row(f'Уведомления о приближающемся событии:{hot_event_setting}')
            user_markup.row('Изменить выводное сообщение команды /help')
            user_markup.row('Скачать лог файл')
            user_markup.row('Вернуться в главное меню')

            await bot.send_message(message.chat.id, "Уведомления о приближающемся событии выключены",
                                   reply_markup=user_markup)

        elif message.text == 'Изменить выводное сообщение команды /help':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Вернуться в главное меню')

            help_text = settings.help_text

            await bot.send_message(message.chat.id, "На данный момент сообщение help такое:")
            await bot.send_message(message.chat.id, help_text, reply_markup=user_markup)
            await bot.send_message(message.chat.id, "Введите новое сообщение для команды help:")

            with shelve.open(files.state_bd) as bd:
                bd[str(message.chat.id)] = 41

        elif get_state(message.chat.id) is True:
            with shelve.open(files.state_bd) as bd:
                state_num = bd[str(message.chat.id)]

            if state_num == 1:
                if message.text == 'NFT mints' or message.text == 'Token sales' or message.text == 'Trend token' \
                        or message.text == 'Whitelist / Registration deadline' or message.text == 'Testnets':
                    creation_event.type_event = message.text

                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, f'Тип события {creation_event.type_event}',
                                           reply_markup=user_markup)

                    key = InlineKeyboardMarkup()
                    key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                                 callback_data='Вернуться в главное меню админки'))
                    await bot.send_message(message.chat.id, 'Введите название события:', reply_markup=key)
                    with shelve.open(files.state_bd) as bd:
                        bd[str(message.chat.id)] = 2
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('NFT mints', 'Token sales', 'Testnets')
                    user_markup.row('Whitelist / Registration deadline')
                    user_markup.row('Trend token')
                    user_markup.row('Вернуться в главное меню')

                    await bot.send_message(message.chat.id, 'Выберите тип события из предложенного списка!',
                                           reply_markup=user_markup)

            elif state_num == 2:
                creation_event.name = message.text
                creation_event.name_entities = message

                key = InlineKeyboardMarkup()
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                             callback_data='Вернуться в главное меню админки'))
                await bot.send_message(message.chat.id, f'Введите описание для {message.text}', reply_markup=key)
                with shelve.open(files.state_bd) as bd:
                    bd[str(message.chat.id)] = 3

            elif state_num == 3:
                creation_event.description = message.text
                creation_event.description_entities = message

                if creation_event.type_event == 'Trend token':
                    creation_event.date = 'TBA'
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    cursor.execute("INSERT INTO events (name, description, date, name_entities, " +
                                   "description_entities, type_event) VALUES " + "('" + str(creation_event.name) +
                                   "', '" + str(creation_event.description) + "', '" +
                                   str(creation_event.date) + "', '" + str(creation_event.name_entities) + "', '" +
                                   str(creation_event.description_entities) + "', '" +
                                   str(creation_event.type_event) + "')")
                    con.commit()
                    con.close()

                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Добавить новое событие', 'Удалить событие')
                    user_markup.row('Редактирование событий')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Событие создано!', reply_markup=user_markup)
                    await log(f'Event {creation_event.name} is created by {message.chat.id}')
                    if settings.new_event_setting:
                        await mailing(bot, creation_event)
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(message.chat.id)]
                else:
                    key = InlineKeyboardMarkup()
                    key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                                 callback_data='Вернуться в главное меню админки'))
                    await bot.send_message(message.chat.id,
                                           'Введите дату события (в формате ДД.ММ.ГГГГ ЧЧ:ММ или TBA):',
                                           reply_markup=key)
                    with shelve.open(files.state_bd) as bd:
                        bd[str(message.chat.id)] = 4

            elif state_num == 4:
                creation_event.date = message.text
                if creation_event.date == 'TBA':
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    cursor.execute("INSERT INTO events (name, description, date, name_entities, " +
                                   "description_entities, type_event) VALUES " + "('" + str(creation_event.name) +
                                   "', '" + str(creation_event.description) + "', '" +
                                   str(creation_event.date) + "', '" + str(creation_event.name_entities) + "', '" +
                                   str(creation_event.description_entities) + "', '" +
                                   str(creation_event.type_event) + "')")
                    con.commit()
                    con.close()

                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Добавить новое событие', 'Удалить событие')
                    user_markup.row('Редактирование событий')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Событие создано!', reply_markup=user_markup)
                    await log(f'Event {creation_event.name} is created by {message.chat.id}')
                    if settings.new_event_setting:
                        await mailing(bot, creation_event)
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(message.chat.id)]
                else:
                    try:
                        pendulum.from_format(message.text, "DD.MM.YYYY HH:mm", tz=settings.time_zone)
                    except:
                        await bot.send_message(message.chat.id, 'Вы ввели дату в неправильном формате!')
                        key = InlineKeyboardMarkup()
                        key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                                     callback_data='Вернуться в главное меню админки'))
                        await bot.send_message(message.chat.id,
                                               'Введите дату события (в формате ДД.ММ.ГГГГ ЧЧ:ММ или TBA):',
                                               reply_markup=key)
                    else:
                        con = sqlite3.connect(files.main_db)
                        cursor = con.cursor()
                        cursor.execute("INSERT INTO events (name, description, date, name_entities, " +
                                       "description_entities, type_event) VALUES " + "('" + str(creation_event.name) +
                                       "', '" + str(creation_event.description) + "', '" +
                                       str(creation_event.date) + "', '" + str(creation_event.name_entities) + "', '" +
                                       str(creation_event.description_entities) + "', '" +
                                       str(creation_event.type_event) + "')")
                        con.commit()
                        con.close()

                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('Добавить новое событие', 'Удалить событие')
                        user_markup.row('Редактирование событий')
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(message.chat.id, 'Событие создано!', reply_markup=user_markup)
                        await log(f'Event {creation_event.name} is created by {message.chat.id}')
                        if settings.new_event_setting:
                            await mailing(bot, creation_event)
                        with shelve.open(files.state_bd) as bd:
                            del bd[str(message.chat.id)]

            elif state_num == 6:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute("SELECT description FROM events WHERE name = " + "'" + message.text + "'")
                for i in cursor.fetchall(): a += 1
                if a == 0:
                    await bot.send_message(message.chat.id,
                                           'Выбранного события не обнаружено! '
                                           'Выберите его, нажав на соотвествующую кнопку')
                else:
                    cursor.execute("DELETE FROM events WHERE name = " + "'" + message.text + "';")
                    con.commit()
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Добавить новое событие', 'Удалить событие')
                    user_markup.row('Редактирование событий')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Событие успешно удалено!', reply_markup=user_markup)
                    await log(f'Event {message.text} is deleted by {message.chat.id}')
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(message.chat.id)]
                con.close()

            elif state_num == 7:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute("SELECT name FROM events WHERE name = " + "'" + message.text + "';")
                for i in cursor.fetchall(): a += 1

                if a == 0:
                    await bot.send_message(message.chat.id, 'События с таким названием нет!\nВыберите заново!')
                else:
                    edition_event.name = message.text
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Изменить название', 'Изменить описание')
                    user_markup.row('Изменить дату', 'Изменить тип')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Теперь выберите, что хотите изменить',
                                           reply_markup=user_markup)
                    with shelve.open(files.state_bd) as bd:
                        bd[str(message.chat.id)] = 8
                con.close()

            elif state_num == 9:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute("UPDATE events SET name = '" + message.text + "', name_entities = '" +
                               str(message) + "' " + "WHERE name = '" + edition_event.name + "';")
                con.commit()
                con.close()

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить название', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить тип')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Название события успешно изменено!', reply_markup=user_markup)
                await log(f'Name event {edition_event.name} is changed by {message.chat.id}')
                with shelve.open(files.state_bd) as bd:
                    bd[str(message.chat.id)] = 8

            elif state_num == 10:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute("UPDATE events SET description = '" + message.text +
                               "', description_entities = '" + str(message) + "' " +
                               "WHERE name = '" + edition_event.name + "';")
                con.commit()
                con.close()

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить название', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить тип')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Описание события успешно изменено!', reply_markup=user_markup)
                await log(f'Description event {edition_event.name} is changed by {message.chat.id}')
                with shelve.open(files.state_bd) as bd:
                    bd[str(message.chat.id)] = 8

            elif state_num == 11:
                if message.text == 'TBA':
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    cursor.execute("UPDATE events SET date = '" + message.text + "' WHERE name = '" +
                                   edition_event.name + "';")
                    con.commit()
                    con.close()

                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Изменить название', 'Изменить описание')
                    user_markup.row('Изменить дату', 'Изменить тип')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Дата события успешно изменена!', reply_markup=user_markup)
                    await log(f'Date event {edition_event.name} is changed by {message.chat.id}')
                    with shelve.open(files.state_bd) as bd:
                        bd[str(message.chat.id)] = 8
                else:
                    try:
                        pendulum.from_format(message.text, "DD.MM.YYYY HH:mm", tz=settings.time_zone)
                    except:
                        await bot.send_message(message.chat.id, 'Вы ввели дату в неправильном формате!')
                        key = InlineKeyboardMarkup()
                        key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                                     callback_data='Вернуться в главное меню админки'))
                        await bot.send_message(message.chat.id,
                                               'Введите дату события (в формате ДД.ММ.ГГГГ ЧЧ:ММ или TBA):',
                                               reply_markup=key)
                    else:
                        con = sqlite3.connect(files.main_db)
                        cursor = con.cursor()
                        cursor.execute("UPDATE events SET date = '" + message.text + "' WHERE name = '" +
                                       edition_event.name + "';")
                        con.commit()
                        con.close()

                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('Изменить название', 'Изменить описание')
                        user_markup.row('Изменить дату', 'Изменить тип')
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(message.chat.id, 'Дата события успешно изменена!',
                                               reply_markup=user_markup)
                        await log(f'Date event {edition_event.name} is changed by {message.chat.id}')
                        with shelve.open(files.state_bd) as bd:
                            bd[str(message.chat.id)] = 8

            elif state_num == 12:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute("UPDATE events SET type_event = '" + message.text + "' " +
                               "WHERE name = '" + edition_event.name + "';")
                con.commit()
                con.close()

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить название', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить тип')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Тип события успешно изменено!', reply_markup=user_markup)
                await log(f'Type event {edition_event.name} is changed by {message.chat.id}')
                with shelve.open(files.state_bd) as bd:
                    bd[str(message.chat.id)] = 8

            elif state_num == 21:
                if message.forward_from:
                    new_admin(message.forward_from.id, message.forward_from.username)
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Добавить нового админа', 'Удалить админа')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Новый админ успешно добавлен', reply_markup=user_markup)
                    await log(f'New admin {message.forward_from.username} is added by {message.chat.id}')
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(message.chat.id)]
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Добавить нового админа', 'Удалить админа')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Новый админ не был добавлен\n'
                                                            'Перешлите сообщение пользователя в бота, '
                                                            'чтобы добавить сделать его админом.',
                                           reply_markup=user_markup)

            elif state_num == 22:
                admin = str(message.text)
                admin = admin.split(' - ')
                if int(admin[0]) in [int(admin[0]) for item in get_admin_list() if int(admin[0]) in item]:
                    try:
                        del_id('admins', int(admin[0]))
                    except:
                        print('cant delete admin id')
                    else:
                        await bot.send_message(message.chat.id, 'Админ успешно удалён из списка')
                        await log(f'The admin {message.text} is removed by {message.chat.id}')
                        with shelve.open(files.state_bd) as bd:
                            del bd[str(message.chat.id)]
                else:
                    await bot.send_message(message.chat.id, 'Такого id в списках админов не обнаружено! '
                                                            'Выберите правильный id!')
                    with shelve.open(files.state_bd) as bd:
                        bd[str(message.chat.id)] = 22

            elif state_num == 31:
                if message.forward_from:
                    new_moder(message.forward_from.id, message.forward_from.username)
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Добавить нового модератора', 'Удалить модератора')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Новый модератор успешно добавлен', reply_markup=user_markup)
                    await log(f'New moder {message.text} is added by {message.chat.id}')
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(message.chat.id)]
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Добавить нового модератора', 'Удалить модератора')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Новый модератор не был добавлен\n'
                                                            'Перешлите сообщение пользователя в бота, '
                                                            'чтобы добавить сделать его модератором.',
                                           reply_markup=user_markup)

            elif state_num == 32:
                moder = str(message.text)
                moder = moder.split(' - ')
                if int(moder[0]) in [int(moder[0]) for item in get_moder_list() if int(moder[0]) in item]:
                    try:
                        del_id('moders', int(moder[0]))
                    except:
                        print('cant delete moder id')
                    else:
                        await bot.send_message(message.chat.id, 'Модератор успешно удалён из списка')
                        await log(f'The moder {message.text} is removed by {message.chat.id}')
                        with shelve.open(files.state_bd) as bd:
                            del bd[str(message.chat.id)]
                else:
                    await bot.send_message(message.chat.id, 'Такого id в списках модеров не обнаружено! '
                                                            'Выберите правильный id!')
                    with shelve.open(files.state_bd) as bd:
                        bd[str(message.chat.id)] = 32

            elif state_num == 41:
                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Вернуться в главное меню')

                settings.help_text = message.text
                change_phrase(settings.help_text, files.help_text)

                await bot.send_message(message.chat.id, 'Добавлено новое сообщение помощи', reply_markup=user_markup)


async def admin_inline(bot, callback_data, chat_id, message_id):
    if callback_data == 'Вернуться в главное меню админки':
        if get_state(chat_id) is True:
            with shelve.open(files.state_bd) as bd: del bd[str(chat_id)]
        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('События')
        user_markup.row('Списки')
        user_markup.row('Настройки бота')

        await bot.delete_message(chat_id, message_id)  # удаляется старое сообщение
        await bot.send_message(chat_id, 'Вы вошли в админку бота!\nЧтобы выйти из неё, нажмите /start',
                               reply_markup=user_markup)
