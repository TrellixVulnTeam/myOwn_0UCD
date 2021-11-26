import sqlite3
import shelve
from datetime import datetime

import files
from defs import get_moder_list, get_state, new_moder, log
from extensions import Event
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


creation_event = Event()
edition_event = Event()


async def moder_panel(bot, chat_id):
    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.row('События')

    await bot.send_message(chat_id, """ Добро пожаловать в панель модератора.
    """, parse_mode='MarkDown', reply_markup=user_markup)

    await log(f'Launch moder panel of bot by moder {chat_id}')


async def in_moder_panel(bot, chat_id, message_text):
    if chat_id in get_moder_list():
        if message_text == 'Вернуться в главное меню' or message_text == '/mod':
            if get_state(chat_id) is True:
                with shelve.open(files.state_bd) as bd: del bd[str(chat_id)]
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('События')

            await bot.send_message(chat_id, 'Вы вошли в панель модератора!\nЧтобы выйти из неё, нажмите /start',
                                   reply_markup=user_markup)

        elif message_text == 'События':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Добавить новое событие', 'Удалить событие')
            user_markup.row('Редактирование событий')
            user_markup.row('Вернуться в главное меню')

            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            events = 'Созданые события:\n\n'
            a = 0
            try:
                cursor.execute("SELECT name, description, date FROM events;")
            except:
                cursor.execute("CREATE TABLE events (id INT, name TEXT, "
                               "description TEXT, date DATETIME);")
            else:
                for name, description, date in cursor.fetchall():
                    a += 1
                    events += str(a) + '. ' + name + ' - ' + str(date) + ' МСК - ' + description + '\n'
                con.close()

            if a == 0:
                events = "События не созданы!"
            else:
                pass
            await bot.send_message(chat_id, events, reply_markup=user_markup, parse_mode='HTML')

        elif message_text == 'Добавить новое событие':
            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                         callback_data='Вернуться в главное меню админки'))
            await bot.send_message(chat_id, 'Введите название события:', reply_markup=key)
            with shelve.open(files.state_bd) as bd:
                bd[str(chat_id)] = 2

        elif message_text == 'Редактирование событий':
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

        elif message_text == 'Изменить название':
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

        elif message_text == 'Изменить описание':
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

        elif message_text == 'Изменить дату':
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

        elif message_text == 'Удалить событие':
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

            if state_num == 2:
                creation_event.name = message_text
                # print(message_text)
                key = InlineKeyboardMarkup()
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                             callback_data='Вернуться в главное меню админки'))
                await bot.send_message(chat_id, f'Введите описание для {message_text}', reply_markup=key)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 3

            elif state_num == 3:
                creation_event.description = message_text
                key = InlineKeyboardMarkup()
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню админки',
                                             callback_data='Вернуться в главное меню админки'))
                await bot.send_message(chat_id, 'Введите дату события (в формате ДД.ММ.ГГГГ ЧЧ:ММ):', reply_markup=key)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 4

            elif state_num == 4:
                creation_event.date = message_text
                if creation_event.date == 'TBA':
                    con = sqlite3.connect(files.main_db)
                    cursor = con.cursor()
                    cursor.execute("INSERT INTO events (name, description, date) VALUES " +
                                   "('" + creation_event.name + "', '" + creation_event.description + "', '" +
                                   creation_event.date + "')")
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
                        datetime.strptime(message_text, "%d.%m.%Y %H:%M")
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
                        cursor.execute("INSERT INTO events (name, description, date) VALUES " +
                                       "('" + creation_event.name + "', '" + creation_event.description + "', '" +
                                       creation_event.date + "')")
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
                cursor.execute("SELECT description FROM events WHERE name = " + "'" + message_text + "'")
                for i in cursor.fetchall(): a += 1
                if a == 0:
                    await bot.send_message(chat_id,
                                           'Выбранного события не обнаружено! '
                                           'Выберите его, нажав на соотвествующую кнопку')
                else:
                    cursor.execute("DELETE FROM events WHERE name = " + "'" + message_text + "';")
                    con.commit()
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Добавить новое событие', 'Удалить событие')
                    user_markup.row('Редактирование событий')
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(chat_id, 'Событие успешно удалено!', reply_markup=user_markup)
                    await log(f'Event {message_text} is deleted by {chat_id}')
                    with shelve.open(files.state_bd) as bd:
                        del bd[str(chat_id)]
                con.close()

            elif state_num == 7:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute("SELECT name FROM events WHERE name = " + "'" + message_text + "';")
                for i in cursor.fetchall(): a += 1

                if a == 0:
                    await bot.send_message(chat_id, 'События с таким названием нет!\nВыберите заново!')
                else:
                    edition_event.name = message_text
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
                cursor.execute("UPDATE events SET name = '" + message_text + "' WHERE name = '" +
                               edition_event.name + "';")
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
                cursor.execute("UPDATE events SET description = '" + message_text + "' WHERE name = '" +
                               edition_event.name + "';")
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
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute("UPDATE events SET date = '" + message_text + "' WHERE name = '" +
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


async def moder_inline(bot, callback_data, chat_id, message_id):
    if 'Вернуться в главное меню модпанели' == callback_data:
        if get_state(chat_id) is True:
            with shelve.open(files.state_bd) as bd: del bd[str(chat_id)]
        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('События')

        await bot.delete_message(chat_id, message_id)  # удаляется старое сообщение
        await bot.send_message(chat_id, 'Вы вошли в панель модератора!\nЧтобы выйти из неё, нажмите /start',
                               reply_markup=user_markup)
