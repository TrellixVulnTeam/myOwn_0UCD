import sqlite3
import shelve
import yaml
import pendulum

from aiogram.types import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.json import json

import files
from extensions import Event_List


# запись в файл логирования
async def log(text):
    time = str(pendulum.now())
    try:
        with open(files.working_log, 'a', encoding='utf-8') as f:
            f.write(time + '    | ' + text + '\n')
    except:
        with open(files.working_log, 'w', encoding='utf-8') as f:
            f.write(time + '    | ' + text + '\n')


def get_admin_list():
    admins_list = []
    a = 0

    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    try:
        cursor.execute("SELECT id, username FROM admins;")
    except:
        cursor.execute("CREATE TABLE admins (id INT, username TEXT);")

    for id_a, name in cursor.fetchall():
        a += 1
        admin = (id_a, name)
        admins_list.append(admin)

    return admins_list


def get_moder_list():
    moders_list = []
    a = 0

    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    try:
        cursor.execute("SELECT id, username FROM moders;")
    except:
        cursor.execute("CREATE TABLE moders (id INT, username TEXT);")

    for id_m, name in cursor.fetchall():
        a += 1
        moder = (id_m, name)
        moders_list.append(moder)

    return moders_list


def new_admin(his_id, his_username):
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    try:
        cursor.execute("INSERT INTO admins (id, username) VALUES (" + str(his_id) + ", '" + str(his_username) + "');")
    except:
        cursor.execute("CREATE TABLE admins (id INT, username TEXT);")
        cursor.execute("INSERT INTO admins (id, username) VALUES (" + str(his_id) + ", '" + str(his_username) + "');")

    con.commit()
    con.close()


def new_moder(his_id, his_username):
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    try:
        cursor.execute("INSERT INTO moders (id, username) VALUES (" + str(his_id) + ", '" + str(his_username) + "');")
    except:
        cursor.execute("CREATE TABLE moders (id INT, username TEXT);")
        cursor.execute("INSERT INTO moders (id, username) VALUES (" + str(his_id) + ", '" + str(his_username) + "');")

    con.commit()
    con.close()


def get_state(chat_id):
    with shelve.open(files.state_bd) as bd:
        if str(chat_id) in bd: return True


# запись в список пользователей
# если 0 в качестве входного аргумента, выводит список пользователей
def user_logger(his_id, his_username=None):
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()

    if his_id == 0:
        users_list = []
        a = 0
        try:
            cursor.execute("SELECT id, username FROM users;")
        except:
            cursor.execute("CREATE TABLE users (id INT, username TEXT);")

        for id_u, name in cursor.fetchall():
            a += 1
            group = (id_u, name)
            users_list.append(group)

        con.close()
        return users_list
    else:
        try:
            cursor.execute(
                "INSERT INTO users (id, username) VALUES (" + his_id + ", '" + str(his_username) + "');")
        except:
            cursor.execute("CREATE TABLE users (id INT, username TEXT);")
            cursor.execute(
                "INSERT INTO users (id, username) VALUES (" + his_id + ", '" + str(his_username) + "');")

        con.commit()
        con.close()


# запись в список групп
# если 0 в качестве входного аргумента, выводит список групп
def chat_logger(chat_id, chat_name=None, chat_link=None):
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()

    if chat_id == 0:
        chats_list = []
        a = 0
        try:
            cursor.execute("SELECT id, name, link FROM groups;")
        except:
            cursor.execute("CREATE TABLE groups (id INT, name TEXT, link TEXT);")

        for id_g, name, link in cursor.fetchall():
            a += 1
            group = (id_g, name, link)
            chats_list.append(group)

        con.close()
        return chats_list
    else:
        if chat_link is not None:
            try:
                cursor.execute(
                    "INSERT INTO groups (id, name, link) VALUES (" + chat_id + ", '" + str(chat_name) +
                    "', '" + str(chat_link) + "');")
            except:
                cursor.execute("CREATE TABLE groups (id INT, name TEXT, link URL);")
                cursor.execute(
                    "INSERT INTO groups (id, name, link) VALUES (" + chat_id + ", '" + str(chat_name) +
                    "', '" + str(chat_link) + "');")
        else:
            try:
                cursor.execute(
                    "INSERT INTO groups (id, name) VALUES (" + chat_id + ", " + str(chat_name) + ");")
            except:
                cursor.execute("CREATE TABLE groups (id INT, name TEXT, link URL);")
                cursor.execute(
                    "INSERT INTO groups (id, name) VALUES (" + chat_id + ", " + str(chat_name) + ");")

        con.commit()
        con.close()


