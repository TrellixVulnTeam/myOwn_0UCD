import datetime
from datetime import datetime
import sqlite3
import shelve

import files
from extensions import Event
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from bot import config

creation_event = Event()
edition_event = Event()


async def log(text):
    time = str(datetime.now())
    try:
        with open(files.working_log, 'a', encoding='utf-8') as f:
            f.write(time + '    | ' + text + '\n')
    except:
        with open(files.working_log, 'w', encoding='utf-8') as f:
            f.write(time + '    | ' + text + '\n')


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
    user_markup.row('Список админов')
    user_markup.row('Скачать лог файл')
    if first__launch:
        await bot.send_message(chat_id, """Добро пожаловать в админ панель. Это первый запуск бота.\n 
        В следующий раз чтобы войти в админ панель введите команду '/adm'.
        """, parse_mode='MarkDown', reply_markup=user_markup)
        new_admin(chat_id)
        await log(f'First launch admin panel of bot by admin {chat_id}')  # логгируется первый запуск get_adminlist
    else:
        await bot.send_message(chat_id, """ Добро пожаловать в админ панель.
        """, parse_mode='MarkDown', reply_markup=user_markup)

        await log(f'Launch admin panel of bot by admin {chat_id}')  # логгируется первый запуск get_adminlist


async def in_admin_panel(bot, chat_id, message_text):

    if chat_id in get_adminlist():
        if message_text == 'Вернуться в главное меню' or message_text == '/adm':
            if get_state(chat_id) is True:
                with shelve.open(files.state_bd) as bd: del bd[str(chat_id)]
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('События')
            user_markup.row('Список пользователей')
            user_markup.row('Список админов')
            user_markup.row('Скачать лог файл')
            await bot.send_message(chat_id, 'Вы вошли в админку бота!\nЧтобы выйти из неё, нажмите /start',
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
                    events += name + ' - ' + str(date) + ' МСК - ' + description + '\n'
                con.close()

            if a == 0:
                events = "События не созданы!"
            else:
                pass
            await bot.send_message(chat_id, events, reply_markup=user_markup, parse_mode='Markdown')

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

        elif message_text == 'Список админов':
            admins = "Список админов:\n\n"
            for admin in get_adminlist():
                admins += f"{admin}\n"
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Добавить нового админа', 'Удалить админа')
            user_markup.row('Вернуться в главное меню')
            await bot.send_message(chat_id, admins, reply_markup=user_markup)

        elif message_text == 'Добавить нового админа':
            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton('Отменить и вернуться в главное меню админки',
                                         callback_data='Вернуться в главное меню админки'))
            await bot.send_message(chat_id, 'Введите id нового админа', reply_markup=key)
            with shelve.open(files.state_bd) as bd:
                bd[str(chat_id)] = 21

        elif message_text == 'Удалить админа':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for admin_id in get_adminlist():
                a += 1
                if int(admin_id) != config.admin_id: user_markup.row(str(admin_id))
            if a == 1:
                await bot.send_message(chat_id, 'Вы ещё не добавляли админов!')
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(chat_id, 'Выбери id админа, которого нужно удалить', reply_markup=user_markup)
                with shelve.open(files.state_bd) as bd:
                    bd[str(chat_id)] = 22

        elif message_text == 'Список пользователей':
            get_list = 0
            users = "Список пользователей:\n\n"
            for user in user_logger(get_list):
                users += f"{user}\n"
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Вернуться в главное меню')
            await bot.send_message(chat_id, users, reply_markup=user_markup)

        elif message_text == 'Скачать лог файл':
            working_log = open(files.working_log, 'rb')
            await bot.send_document(chat_id, working_log)
            working_log.close()

        elif get_state(chat_id) is True:
            with shelve.open(files.state_bd) as bd:
                state_num = bd[str(chat_id)]

            if state_num == 2:
                creation_event.name = message_text
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

            elif state_num == 21:
                new_admin(message_text)
                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Добавить нового админа', 'Удалить админа')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(chat_id, 'Новый админ успешно добавлен', reply_markup=user_markup)
                await log(f'New admin {message_text} is added by {chat_id}')
                with shelve.open(files.state_bd) as bd:
                    del bd[str(chat_id)]

            elif state_num == 22:
                with open(files.admins_list, encoding='utf-8') as f:
                    if str(message_text) in f.read():
                        del_id(files.admins_list, message_text)
                        await bot.send_message(chat_id, 'Админ успешно удалён из списка')
                        await log(f'The admin {message_text} is removed by {chat_id}')
                        with shelve.open(files.state_bd) as bd:
                            del bd[str(chat_id)]
                    else:
                        await bot.send_message(chat_id, 'Такого id в списках админов не обнаружено! '
                                                        'Выберите правильный id!')
                        with shelve.open(files.state_bd) as bd:
                            bd[str(chat_id)] = 22


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


def get_adminlist():
    admins_list = []
    with open(files.admins_list, encoding='utf-8') as f:
        for admin_id in f.readlines():
            admins_list.append(int(admin_id))
    return admins_list


def new_admin(his_id):
    with open(files.admins_list, encoding='utf-8') as f:
        if not str(his_id) in f.read():
            with open(files.admins_list, 'a', encoding='utf-8') as f: f.write(str(his_id) + '\n')


def get_state(chat_id):
    with shelve.open(files.state_bd) as bd:
        if str(chat_id) in bd: return True


def user_logger(chat_id):
    if chat_id == 0:
        users_list = []
        with open(files.users_list, encoding='utf-8') as f:
            for user_id in f.readlines():
                users_list.append(int(user_id))
        return users_list
    else:
        if chat_id not in get_adminlist():
            with open(files.users_list, encoding='utf-8') as f:
                if not str(chat_id) in f.read():
                    with open(files.users_list, 'a', encoding='utf-8') as f: f.write(str(chat_id) + '\n')


def new_blockuser(his_id):
    with open(files.blockusers_list, 'w', encoding='utf-8') as f: return f.write(str(his_id) + '\n')


def check_message(message):
    with shelve.open(files.bot_message_bd) as bd:
        if message in bd:
            return True
        else:
            return False


def del_id(file, chat_id):
    text = ''
    with open(file, encoding='utf-8') as f:
        for i in f.readlines():
            i = i[:len(i) - 1]
            if str(chat_id) == i:
                pass
            else:
                text += i + '\n'
    with open(file, 'w', encoding='utf-8') as f:
        f.write(text)
