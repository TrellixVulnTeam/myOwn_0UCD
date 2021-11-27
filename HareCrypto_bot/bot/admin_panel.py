import datetime
from datetime import datetime
import sqlite3
import shelve

from aiogram.utils.json import json

import files
from extensions import Event
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity

import config
from defs import get_admin_list, log, user_logger, new_admin, get_state, del_id, get_moder_list, new_moder

creation_event = Event()
edition_event = Event()


async def first_launch(bot, chat_id):
    try:
        with open(files.working_log, encoding='utf-8') as f:
            return False
    except:
        await admin_panel(bot, chat_id, first__launch=True)
        return True


async def admin_panel(bot, chat_id, first__launch=False):
    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.row('События')
    user_markup.row('Список пользователей')
    user_markup.row('Список модераторов')
    user_markup.row('Список админов')
    user_markup.row('Скачать лог файл')
    if first__launch:
        await bot.send_message(chat_id, """Добро пожаловать в админ панель. Это первый запуск бота.\n 
        В следующий раз чтобы войти в админ панель введите команду '/adm'.
        """, parse_mode='MarkDown', reply_markup=user_markup)
        new_admin(chat_id)
        await log(f'First launch admin panel of bot by admin {chat_id}')
    else:
        await bot.send_message(chat_id, """ Добро пожаловать в админ панель.
        """, parse_mode='MarkDown', reply_markup=user_markup)

        await log(f'Launch admin panel of bot by admin {chat_id}')


