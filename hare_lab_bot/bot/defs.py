import logging
import sqlite3
import shelve
import yaml
import pendulum

from aiogram.types import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.json import json

import files
from config import admin_id

# set logging level
logging.basicConfig(filename=files.system_log, format='%(levelname)s:%(name)s:%(asctime)s:%(message)s',
                    datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)


# запись в файл логирования
async def log(text):
    time = str(pendulum.now())
    try:
        with open(files.working_log, 'a', encoding='utf-8') as f:
            f.write(time + '    | ' + text + '\n')
    except:
        with open(files.working_log, 'w', encoding='utf-8') as f:
            f.write(time + '    | ' + text + '\n')


def get_author_list():
    authors_list = []
    a = 0

    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    try:
        cursor.execute("SELECT id, username, experience FROM authors;")
    except:
        cursor.execute("CREATE TABLE IF NOT EXISTS authors (id INT, username TEXT, experience INT );")
        cursor.execute("SELECT id, username, experience FROM authors;")

    for id_a, name, exp in cursor.fetchall():
        a += 1
        author = (id_a, name, exp)
        authors_list.append(author)

    con.close()
    return authors_list


def get_admin_list():
    admins_list = []
    a = 0

    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    try:
        cursor.execute("SELECT id, username FROM admins;")
    except:
        cursor.execute("CREATE TABLE IF NOT EXISTS admins (id INT, username TEXT);")
        cursor.execute("SELECT id, username FROM admins;")

    for id_a, name in cursor.fetchall():
        a += 1
        admin = (id_a, name)
        admins_list.append(admin)

    con.close()
    return admins_list


def get_moder_list():
    moders_list = []
    a = 0

    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    try:
        cursor.execute("SELECT id, username FROM moders;")
    except:
        cursor.execute("CREATE TABLE IF NOT EXISTS moders (id INT, username TEXT);")
        cursor.execute("SELECT id, username FROM moders;")

    for id_m, name in cursor.fetchall():
        a += 1
        moder = (id_m, name)
        moders_list.append(moder)

    con.close()
    return moders_list


def new_author(settings, his_id, his_username, experience=None):
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS authors (id INT, username TEXT, experience INT );")
    if experience is None:
        experience = 0
        try:
            cursor.execute("INSERT INTO authors (id, username, experience) "
                           f"VALUES ({str(his_id)}, '{str(his_username)}', {str(experience)});")
        except:
            cursor.execute(f"UPDATE authors SET experience = {str(experience)} WHERE id = {str(his_id)};")
    elif experience >= settings.threshold_xp:
        try:
            cursor.execute("INSERT INTO authors (id, username, experience) "
                           f"VALUES ({str(his_id)}, '{str(his_username)}', {str(experience)});")
        except:
            cursor.execute(f"UPDATE authors SET experience = {str(experience)} WHERE id = {str(his_id)};")

    con.commit()
    con.close()


def new_admin(his_id, his_username):
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS admins (id INT, username TEXT);")
    cursor.execute(f"INSERT OR IGNORE INTO admins (id, username) VALUES ({str(his_id)}, '{str(his_username)}');")

    con.commit()
    con.close()


def new_moder(his_id, his_username):
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS moders (id INT, username TEXT);")
    cursor.execute(f"INSERT OR IGNORE INTO moders (id, username) VALUES ({str(his_id)}, '{str(his_username)}');")

    con.commit()
    con.close()


def set_state(chat_id, state):
    with shelve.open(files.state_bd) as bd:
        bd[str(chat_id)] = state


def get_state(chat_id):
    with shelve.open(files.state_bd) as bd:
        try:
            state_num = bd[str(chat_id)]
        except:
            return False
        else:
            return state_num


def delete_state(chat_id):
    with shelve.open(files.state_bd) as bd:
        del bd[str(chat_id)]


def new_blocked_user(his_id):
    pass


def check_message(message):
    with shelve.open(files.bot_message_bd) as bd:
        if message in bd:
            return True
        else:
            return False


def del_id(table, id_for_del):
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()

    cursor.execute(f"DELETE FROM {str(table)} WHERE id = {str(id_for_del)};")
    con.commit()
    con.close()


# изменение настроек бота и запись в файл настроек
def change_settings(settings):
    new_settings = {
        'Settings':
            {
                'TimeZone': settings.time_zone,
                'ChannelName': settings.channel_name,
                'ChannelID': settings.channel_id,
                'ThresholdXP': settings.threshold_xp
            }
                    }
    with open(files.settings, 'w') as f:
        yaml.dump(new_settings, f)


