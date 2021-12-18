import sqlite3
import shelve
from datetime import datetime

from aiogram.utils.json import json

import files
from defs import get_moder_list, get_state, log, mailing
from extensions import Event
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity

creation_event = Event()
edition_event = Event()


async def moder_panel(bot, chat_id, settings):
    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.row('События')

    await bot.send_message(chat_id, """ Добро пожаловать в панель модератора.""",
                           parse_mode='MarkDown', reply_markup=user_markup)

    await log(f'Launch moder panel of bot by moder {chat_id}')


async def in_moder_panel(bot, chat_id, settings, message):
    """
        Функция состоит из двух частей: в первой части обработка текстовых команда,
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


        :param bot: Bot from aiogram
        :param chat_id: int
        :param settings: object class: Settings from hare_bot.py
        :param message: types.Message from aiogram
        :return: None
        """
    if chat_id in get_moder_list():
        if message.text == 'Вернуться в главное меню' or message.text == '/mod':
            if get_state(chat_id) is True:
                with shelve.open(files.state_bd) as bd: del bd[str(chat_id)]
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('События')

            await bot.send_message(chat_id, 'Вы вошли в панель модератора!\nЧтобы выйти из неё, нажмите /start',
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

                    count_string_track += len(description) + 1

                    events += str(a) + '. ' + str(name) + ' - ' + str(date) + ' МСК - ' + str(description) + '\n'

                    if a % 10 == 0:
                        await bot.send_message(chat_id, events, reply_markup=user_markup, entities=entity_list)
                        entity_list = []
                        count_string_track = 19
                        events = 'Созданые события:\n\n'

                con.close()

            if a == 0:
                events = "События не созданы!"
            else:
                pass

            await bot.send_message(chat_id, events, reply_markup=user_markup, entities=entity_list)

        elif message.text == 'Добавить новое событие':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('NFT mints', 'Token sales', 'Testnets')
            user_markup.row('Whitelist / Registration deadline')
            user_markup.row('Trend token')
            user_markup.row('Вернуться в главное меню')

            await bot.send_message(chat_id, 'Выберите тип события', reply_markup=user_markup)
            with shelve.open(files.state_bd) as bd:
                bd[str(chat_id)] = 1

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
                await bot.send_message(chat_id, 'Никаких событий ещё не создано!', reply_markup=user_markup)
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(chat_id, 'Какое событие хотите редактировать?',
                                       parse_mode='Markdown', reply_markup=user_markup)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 7
            con.close()

        elif message.text == 'Изменить название':
            if get_state(chat_id) is True:
                with shelve.open(files.state_bd) as bd:
                    state_num = bd[str(chat_id)]
                if state_num == 8:
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    a = 0
                    cursor.execute("SELECT name FROM events WHERE name = " + "'" + edition_event.name + "';")
                    for i in cursor.fetchall(): a += 1
                    if a == 0:
                        await bot.send_message(chat_id, 'События с таким названием нет!\nВыберите заново!')
                    else:
                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(chat_id, 'Введите новое название события',
                                               parse_mode='Markdown', reply_markup=user_markup)
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 9
                    con.close()

        elif message.text == 'Изменить описание':
            if get_state(chat_id) is True:
                with shelve.open(files.state_bd) as bd:
                    state_num = bd[str(chat_id)]
                if state_num == 8:
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    a = 0
                    cursor.execute("SELECT description FROM events WHERE name = " + "'" + edition_event.name + "';")
                    for i in cursor.fetchall(): a += 1
                    if a == 0:
                        await bot.send_message(chat_id, 'События с таким описанием нет!\nВыберите заново!')
                    else:
                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(chat_id, 'Введите новое описание события',
                                               parse_mode='Markdown', reply_markup=user_markup)
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 10
                    con.close()

        elif message.text == 'Изменить дату':
            if get_state(chat_id) is True:
                with shelve.open(files.state_bd) as bd:
                    state_num = bd[str(chat_id)]
                if state_num == 8:
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    a = 0
                    cursor.execute("SELECT date FROM events WHERE name = " + "'" + edition_event.name + "';")
                    for i in cursor.fetchall(): a += 1
                    if a == 0:
                        await bot.send_message(chat_id, 'События с такой датой нет!\nВыберите заново!')
                    else:
                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(chat_id, 'Введите новую дату события '
                                                        '(в формате ДД.ММ.ГГГГ ЧЧ:ММ или TBA)',
                                               parse_mode='Markdown', reply_markup=user_markup)
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 11
                    con.close()

        elif message.text == 'Изменить тип':
            if get_state(chat_id) is True:
                with shelve.open(files.state_bd) as bd:
                    state_num = bd[str(chat_id)]
                if state_num == 8:
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    a = 0
                    cursor.execute("SELECT type_event FROM events WHERE name = " + "'" + edition_event.name + "';")
                    for i in cursor.fetchall(): a += 1
                    if a == 0:
                        await bot.send_message(chat_id, 'События с таким типом нет!\nВыберите заново!')
                    else:
                        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                        user_markup.row('NFT mints', 'Token sales', 'Testnets')
                        user_markup.row('Whitelist / Registration deadline')
                        user_markup.row('Trend token')
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(chat_id, 'Выберите новый тип события',
                                               parse_mode='Markdown', reply_markup=user_markup)
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 12
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
                await bot.send_message(chat_id, 'Никаких событий ещё не создано!', reply_markup=user_markup)
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(chat_id, 'Какое событие нужно удалить?',
                                       parse_mode='Markdown', reply_markup=user_markup)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 6
            con.close()

        elif get_state(chat_id) is True:
            with shelve.open(files.state_bd) as bd:
                state_num = bd[str(chat_id)]

            if state_num == 1:
                if message.text == 'NFT mints' or message.text == 'Token sales' or message.text == 'Trend token' \
                        or message.text == 'Whitelist / Registration deadline' or message.text == 'Testnets':
                    creation_event.type_event = message.text

                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(chat_id, f'Тип события {creation_event.type_event}',
                                           reply_markup=user_markup)

                    key = InlineKeyboardMarkup()
                    key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню модпанели',
                                                 callback_data='Вернуться в главное меню модпанели'))
                    await bot.send_message(chat_id, 'Введите название события:', reply_markup=key)
                    with shelve.open(files.state_bd) as bd:
                        bd[str(chat_id)] = 2
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('NFT mints', 'Token sales', 'Testnets')
                    user_markup.row('Whitelist / Registration deadline')
                    user_markup.row('Trend token')
                    user_markup.row('Вернуться в главное меню')

                    await bot.send_message(chat_id, 'Выберите тип события из предложенного списка!',
                                           reply_markup=user_markup)

            elif state_num == 2:
                creation_event.name = message.text
                creation_event.name_entities = message

                key = InlineKeyboardMarkup()
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню модпанели',
                                             callback_data='Вернуться в главное меню модпанели'))
                await bot.send_message(chat_id, f'Введите описание для {message.text}', reply_markup=key)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 3

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
                    await bot.send_message(chat_id, 'Событие создано!', reply_markup=user_markup)
                    await log(f'Event {creation_event.name} is created by {chat_id}')
                    if settings.new_event_setting:
                        await mailing(bot, creation_event)
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(chat_id)]
                else:
                    key = InlineKeyboardMarkup()
                    key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню модпанели',
                                                 callback_data='Вернуться в главное меню модпанели'))
                    await bot.send_message(chat_id,
                                           'Введите дату события (в формате ДД.ММ.ГГГГ ЧЧ:ММ или TBA):',
                                           reply_markup=key)
                    with shelve.open(files.state_bd) as bd:
                        bd[str(chat_id)] = 4

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
                    await bot.send_message(chat_id, 'Событие создано!', reply_markup=user_markup)
                    await log(f'Event {creation_event.name} is created by {chat_id}')
                    if settings.new_event_setting:
                        await mailing(bot, creation_event)
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(chat_id)]
                else:
                    try:
                        datetime.strptime(message.text, "%d.%m.%Y %H:%M")
                    except:
                        await bot.send_message(chat_id, 'Вы ввели дату в неправильном формате!')
                        key = InlineKeyboardMarkup()
                        key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню модпанели',
                                                     callback_data='Вернуться в главное меню модпанели'))
                        await bot.send_message(chat_id, 'Введите дату события (в формате ДД.ММ.ГГГГ ЧЧ:ММ):',
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
                        await bot.send_message(chat_id, 'Событие создано!', reply_markup=user_markup)
                        await log(f'Event {creation_event.name} is created by {chat_id}')
                        if settings.new_event_setting:
                            await mailing(bot, creation_event)
                        with shelve.open(files.state_bd) as bd:
                            del bd[str(chat_id)]

            elif state_num == 6:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute("SELECT description FROM events WHERE name = " + "'" + message.text + "'")
                for i in cursor.fetchall(): a += 1
                if a == 0:
                    await bot.send_message(chat_id,
                                           'Выбранного события не обнаружено! '
                                           'Выберите его, нажав на соотвествующую кнопку')
                else:
                    cursor.execute("DELETE FROM events WHERE name = " + "'" + message.text + "';")
                    con.commit()
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Добавить новое событие', 'Удалить событие')
                    user_markup.row('Редактирование событий')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(chat_id, 'Событие успешно удалено!', reply_markup=user_markup)
                    await log(f'Event {message.text} is deleted by {chat_id}')
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(chat_id)]
                con.close()

            elif state_num == 7:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute("SELECT name FROM events WHERE name = " + "'" + message.text + "';")
                for i in cursor.fetchall(): a += 1

                if a == 0:
                    await bot.send_message(chat_id, 'События с таким названием нет!\nВыберите заново!')
                else:
                    edition_event.name = message.text
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Изменить название', 'Изменить описание')
                    user_markup.row('Изменить дату', 'Изменить тип')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(chat_id, 'Теперь выберите, что хотите изменить', reply_markup=user_markup)
                    with shelve.open(files.state_bd) as bd:
                        bd[str(chat_id)] = 8
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
                await bot.send_message(chat_id, 'Название события успешно изменено!', reply_markup=user_markup)
                await log(f'Name event {edition_event.name} is changed by {chat_id}')
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 8

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
                await bot.send_message(chat_id, 'Описание события успешно изменено!', reply_markup=user_markup)
                await log(f'Description event {edition_event.name} is changed by {chat_id}')
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 8

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
                    await bot.send_message(chat_id, 'Дата события успешно изменена!', reply_markup=user_markup)
                    await log(f'Date event {edition_event.name} is changed by {chat_id}')
                    with shelve.open(files.state_bd) as bd:
                        bd[str(chat_id)] = 8
                else:
                    try:
                        datetime.strptime(message.text, "%d.%m.%Y %H:%M")
                    except:
                        await bot.send_message(chat_id, 'Вы ввели дату в неправильном формате!')
                        key = InlineKeyboardMarkup()
                        key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                                     callback_data='Вернуться в главное меню админки'))
                        await bot.send_message(chat_id, 'Введите дату события (в формате ДД.ММ.ГГГГ ЧЧ:ММ):',
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
                        await bot.send_message(chat_id, 'Дата события успешно изменена!', reply_markup=user_markup)
                        await log(f'Date event {edition_event.name} is changed by {chat_id}')
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 8

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
                await bot.send_message(chat_id, 'Тип события успешно изменено!', reply_markup=user_markup)
                await log(f'Type event {edition_event.name} is changed by {chat_id}')
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 8


async def moder_inline(bot, callback_data, chat_id, message_id):
    if callback_data == 'Вернуться в главное меню модпанели':
        if get_state(chat_id) is True:
            with shelve.open(files.state_bd) as bd: del bd[str(chat_id)]
        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('События')

        await bot.delete_message(chat_id, message_id)  # удаляется старое сообщение
        await bot.send_message(chat_id, 'Вы вошли в панель модератора!\nЧтобы выйти из неё, нажмите /start',
                               reply_markup=user_markup)