async def in_admin_panel(bot, chat_id, message):
    if chat_id in get_admin_list():
        if message.text == 'Вернуться в главное меню' or message.text == '/adm':
            if get_state(chat_id) is True:
                with shelve.open(files.state_bd) as bd: del bd[str(chat_id)]
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('События')
            user_markup.row('Список пользователей')
            user_markup.row('Список модераторов')
            user_markup.row('Список админов')
            user_markup.row('Скачать лог файл')
            await bot.send_message(chat_id, 'Вы вошли в админку бота!\nЧтобы выйти из неё, нажмите /start',
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
                cursor.execute("SELECT name, description, date, name_entities, description_entities FROM events;")
            except:
                cursor.execute("CREATE TABLE events (id INT, name TEXT, "
                               "description TEXT, date DATETIME, name_entities JSON, description_entities JSON);")
            else:
                for name, description, date, name_entities, description_entities in cursor.fetchall():
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

                con.close()

            if a == 0:
                events = "События не созданы!"
            else:
                pass
            await bot.send_message(chat_id, events, reply_markup=user_markup, entities=entity_list)

        elif message.text == 'Добавить новое событие':
            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                         callback_data='Вернуться в главное меню админки'))
            await bot.send_message(chat_id, 'Введите название события:', reply_markup=key)
            with shelve.open(files.state_bd) as bd:
                bd[str(chat_id)] = 2

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
                        await bot.send_message(chat_id, 'Введите новую дату события (в формате ДД.ММ.ГГГГ ЧЧ:ММ)',
                                               parse_mode='Markdown', reply_markup=user_markup)
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 11
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

        elif message.text == 'Список админов':
            admins = "Список админов:\n\n"
            for admin in get_admin_list():
                admins += f"<a href='tg://user?id={admin}'>{admin}</a>\n"
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Добавить нового админа', 'Удалить админа')
            user_markup.row('Вернуться в главное меню')
            await bot.send_message(chat_id, admins, reply_markup=user_markup, parse_mode="HTML")

        elif message.text == 'Добавить нового админа':
            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton('Отменить и вернуться в главное меню админки',
                                         callback_data='Вернуться в главное меню админки'))
            await bot.send_message(chat_id, 'Введите id нового админа', reply_markup=key)
            with shelve.open(files.state_bd) as bd:
                bd[str(chat_id)] = 21

        elif message.text == 'Удалить админа':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for admin_id in get_admin_list():
                a += 1
                if int(admin_id) != config.admin_id: user_markup.row(str(admin_id))
            if a == 1:
                await bot.send_message(chat_id, 'Вы ещё не добавляли админов!')
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(chat_id, 'Выбери id админа, которого нужно удалить', reply_markup=user_markup)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 22

        elif message.text == 'Список модераторов':
            moders = "Список модераторов:\n\n"
            for moder in get_moder_list():
                moders += f"<a href='tg://user?id={moder}'>{moder}</a>\n"
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Добавить нового модератора', 'Удалить модератора')
            user_markup.row('Вернуться в главное меню')
            await bot.send_message(chat_id, moders, reply_markup=user_markup, parse_mode="HTML")

        elif message.text == 'Добавить нового модератора':
            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton('Отменить и вернуться в главное меню админки',
                                         callback_data='Вернуться в главное меню админки'))
            await bot.send_message(chat_id, 'Введите id нового модератора', reply_markup=key)
            with shelve.open(files.state_bd) as bd:
                bd[str(chat_id)] = 31

        elif message.text == 'Удалить модератора':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for moder_id in get_moder_list():
                a += 1
                user_markup.row(str(moder_id))
            if a == 0:
                await bot.send_message(chat_id, 'Вы ещё не добавляли модераторов!')
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(chat_id, 'Выбери id модератора, которого нужно удалить',
                                       reply_markup=user_markup)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 32

        elif message.text == 'Список пользователей':
            get_list = 0
            users = "Список пользователей:\n\n"
            for user in user_logger(get_list):
                users += f"<a href='tg://user?id={user}'>{user}</a>\n"
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Вернуться в главное меню')
            await bot.send_message(chat_id, users, reply_markup=user_markup, parse_mode="HTML")

        elif message.text == 'Скачать лог файл':
            working_log = open(files.working_log, 'rb')
            await bot.send_document(chat_id, working_log)
            working_log.close()

        elif get_state(chat_id) is True:
            with shelve.open(files.state_bd) as bd:
                state_num = bd[str(chat_id)]

            if state_num == 2:
                creation_event.name = message.text
                creation_event.name_entities = message

                key = InlineKeyboardMarkup()
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                             callback_data='Вернуться в главное меню админки'))
                await bot.send_message(chat_id, f'Введите описание для {message.text}', reply_markup=key)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 3

            elif state_num == 3:
                creation_event.description = message.text
                creation_event.description_entities = message

                key = InlineKeyboardMarkup()
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                             callback_data='Вернуться в главное меню админки'))
                await bot.send_message(chat_id, 'Введите дату события (в формате ДД.ММ.ГГГГ ЧЧ:ММ):', reply_markup=key)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 4

            elif state_num == 4:
                creation_event.date = message.text
                if creation_event.date == 'TBA':
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    cursor.execute("INSERT INTO events (name, description, date, name_entities, " +
                                   "description_entities) VALUES " + "('" + str(creation_event.name) + "', '" +
                                   str(creation_event.description) + "', '" + str(creation_event.date) + "', '" +
                                   str(creation_event.name_entities) + "', '" +
                                   str(creation_event.description_entities) + "')")
                    con.commit()
                    con.close()
                    key = InlineKeyboardMarkup()
                    key.add(InlineKeyboardButton(text='Вернуться в главное меню админки',
                                                 callback_data='Вернуться в главное меню админки'))
                    await bot.send_message(chat_id, 'Событие создано!', reply_markup=key)
                    await log(f'Event {creation_event.name} is created by {chat_id}')
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(chat_id)]
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
                        cursor.execute("INSERT INTO events (name, description, date, name_entities," +
                                       " description_entities)  VALUES " +
                                       "('" + str(creation_event.name) + "', '" + str(creation_event.description) +
                                       "', '" + str(creation_event.date) + "', '" + str(creation_event.name_entities) +
                                       "', '" + str(creation_event.description_entities) + "')")
                        con.commit()
                        con.close()
                        key = InlineKeyboardMarkup()
                        key.add(InlineKeyboardButton(text='Вернуться в главное меню админки',
                                                     callback_data='Вернуться в главное меню админки'))
                        await bot.send_message(chat_id, 'Событие создано!', reply_markup=key)
                        await log(f'Event {creation_event.name} is created by {chat_id}')
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
                    user_markup.row('Изменить дату')
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
                user_markup.row('Изменить дату')
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
                user_markup.row('Изменить дату')
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
                    user_markup.row('Изменить дату')
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
                        user_markup.row('Изменить дату')
                        user_markup.row('Вернуться в главное меню')
                        await bot.send_message(chat_id, 'Дата события успешно изменена!', reply_markup=user_markup)
                        await log(f'Date event {edition_event.name} is changed by {chat_id}')
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 8

            elif state_num == 21:
                new_admin(message.text)
                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Добавить нового админа', 'Удалить админа')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(chat_id, 'Новый админ успешно добавлен', reply_markup=user_markup)
                await log(f'New admin {message.text} is added by {chat_id}')
                with shelve.open(files.state_bd) as bd:
                    del bd[str(chat_id)]

            elif state_num == 22:
                with open(files.admins_list, encoding='utf-8') as f:
                    if str(message.text) in f.read():
                        del_id(files.admins_list, message.text)
                        await bot.send_message(chat_id, 'Админ успешно удалён из списка')
                        await log(f'The admin {message.text} is removed by {chat_id}')
                        with shelve.open(files.state_bd) as bd:
                            del bd[str(chat_id)]
                    else:
                        await bot.send_message(chat_id, 'Такого id в списках админов не обнаружено! '
                                                        'Выберите правильный id!')
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 22

            elif state_num == 31:
                new_moder(message.text)
                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Добавить нового модератора', 'Удалить модератора')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(chat_id, 'Новый модератор успешно добавлен', reply_markup=user_markup)
                await log(f'New moder {message.text} is added by {chat_id}')
                with shelve.open(files.state_bd) as bd:
                    del bd[str(chat_id)]

            elif state_num == 32:
                with open(files.moders_list, encoding='utf-8') as f:
                    if str(message.text) in f.read():
                        del_id(files.moders_list, message.text)
                        await bot.send_message(chat_id, 'Модератор успешно удалён из списка')
                        await log(f'The moder {message.text} is removed by {chat_id}')
                        with shelve.open(files.state_bd) as bd:
                            del bd[str(chat_id)]
                    else:
                        await bot.send_message(chat_id, 'Такого id в списках модераторов не обнаружено! '
                                                        'Выберите правильный id!')
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 32


async def admin_inline(bot, callback_data, chat_id, message_id):
    if 'Вернуться в главное меню админки' == callback_data:
        if get_state(chat_id) is True:
            with shelve.open(files.state_bd) as bd: del bd[str(chat_id)]
        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('События')
        user_markup.row('Список пользователей')
        user_markup.row('Список админов')
        user_markup.row('Скачать лог файл')
        await bot.delete_message(chat_id, message_id)  # удаляется старое сообщение
        await bot.send_message(chat_id, 'Вы вошли в админку бота!\nЧтобы выйти из неё, нажмите /start',
                               reply_markup=user_markup)