# изменение фразы и сохранение её в файл
def change_phrase(phrase, file):
    with open(file, 'w', encoding='utf-8') as f:
        f.write(str(phrase) + '\n')


async def get_csv(bot, settings):
    try:
        csv = settings.session.get(settings.url_csv).text
    except:
        logging.info('Session was closed')
        await bot.send_message(admin_id, 'Данные не могут быть обновлены!\n'
                                         'Вставьте ссылку с одноразовым ключом для доступа к csv файлу! '
                                         'Получите её у Combot по команде /onetime.')
        with shelve.open(files.state_bd) as bd:
            bd[str(admin_id)] = 55
        return False
    else:
        with open('csv.csv', "w", encoding='utf-8') as file:
            file.write(csv)

        with open('csv.csv', encoding='utf-8') as file:
            for line in file.readlines():
                if "<!DOCTYPE html>" in line:
                    settings.session.close()
                    settings.session = None
                    await bot.send_message(admin_id, 'Данные не могут быть обновлены!\n'
                                                     'Вставьте действительную '
                                                     'ссылку с одноразовым ключом для доступа к csv файлу! '
                                                     'Получите её у Combot по команде /onetime.')
                    with shelve.open(files.state_bd) as bd:
                        bd[str(admin_id)] = 55
                    return False
                else:
                    line = line.split(',')
                    if int(line[0]) == 5064416622:
                        continue
                    elif int(line[0]) == 777000:
                        continue
                    elif int(line[0]) == 136817688:
                        continue
                    elif int(line[0]) in [int(line[0]) for item in get_admin_list() if int(line[0]) in item]:
                        continue
                    elif int(line[0]) in [int(line[0]) for item in get_moder_list() if int(line[0]) in item]:
                        continue
                    else:
                        try:
                            new_author(settings, int(line[0]), line[2], int(line[5]))
                        except ValueError:
                            pass
            return True


async def preview(bot, message, preview_post, settings):
    '''preview'''
    entity_list = []
    if preview_post.post_date == '':
        preview_post.post_date = 'Нет даты проведения'
    if preview_post.what_needs == '':
        preview_post.what_needs = 'Нет требований'
    name_entities = json.loads(str(preview_post.name_entities))
    description_entities = json.loads(str(preview_post.desc_entities))
    date_entities = json.loads(str(preview_post.date_entities))
    what_needs_entities = json.loads(str(preview_post.what_needs_entities))
    footer_text_entities = json.loads(str(settings.footer_text_entities))
    text = f'{preview_post.post_name}\n\n' \
           f'{preview_post.post_desc}\n\n' \
           f'✅ {preview_post.what_needs}\n\n' \
           f'📆 {preview_post.post_date}\n\n' \
           f'{preview_post.hashtags}\n\n' \
           f'Автор: @{preview_post.author_name}\n' \
           f'{settings.footer_text}'

    if type(preview_post.pic_post) is tuple:
        if preview_post.pic_post[0] == '':
            text_format_char = 4096
        else:
            text_format_char = 1024
    else:
        if preview_post.pic_post == '':
            text_format_char = 4096
        else:
            text_format_char = 1024

    count_string_track = 0

    entity = MessageEntity(type="bold",
                           offset=count_string_track,
                           length=len(preview_post.post_name))
    entity_list.append(entity)

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

    count_string_track += len(str(preview_post.post_name)) + 2

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

    count_string_track += len(str(preview_post.post_desc)) + len(str('\n\n✅ '))

    if "entities" in what_needs_entities:

        for entity in what_needs_entities["entities"]:
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

    count_string_track += len(str(preview_post.what_needs)) + len(str('\n\n📆 '))

    if "entities" in date_entities:

        for entity in date_entities["entities"]:
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

    count_string_track += len(str(preview_post.post_date)) + 2 + len(str(preview_post.hashtags)) + 3

    entity = MessageEntity(type="italic",
                           offset=count_string_track,
                           length=len('Автор'))
    entity_list.append(entity)

    count_string_track += len(f'Автор: @{preview_post.author_name}\n')

    if "entities" in footer_text_entities:

        for entity in footer_text_entities["entities"]:
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

    inline_status = InlineKeyboardMarkup()
    inline_status.add(InlineKeyboardButton(text=f"Статус: {'размещён' if preview_post.status else 'не размещён'}",
                                           callback_data='status'))

    try:
        if type(preview_post.pic_post) is tuple:
            if preview_post.pic_post[0] == '':
                await bot.send_message(message.chat.id, text, entities=entity_list, reply_markup=inline_status)
            else:
                photo = open(preview_post.pic_post[0], 'rb')
                await bot.send_photo(message.chat.id, photo, caption=text, caption_entities=entity_list,
                                     reply_markup=inline_status)
        else:
            if preview_post.pic_post == '':
                await bot.send_message(message.chat.id, text, entities=entity_list, reply_markup=inline_status)
            else:
                photo = open(preview_post.pic_post, 'rb')
                await bot.send_photo(message.chat.id, photo, caption=text, caption_entities=entity_list,
                                     reply_markup=inline_status)
    except Exception as e:
        if str(e) == 'Media_caption_too_long':
            await bot.send_message(message.chat.id, 'Пост слишком большой, нужно его сократить.\n'
                                                    f'Сейчас количество символов: {len(text)}.\n'
                                                    f'Должно быть: {text_format_char}')