def new_blocked_user(his_id):
    with open(files.blockusers_list, 'w', encoding='utf-8') as f: return f.write(str(his_id) + '\n')


def check_message(message):
    with shelve.open(files.bot_message_bd) as bd:
        if message in bd:
            return True
        else:
            return False


def del_id(table, id_for_del):
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()

    cursor.execute("DELETE FROM " + str(table) + " WHERE id = " + str(id_for_del) + ";")
    con.commit()
    con.close()


# изменение настроек бота и запись в файл настроек
def change_settings(settings):
    new_settings = {
        'Settings':
            {
                'HotEventNotification': settings.hot_event_setting,
                'NewEventNotification': settings.new_event_setting,
                'TimeZone': settings.time_zone
            }
                    }
    with open(files.settings, 'w') as f:
        yaml.dump(new_settings, f)


# изменение фразы и сохранение её в файл
def change_phrase(phrase, file):
    with open(file, 'w', encoding='utf-8') as f:
        f.write(str(phrase) + '\n')


# рассылка уведомлений о создании нового события
async def mailing(bot, creation_event):
    get_list = 0
    entity_list = []
    name_entities = json.loads(str(creation_event.name_entities))
    description_entities = json.loads(str(creation_event.description_entities))
    count_string_track = len("Было добавлено новое событие!\n\n")

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

    count_string_track += len(str(creation_event.name)) + 3 + len(str(creation_event.date)) + 7

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

    for user in user_logger(get_list):
        try:
            await bot.send_message(user[0], f"Было добавлено новое событие!\n\n"
                                              f"{str(creation_event.name)} - {str(creation_event.date)} МСК - "
                                              f"{str(creation_event.description)}", entities=entity_list)
            await log(f"User {user[0]} got 'New event' message")
        except:
            await log(f"User {user[0]} didn't get 'New event' message")

            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            try:
                cursor.execute("SELECT id FROM users WHERE id = " + str(user[0]) + ";")
            except:
                pass
            else:
                cursor.execute("DELETE FROM users WHERE id = " + str(user[0]) + ";")
                con.commit()
            con.close()

    for chat in chat_logger(get_list):

        try:
            await bot.send_message(int(chat[0]), f"Было добавлено новое событие!\n\n"
                                                 f"{str(creation_event.name)} - {str(creation_event.date)} МСК - "
                                                 f"{str(creation_event.description)}", entities=entity_list)
            await log(f"Chat {int(chat[0])} got 'New event' message")
        except:
            await log(f"Chat {int(chat[0])} didn't get 'New event' message")

            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            try:
                cursor.execute("SELECT id FROM groups WHERE id = " + str(chat[0]) + ";")
            except:
                pass
            else:
                cursor.execute("DELETE FROM groups WHERE id = " + str(chat[0]) + ";")
                con.commit()
            con.close()


# рассылка уведомления о скором приближении события
async def hot_notification(bot, hot_event):
    get_list = 0
    entity_list = []
    name_entities = json.loads(hot_event[3])
    description_entities = json.loads(hot_event[4])
    count_string_track = len("Осталось меньше часа до события:\n\n") + 1 + len('🔥 ')

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

    count_string_track += len(str(hot_event[0])) + len(' - ') + len(str(hot_event[2])) + len(' МСК - ')

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

    for user in user_logger(get_list):
        try:
            await bot.send_message(user[0], f"Осталось меньше часа до события:\n\n"
                                              f"🔥 {str(hot_event[0])} - {str(hot_event[2])} МСК - "
                                              f"{str(hot_event[1])}", entities=entity_list)
            await log(f"User {user[0]} got 'Hot event' message")
        except:
            await log(f"User {user[0]} didn't get 'Hot event' message")

            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            try:
                cursor.execute("SELECT id FROM users WHERE id = " + str(user[0]) + ";")
            except:
                pass
            else:
                cursor.execute("DELETE FROM users WHERE id = " + str(user[0]) + ";")
                con.commit()
            con.close()

    for chat in chat_logger(get_list):

        try:
            await bot.send_message(int(chat[0]), f"Осталось меньше часа до события:\n\n"
                                                 f"🔥 {str(hot_event[0])} - {str(hot_event[2])} МСК - "
                                                 f"{str(hot_event[1])}", entities=entity_list)
            await log(f"Chat {int(chat[0])} got 'Hot event' message")
        except:
            await log(f"Chat {int(chat[0])} didn't get 'Hot event' message")

            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            try:
                cursor.execute("SELECT id FROM groups WHERE id = " + str(chat[0]) + ";")
            except:
                pass
            else:
                cursor.execute("DELETE FROM groups WHERE id = " + str(chat[0]) + ";")
                con.commit()
            con.close()