async def edit_post(bot, message, edited_post, settings, edit_picture):
    '''preview'''
    entity_list = []
    if edited_post.post_date == '':
        edited_post.post_date = 'Нет даты проведения'
    if edited_post.what_needs == '':
        edited_post.what_needs = 'Нет требований'
    name_entities = json.loads(str(edited_post.name_entities))
    description_entities = json.loads(str(edited_post.desc_entities))
    date_entities = json.loads(str(edited_post.date_entities))
    what_needs_entities = json.loads(str(edited_post.what_needs_entities))
    footer_text_entities = json.loads(str(settings.footer_text_entities))
    text = f'{edited_post.post_name}\n\n' \
           f'{edited_post.post_desc}\n\n' \
           f'✅ {edited_post.what_needs}\n\n' \
           f'📆 {edited_post.post_date}\n\n' \
           f'{edited_post.hashtags}\n\n' \
           f'Автор: @{edited_post.author_name}\n' \
           f'{settings.footer_text}'

    if type(edited_post.pic_post) is tuple:
        if edited_post.pic_post[0] == '':
            text_format_char = 4096
        else:
            text_format_char = 1024
    else:
        if edited_post.pic_post == '':
            text_format_char = 4096
        else:
            text_format_char = 1024

    count_string_track = 0

    entity = MessageEntity(type="bold",
                           offset=count_string_track,
                           length=len(edited_post.post_name))
    entity_list.append(entity)

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

    count_string_track += len(str(edited_post.post_name)) + 2

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

    count_string_track += len(str(edited_post.post_desc)) + len(str('\n\n✅ '))

    if "entities" in what_needs_entities:

        for entity in what_needs_entities["entities"]:
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

    count_string_track += len(str(edited_post.what_needs)) + len(str('\n\n📆 '))

    if "entities" in date_entities:

        for entity in date_entities["entities"]:
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

    count_string_track += len(str(edited_post.post_date)) + 2 + len(str(edited_post.hashtags)) + 3

    entity = MessageEntity(type="italic",
                           offset=count_string_track,
                           length=len('Автор'))
    entity_list.append(entity)

    count_string_track += len(f'Автор: @{edited_post.author_name}\n')

    if "entities" in footer_text_entities:

        for entity in footer_text_entities["entities"]:
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

    if edit_picture:
        if type(edited_post.pic_post) is tuple:
            if edited_post.pic_post[0] == '':
                pass
            else:
                photo = open(edited_post.pic_post[0], 'rb')
                await bot.edit_message_media(media=photo, chat_id=settings.channel_name,
                                             message_id=edited_post.message_id)
        else:
            if edited_post.pic_post == '':
                pass
            else:
                photo = open(edited_post.pic_post, 'rb')
                await bot.edit_message_media(media=photo, chat_id=settings.channel_name,
                                             message_id=edited_post.message_id)
    else:
        if type(edited_post.pic_post) is tuple:
            if edited_post.pic_post[0] == '':
                await bot.edit_message_text(chat_id=settings.channel_name, message_id=edited_post.message_id,
                                            text=text, entities=entity_list)
            else:
                await bot.edit_message_caption(chat_id=settings.channel_name, message_id=edited_post.message_id,
                                               caption=text, caption_entities=entity_list)
        else:
            if edited_post.pic_post == '':
                await bot.edit_message_text(chat_id=settings.channel_name, message_id=edited_post.message_id,
                                            text=text, entities=entity_list)
            else:
                await bot.edit_message_caption(chat_id=settings.channel_name, message_id=edited_post.message_id,
                                               caption=text, caption_entities=entity_list)