# постраничный вывод списков событий
async def page_output(message, last_page, page_num, time_zone):
    """
    На первой странице - предыдущие события и ближайшие,
    На второй странице - категория NFT mints,
    На третьей странице - категория Token sales,
    На четвертой странице - категория Whitelist / Registration deadline,
    На пятой странице - категория Testnets,
    На шестой странице - категория Trend token (эта категория особенная:
                                            не имеет даты, и пока не относится к предыдущим).

    :param time_zone:
    :param message: types.Message from aiogram
    :param last_page: int
    :param page_num: int
    :return: events: List
    :return: entity_list: List[types.MessageEntity from aiogram]
    :return: inline_paginator: types.InlineKeyboardMarkup(types.InlineKeyboardButton) from aiogram
    """

    events_list = Event_List()
    last_page.last_page[message.message_id] = page_num

    entity_list = []

    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    events = ''
    a = 0
    try:
        cursor.execute("SELECT name, description, date, name_entities, description_entities, "
                       "type_event FROM events;")
    except:
        cursor.execute("CREATE TABLE events (id INT, name TEXT, "
                       "description TEXT, date DATETIME, name_entities JSON, description_entities JSON, "
                       "type_event TEXT);")
    else:
        now = pendulum.now(time_zone)

        for name, description, date, name_entities, description_entities, type_event in cursor.fetchall():
            a += 1
            if type_event == 'Trend token':
                events_list.events_TT.append((name, description, date, name_entities,
                                              description_entities, type_event))
                continue

            if date == 'TBA':
                events_list.events_unsorted.update({(name, description, date, name_entities,
                                                     description_entities, type_event): 'TBA'})
            else:
                date_formatted = pendulum.from_format(date, "DD.MM.YYYY HH:mm", tz=time_zone)
                delta = date_formatted - now
                delta = divmod(delta.total_seconds(), 3600)
                events_list.events_unsorted.update({(name, description, date, name_entities,
                                                     description_entities, type_event): int(delta[0])})

        con.close()

        for events_key, events_value in events_list.events_unsorted.items():
            if events_value == 'TBA':
                events_list.events_TBA.append(events_key)
                continue
            if -3 <= events_value <= 23:
                if -3 <= events_value <= 1:
                    events_list.events_HOT_unsorted[events_key] = events_value
                    events_list.events_TODAY_unsorted[events_key] = events_value
                else:
                    events_list.events_TODAY_unsorted[events_key] = events_value
                continue
            if -23 <= events_value < -3:
                events_list.events_PREVIOUS_unsorted[events_key] = events_value
                continue
            if events_value > 23:
                events_list.events_UPCOMING_unsorted[events_key] = events_value
                continue

        events_list.sort_out_all_groups()

        if page_num == 1:
            count_string_track = 0
            events += "🔴Предыдущие события:\n"  # 21
            num_event = 1
            count_string_track += len("🔴Предыдущие события:\n") + 1

            for prev_events in events_list.events_types_pair[1][1]:

                name_entities = json.loads(prev_events[3])
                description_entities = json.loads(prev_events[4])
                count_string_track += len(str(num_event)) + 2

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

                count_string_track += len(prev_events[0]) + 3 + len(str(prev_events[2])) + 7

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

                count_string_track += len(prev_events[1]) + 1

                events += str(num_event) + '. ' + prev_events[0] + ' - ' + \
                          prev_events[2] + ' МСК - ' + prev_events[1] + '\n'
                num_event += 1

            events += "\n🟢Ближайшие события:\n"  # 21
            num_event = 1
            count_string_track += len("\n🟢Ближайшие события:\n") + 1

            for today_events in events_list.events_types_pair[2][1]:
                name_entities = json.loads(today_events[3])
                description_entities = json.loads(today_events[4])
                count_string_track += len(str(num_event)) + 2

                if today_events in events_list.events_types_pair[0][1]:
                    count_string_track += 3
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

                    count_string_track += len(today_events[0]) + 3 + len(str(today_events[2])) + 7

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

                    count_string_track += len(today_events[1]) + 1

                    events += str(num_event) + '. 🔥 ' + today_events[0] + ' - ' + \
                              today_events[2] + ' МСК - ' + today_events[1] + '\n'
                else:
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

                    count_string_track += len(today_events[0]) + 3 + len(str(today_events[2])) + 7

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

                    count_string_track += len(today_events[1]) + 1

                    events += str(num_event) + '. ' + today_events[0] + ' - ' + \
                              today_events[2] + ' МСК - ' + today_events[1] + '\n'
                num_event += 1

        elif page_num == 2:
            count_string_track = 0
            events += "🔵Предстоящие события:\n"
            num_event = 1
            count_string_track += len("🔵Предстоящие события:\n") + 1

            entity = MessageEntity(type='bold',
                                   offset=count_string_track + 0,
                                   length=len("\nNFT mints:\n"))
            entity_list.append(entity)
            entity = MessageEntity(type='underline',
                                   offset=count_string_track + 0,
                                   length=len("\nNFT mints:\n"))
            entity_list.append(entity)

            events += "\nNFT mints:\n"
            count_string_track += len("\nNFT mints:\n")

            for upcom_events in events_list.events_types_pair[3][1]:
                if upcom_events[5] == 'NFT mints':
                    name_entities = json.loads(upcom_events[3])
                    description_entities = json.loads(upcom_events[4])
                    count_string_track += len(str(num_event)) + 2

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

                    count_string_track += len(upcom_events[0]) + 3 + len(str(upcom_events[2])) + 7

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

                    count_string_track += len(upcom_events[1]) + 1

                    events += str(num_event) + '. ' + upcom_events[0] + ' - ' + \
                              upcom_events[2] + ' МСК - ' + upcom_events[1] + '\n'
                    num_event += 1

            for tba_events in events_list.events_TBA:
                if tba_events[5] == 'NFT mints':
                    name_entities = json.loads(tba_events[3])
                    description_entities = json.loads(tba_events[4])
                    count_string_track += len(str(num_event)) + 2

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

                    count_string_track += len(tba_events[0]) + 3 + len(str(tba_events[2])) + 7

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

                    count_string_track += len(tba_events[1]) + 1

                    events += str(num_event) + '. ' + tba_events[0] + ' - ' + \
                              tba_events[2] + ' МСК - ' + tba_events[1] + '\n'
                    num_event += 1

        elif page_num == 3:
            count_string_track = 0
            num_event = 1
            events += "🔵Предстоящие события:\n"
            count_string_track += len("🔵Предстоящие события:\n") + 1

            entity = MessageEntity(type='bold',
                                   offset=count_string_track + 0,
                                   length=len("\nToken sales:\n"))
            entity_list.append(entity)
            entity = MessageEntity(type='underline',
                                   offset=count_string_track + 0,
                                   length=len("\nToken sales:\n"))
            entity_list.append(entity)

            events += "\nToken sales:\n"
            count_string_track += len("\nToken sales:\n")

            for upcom_events in events_list.events_types_pair[3][1]:
                if upcom_events[5] == 'Token sales':
                    name_entities = json.loads(upcom_events[3])
                    description_entities = json.loads(upcom_events[4])
                    count_string_track += len(str(num_event)) + 2

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

                    count_string_track += len(upcom_events[0]) + 3 + len(str(upcom_events[2])) + 7

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

                    count_string_track += len(upcom_events[1]) + 1

                    events += str(num_event) + '. ' + upcom_events[0] + ' - ' + \
                              upcom_events[2] + ' МСК - ' + upcom_events[1] + '\n'
                    num_event += 1

            for tba_events in events_list.events_TBA:
                if tba_events[5] == 'Token sales':
                    name_entities = json.loads(tba_events[3])
                    description_entities = json.loads(tba_events[4])
                    count_string_track += len(str(num_event)) + 2

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

                    count_string_track += len(tba_events[0]) + 3 + len(str(tba_events[2])) + 7

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

                    count_string_track += len(tba_events[1]) + 1

                    events += str(num_event) + '. ' + tba_events[0] + ' - ' + \
                              tba_events[2] + ' МСК - ' + tba_events[1] + '\n'
                    num_event += 1

        elif page_num == 4:
            count_string_track = 0
            events += "🔵Предстоящие события:\n"
            num_event = 1
            count_string_track += len("🔵Предстоящие события:\n") + 1

            entity = MessageEntity(type='bold',
                                   offset=count_string_track + 0,
                                   length=len("\nWhitelist / Registration deadline:\n"))
            entity_list.append(entity)
            entity = MessageEntity(type='underline',
                                   offset=count_string_track + 0,
                                   length=len("\nWhitelist / Registration deadline:\n"))
            entity_list.append(entity)

            events += "\nWhitelist / Registration deadline:\n"
            count_string_track += len("\nWhitelist / Registration deadline:\n")

            for upcom_events in events_list.events_types_pair[3][1]:
                if upcom_events[5] == 'Whitelist / Registration deadline':
                    name_entities = json.loads(upcom_events[3])
                    description_entities = json.loads(upcom_events[4])
                    count_string_track += len(str(num_event)) + 2

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

                    count_string_track += len(upcom_events[0]) + 3 + len(str(upcom_events[2])) + 7

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

                    count_string_track += len(upcom_events[1]) + 1

                    events += str(num_event) + '. ' + upcom_events[0] + ' - ' + \
                              upcom_events[2] + ' МСК - ' + upcom_events[1] + '\n'
                    num_event += 1

            for tba_events in events_list.events_TBA:
                if tba_events[5] == 'Whitelist / Registration deadline':
                    name_entities = json.loads(tba_events[3])
                    description_entities = json.loads(tba_events[4])
                    count_string_track += len(str(num_event)) + 2

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

                    count_string_track += len(tba_events[0]) + 3 + len(str(tba_events[2])) + 7

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

                    count_string_track += len(tba_events[1]) + 1

                    events += str(num_event) + '. ' + tba_events[0] + ' - ' + \
                              tba_events[2] + ' МСК - ' + tba_events[1] + '\n'
                    num_event += 1

        elif page_num == 5:
            count_string_track = 0
            num_event = 1
            events += "🔵Предстоящие события:\n"
            count_string_track += len("🔵Предстоящие события:\n") + 1

            entity = MessageEntity(type='bold',
                                   offset=count_string_track + 0,
                                   length=len("\nTestnets:\n"))
            entity_list.append(entity)
            entity = MessageEntity(type='underline',
                                   offset=count_string_track + 0,
                                   length=len("\nTestnets:\n"))
            entity_list.append(entity)

            events += "\nTestnets:\n"
            count_string_track += len("\nTestnets:\n")

            for upcom_events in events_list.events_types_pair[3][1]:
                if upcom_events[5] == 'Testnets':
                    name_entities = json.loads(upcom_events[3])
                    description_entities = json.loads(upcom_events[4])
                    count_string_track += len(str(num_event)) + 2

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

                    count_string_track += len(upcom_events[0]) + 3 + len(str(upcom_events[2])) + 7

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

                    count_string_track += len(upcom_events[1]) + 1

                    events += str(num_event) + '. ' + upcom_events[0] + ' - ' + \
                              upcom_events[2] + ' МСК - ' + upcom_events[1] + '\n'
                    num_event += 1

            for tba_events in events_list.events_TBA:
                if tba_events[5] == 'Testnets':
                    name_entities = json.loads(tba_events[3])
                    description_entities = json.loads(tba_events[4])
                    count_string_track += len(str(num_event)) + 2

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

                    count_string_track += len(tba_events[0]) + 3 + len(str(tba_events[2])) + 7

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

                    count_string_track += len(tba_events[1]) + 1

                    events += str(num_event) + '. ' + tba_events[0] + ' - ' + \
                              tba_events[2] + ' МСК - ' + tba_events[1] + '\n'
                    num_event += 1

        elif page_num == 6:
            count_string_track = 0
            num_event = 1

            entity = MessageEntity(type='bold',
                                   offset=count_string_track + 0,
                                   length=len("💸Трендовые токены:\n"))
            entity_list.append(entity)
            entity = MessageEntity(type='underline',
                                   offset=count_string_track + 0,
                                   length=len("💸Трендовые токены:\n"))
            entity_list.append(entity)
            events += "💸Трендовые токены:\n"
            count_string_track += len("💸Трендовые токены:\n") + 1

            for tt_events in events_list.events_TT:
                name_entities = json.loads(tt_events[3])
                description_entities = json.loads(tt_events[4])
                count_string_track += len(str(num_event)) + 2

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

                count_string_track += len(tt_events[0]) + 3

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

                count_string_track += len(tt_events[1]) + 1

                events += str(num_event) + '. ' + tt_events[0] + ' - ' + tt_events[1] + '\n'
                num_event += 1

    inline_paginator = InlineKeyboardMarkup()
    forward_button = InlineKeyboardButton(text="➡️", callback_data="forward")
    backward_button = InlineKeyboardButton(text="⬅️", callback_data="backward")
    page_empty_button = InlineKeyboardButton(text=f"{page_num}/6", callback_data="nothing")
    inline_paginator.add(backward_button, page_empty_button, forward_button)

    return events, entity_list, inline_paginator
