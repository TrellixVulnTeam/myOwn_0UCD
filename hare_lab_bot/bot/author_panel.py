import sqlite3
import shelve
import logging
from aiogram.utils.json import json

import files
from defs import get_moder_list, get_state, log, delete_state, set_state, get_admin_list, get_author_list, preview, \
    edit_post
from extensions import Post
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity

# set logging level
logging.basicConfig(filename=files.system_log, format='%(levelname)s:%(name)s:%(asctime)s:%(message)s',
                    datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)

creation_post_author = Post()
edition_post_author = Post()
unposted_post_author = Post()


async def author_panel(bot, message):
    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.row('Посты')
    user_markup.row('Списки')

    await bot.send_message(message.chat.id, "Добро пожаловать в панель автора.", reply_markup=user_markup)

    await log(f'Launch author panel of bot by moder {message.chat.id}')


async def in_author_panel(bot, settings, message):
    """
    Функция состоит из двух частей: в первой части обработка текстовых команд,
    во второй - обработка состояний переписки.

    При добавлении поста учитываются состояния 1, 2, 3, 4, 5, 6, 7:
    1 - ввод темы поста,
    2 - ввод описания,
    3 - ввод даты или дедлайна,
    4 - ввод требований для участия,
    5 - вставка баннера,
    6 - ввод хэштегов,
    7 - подтверждение создания поста

    При размещение постов учитываются состояния 9, 10:
    9 - вывод неразмещённых постов
    10 -

    При удалении поста - состояние 11:
    11 - выбор поста для удаления

    При редактировании поста - состояния 12, 13, 14, 15, 16, 17, 18, 19:
    12 - выбор поста для редактирования из существующих,
    13 - состояние изменения поста,
    14 - изменение темы поста,
    15 - изменение описания поста,
    16 - изменение даты поста,
    17 - изменение требований к участию,
    18 - изменение баннера,
    19 - изменение хэштегов

    :param bot: Bot from aiogram
    :param settings: object class: Settings from hare_bot.py
    :param message: types.Message from aiogram
    :return: None
    """
    if message.chat.id in [message.chat.id for item in get_author_list() if message.chat.id in item]:
        if message.text == 'Вернуться в главное меню':
            if get_state(message.chat.id) is True:
                with shelve.open(files.state_bd) as bd: del bd[str(message.chat.id)]
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Посты')
            user_markup.row('Списки')

            await bot.send_message(message.chat.id, 'Вы в главном меню бота.',
                                   reply_markup=user_markup)

        elif message.text == 'Посты':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Добавить новый пост', 'Удалить пост')
            user_markup.row('Редактирование постов', 'Размещение постов')
            user_markup.row('Вернуться в главное меню')

            entity_list = []
            count_string_track = len('Созданные посты:\n\n')
            events = 'Созданные посты:\n\n'
            a = 0
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()

            try:
                cursor.execute("SELECT author_name, post_name, post_date, "
                               f"name_entities, date_entities, status FROM posts WHERE author_id = {message.chat.id};")
            except:
                cursor.execute("SELECT author_name, post_name, post_date, "
                               f"name_entities, date_entities, status FROM posts WHERE author_id = {message.chat.id};")
            else:
                for author_name, post_name, post_date, name_entities, date_entities, status in cursor.fetchall():
                    a += 1
                    count_string_track += len(str(a)) + 2
                    name_entities = json.loads(str(name_entities))

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

                    count_string_track += len(post_name) + 3

                    count_string_track += len(author_name) + 3 + len('Posted' if status else 'Not posted') + 1

                    events += str(a) + '. ' + str(post_name) + ' - ' + str(author_name) + \
                              ' - ' + str('Posted' if status else 'Not posted') + '\n'

                    if a % 10 == 0:
                        await bot.send_message(message.chat.id, events, reply_markup=user_markup, entities=entity_list)
                        entity_list = []
                        count_string_track = len('Созданные посты:\n\n')
                        events = 'Созданные посты:\n\n'

                con.close()

            if a == 0:
                events = "Посты не созданы!"
            else:
                pass

            await bot.send_message(message.chat.id, events, reply_markup=user_markup, entities=entity_list)

        elif message.text == 'Добавить новый пост':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Вернуться в главное меню')

            with open(files.example_text, encoding='utf-8') as example_text:
                example_text = example_text.read()

            example_entities = []
            raw_entities = [{"type": "bold", "offset": 0, "length": 46},
                            {"type": "underline", "offset": 0, "length": 46},
                            {"type": "code", "offset": 46, "length": 27},
                            {"type": "bold", "offset": 73, "length": 23},
                            {"type": "pre", "offset": 96, "length": 31},
                            {"type": "text_link", "offset": 127, "length": 10,
                             "url": "https://t.me/harecrypta"},
                            {"type": "text_link", "offset": 247, "length": 3,
                             "url": "https://t.me/harecrypta_chat"},
                            {"type": "pre", "offset": 636, "length": 36},
                            {"type": "italic", "offset": 672, "length": 1},
                            {"type": "text_link", "offset": 742, "length": 5,
                             "url": "https://t.me/harecrypta"},
                            {"type": "text_link", "offset": 779, "length": 4,
                             "url": "https://t.me/harecrypta_chat"},
                            {"type": "text_link", "offset": 813, "length": 16,
                             "url": "https://t.me/HareCrypta_lab_ann"},
                            {"type": "text_link", "offset": 863, "length": 9,
                             "url": "https://www.youtube.com/c/Harecrypta"},
                            {"type": "pre", "offset": 872, "length": 35},
                            {"type": "italic", "offset": 907, "length": 2},
                            {"type": "pre", "offset": 927, "length": 24},
                            {"type": "hashtag", "offset": 951, "length": 11},
                            {"type": "hashtag", "offset": 963, "length": 10},
                            {"type": "hashtag", "offset": 974, "length": 7},
                            {"type": "italic", "offset": 983, "length": 22},
                            {"type": "code", "offset": 1006, "length": 12}]

            for entity in raw_entities:
                if entity["type"] == "text_link":
                    entity = MessageEntity(type=entity["type"],
                                           offset=entity["offset"],
                                           length=entity["length"], url=entity["url"])
                    example_entities.append(entity)
                elif (entity["type"] == "mention") or (entity["type"] == "url") or \
                        (entity["type"] == "hashtag") or (entity["type"] == "cashtag") or \
                        (entity["type"] == "bot_command") or (entity["type"] == "pre") or \
                        (entity["type"] == "email") or (entity["type"] == "phone_number") or \
                        (entity["type"] == "bold") or (entity["type"] == "italic") or \
                        (entity["type"] == "underline") or (entity["type"] == "strikethrough") \
                        or (entity["type"] == "code"):
                    entity = MessageEntity(type=entity["type"],
                                           offset=entity["offset"],
                                           length=entity["length"])
                    example_entities.append(entity)

            photo = open(files.photo_example, 'rb')
            await bot.send_photo(message.chat.id, photo, caption=example_text, caption_entities=example_entities)

            await bot.send_message(message.chat.id, 'Введите тему поста', reply_markup=user_markup)
            set_state(message.chat.id, 1)

        elif message.text == 'Размещение постов':
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute(f"SELECT post_name, status FROM posts WHERE author_id = {message.chat.id};")
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for post_name, status in cursor.fetchall():
                if status:
                    pass
                else:
                    a += 1
                    user_markup.row(str(post_name))
            if a == 0:
                await bot.send_message(message.chat.id, 'Не размещенных постов нет!', reply_markup=user_markup)
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Какой пост хотите разместить?',
                                       parse_mode='Markdown', reply_markup=user_markup)
                set_state(message.chat.id, 9)
            con.close()

        elif message.text == 'Редактирование постов':
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute(f"SELECT author_name, post_name, post_date FROM posts WHERE author_id = {message.chat.id};")
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for author_name, post_name, post_date in cursor.fetchall():
                a += 1
                user_markup.row(str(post_name))
            if a == 0:
                await bot.send_message(message.chat.id, 'Никаких постов ещё не создано!', reply_markup=user_markup)
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Какой пост хотите редактировать?',
                                       parse_mode='Markdown', reply_markup=user_markup)
                set_state(message.chat.id, 12)
            con.close()

        elif message.text == 'Изменить тему':
            if get_state(message.chat.id) == 13 or get_state(message.chat.id) == 130:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute(f"SELECT post_name FROM posts WHERE post_name = '{str(edition_post_author.post_name)}';")
                for i in cursor.fetchall(): a += 1
                if a == 0:
                    await bot.send_message(message.chat.id, 'Поста с такой темой нет!\nВыберите заново!')
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Введите новую тему поста',
                                           parse_mode='Markdown', reply_markup=user_markup)
                    if get_state(message.chat.id) == 13:
                        set_state(message.chat.id, 14)
                    elif get_state(message.chat.id) == 130:
                        set_state(message.chat.id, 140)
                con.close()

        elif message.text == 'Изменить описание':
            if get_state(message.chat.id) == 13 or get_state(message.chat.id) == 130:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute(f"SELECT post_desc FROM posts WHERE post_name = '{str(edition_post_author.post_name)}';")
                for i in cursor.fetchall(): a += 1
                if a == 0:
                    await bot.send_message(message.chat.id, 'Поста с таким описанием нет!\nВыберите заново!')
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Введите новое описание поста',
                                           parse_mode='Markdown', reply_markup=user_markup)
                    if get_state(message.chat.id) == 13:
                        set_state(message.chat.id, 15)
                    elif get_state(message.chat.id) == 130:
                        set_state(message.chat.id, 150)
                con.close()

        elif message.text == 'Изменить дату':
            if get_state(message.chat.id) == 13 or get_state(message.chat.id) == 130:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute(f"SELECT post_date FROM posts WHERE post_name = '{str(edition_post_author.post_name)}';")
                for i in cursor.fetchall(): a += 1
                if a == 0:
                    await bot.send_message(message.chat.id, 'Поста с такой датой нет!\nВыберите заново!')
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Введите новую дату поста',
                                           parse_mode='Markdown', reply_markup=user_markup)
                    if get_state(message.chat.id) == 13:
                        set_state(message.chat.id, 16)
                    elif get_state(message.chat.id) == 130:
                        set_state(message.chat.id, 160)
                con.close()

        elif message.text == 'Изменить требования':
            if get_state(message.chat.id) == 13 or get_state(message.chat.id) == 130:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute(f"SELECT what_needs FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")
                for i in cursor.fetchall(): a += 1
                if a == 0:
                    await bot.send_message(message.chat.id, 'Поста с такими требованиями нет!\nВыберите заново!')
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Введите что нужно сделать для участия',
                                           parse_mode='Markdown', reply_markup=user_markup)
                    if get_state(message.chat.id) == 13:
                        set_state(message.chat.id, 17)
                    elif get_state(message.chat.id) == 130:
                        set_state(message.chat.id, 170)
                con.close()

        elif message.text == 'Изменить баннер':
            if get_state(message.chat.id) == 13 or get_state(message.chat.id) == 130:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute(f"SELECT pic_post FROM posts WHERE post_name = '{str(edition_post_author.post_name)}';")
                for i in cursor.fetchall(): a += 1
                if a == 0:
                    await bot.send_message(message.chat.id, 'Поста с таким баннером нет!\nВыберите заново!')
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Вставьте баннер (изображение) поста.'
                                                            'Или если нет баннера, то пропишите /empty',
                                           parse_mode='Markdown', reply_markup=user_markup)
                    if get_state(message.chat.id) == 13:
                        set_state(message.chat.id, 18)
                    elif get_state(message.chat.id) == 130:
                        set_state(message.chat.id, 180)
                con.close()

        elif message.text == 'Изменить хэштеги':
            if get_state(message.chat.id) == 13 or get_state(message.chat.id) == 130:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                a = 0
                cursor.execute(f"SELECT hashtags FROM posts WHERE post_name = '{str(edition_post_author.post_name)}';")
                for i in cursor.fetchall(): a += 1
                if a == 0:
                    await bot.send_message(message.chat.id, 'Поста с такими хэштегами нет!\nВыберите заново!')
                else:
                    user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    user_markup.row('Вернуться в главное меню')
                    await bot.send_message(message.chat.id, 'Введите новые хэштеги',
                                           parse_mode='Markdown', reply_markup=user_markup)
                    if get_state(message.chat.id) == 13:
                        set_state(message.chat.id, 19)
                    elif get_state(message.chat.id) == 130:
                        set_state(message.chat.id, 190)
                con.close()

        elif message.text == 'Удалить пост':
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute(f"SELECT author_name, post_name, post_date FROM posts WHERE author_id = {message.chat.id};")
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            a = 0
            for author_username, post_name, post_date in cursor.fetchall():
                a += 1
                user_markup.row(str(post_name))
            if a == 0:
                await bot.send_message(message.chat.id, 'Никаких постов ещё не создано!', reply_markup=user_markup)
            else:
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Какой пост нужно удалить?',
                                       parse_mode='Markdown', reply_markup=user_markup)
                set_state(message.chat.id, 11)
            con.close()

        elif message.text == 'Списки':
            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Список авторов')
            user_markup.row('Список модераторов', 'Список админов')
            user_markup.row('Вернуться в главное меню')

            await bot.send_message(message.chat.id, "Выберите список для отображения", reply_markup=user_markup)

        elif message.text == 'Список авторов':
            authors = "Список авторов:\n\n"
            if len(get_author_list()) != 0:
                for author in get_author_list():
                    authors += f"{author[0]} - @{author[1]} - {author[2]} XP\n"

                await bot.send_message(message.chat.id, authors, parse_mode="HTML")
            else:
                await bot.send_message(message.chat.id, "Авторов еще нет")

        elif message.text == 'Список админов':
            admins = "Список админов:\n\n"
            if len(get_admin_list()) != 0:
                for admin in get_admin_list():
                    admins += f"{admin[0]} - @{admin[1]}\n"

                await bot.send_message(message.chat.id, admins, parse_mode="HTML")
            else:
                await bot.send_message(message.chat.id, "Админов еще нет")

        elif message.text == 'Список модераторов':
            moders = "Список модераторов:\n\n"
            if len(get_moder_list()) != 0:
                for moder in get_moder_list():
                    moders += f"{moder[0]} - @{moder[1]}\n"
                await bot.send_message(message.chat.id, moders, parse_mode="HTML")
            else:
                await bot.send_message(message.chat.id, "Модераторов еще нет")

        elif get_state(message.chat.id) == 1:
            creation_post_author.author_name = message.chat.username
            creation_post_author.author_id = message.chat.id
            creation_post_author.post_name = message.text
            creation_post_author.name_entities = message

            user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('Вернуться в главное меню')
            await bot.send_message(message.chat.id, f'Тема поста: {str(creation_post_author.post_name)}',
                                   reply_markup=user_markup)

            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                         callback_data='Вернуться в главное меню'))
            await bot.send_message(message.chat.id, f'Введите описание для {creation_post_author.post_name}',
                                   reply_markup=key)
            set_state(message.chat.id, 2)

        elif get_state(message.chat.id) == 2:
            creation_post_author.post_desc = message.text
            creation_post_author.desc_entities = message

            key = InlineKeyboardMarkup()
            key.row(InlineKeyboardButton(text='ДА', callback_data='Есть дата проведения'),
                    InlineKeyboardButton(text='НЕТ', callback_data='Нет даты проведения'))
            key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                         callback_data='Вернуться в главное меню'))
            await bot.send_message(message.chat.id, 'Есть ли дата проведения события или дедлайн?',
                                   reply_markup=key)

        elif get_state(message.chat.id) == 3:
            creation_post_author.post_date = message.text
            creation_post_author.date_entities = message

            key = InlineKeyboardMarkup()
            key.row(InlineKeyboardButton(text='ДА', callback_data='Есть требования'),
                    InlineKeyboardButton(text='НЕТ', callback_data='Нет требований'))
            key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                         callback_data='Вернуться в главное меню'))
            await bot.send_message(message.chat.id, 'Нужно ли что-то сделать для участия?', reply_markup=key)

        elif get_state(message.chat.id) == 4:
            creation_post_author.what_needs = message.text
            creation_post_author.what_needs_entities = message

            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                         callback_data='Вернуться в главное меню'))
            await bot.send_message(message.chat.id, 'Важное напоминание!!! '
                                                    'Определитесь, будет ли в нём картинка.'
                                                    'Если вы не добавите картинку сразу, '
                                                    'то потом вы её не сможете уже добавить, и если картинка уже была,'
                                                    'то вы не сможете её убрать!')
            await bot.send_message(message.chat.id, 'Вставьте баннер (изображение) поста. '
                                                    'Или если нет баннера, то пропишите /empty', reply_markup=key)

            set_state(message.chat.id, 5)

        elif get_state(message.chat.id) == 5:
            if message.text == '/empty':
                creation_post_author.pic_post = ''
            elif message.document:
                file_info = await bot.get_file(message.document.file_id)
                downloaded_file = await bot.download_file(file_info.file_path)

                src = f'data/media/posts_media/pic for post - {creation_post_author.post_name}.jpeg'
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file.getvalue())

                creation_post_author.pic_post = src
                await bot.send_message(message.chat.id, 'Изображение загружено.')
            elif message.photo:
                file_info = await bot.get_file(message.photo[-1].file_id)
                downloaded_file = await bot.download_file(file_info.file_path)

                src = f'data/media/posts_media/pic for post - {creation_post_author.post_name}.jpeg'
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file.getvalue())

                creation_post_author.pic_post = src
                await bot.send_message(message.chat.id, 'Изображение загружено.')

            key = InlineKeyboardMarkup()
            key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                         callback_data='Вернуться в главное меню'))
            await bot.send_message(message.chat.id, 'Введите хэштеги поста', reply_markup=key)

            set_state(message.chat.id, 6)

        elif get_state(message.chat.id) == 6:
            if '#' in message.text:
                creation_post_author.hashtags = message.text

                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute("INSERT INTO posts (author_name, author_id, post_name, post_desc, post_date, "
                               "what_needs, hashtags, pic_post, name_entities, desc_entities, date_entities, "
                               f"what_needs_entities) VALUES ('{str(creation_post_author.author_name)}', "
                               f"{str(creation_post_author.author_id)}, '{str(creation_post_author.post_name)}', "
                               f"'{str(creation_post_author.post_desc)}', '{str(creation_post_author.post_date)}', "
                               f"'{str(creation_post_author.what_needs)}', '{str(creation_post_author.hashtags)}', "
                               f"'{str(creation_post_author.pic_post)}', '{str(creation_post_author.name_entities)}', "
                               f"'{str(creation_post_author.desc_entities)}', '{str(creation_post_author.date_entities)}', "
                               f"'{str(creation_post_author.what_needs_entities)}');")
                con.commit()
                con.close()

                await bot.send_message(message.chat.id, 'Пост был сохранён в базу данных.')

                await preview(bot, message, creation_post_author, settings)

                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton(text='ДА', callback_data='Редактировать пост'),
                        InlineKeyboardButton(text='НЕТ', callback_data='Подтвердить пост'))
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                             callback_data='Вернуться в главное меню'))
                await bot.send_message(message.chat.id, 'Хотите ли редактировать пост?', reply_markup=key)
            else:
                await bot.send_message(message.chat.id, 'Вы не ввели ни одного хэштега!'
                                                        'Введите хэштеги поста.')

        elif get_state(message.chat.id) == 7:
            if message.text.lower() == 'да':
                entity_list = []
                if creation_post_author.post_date == '':
                    creation_post_author.post_date = 'Нет даты проведения'
                if creation_post_author.what_needs == '':
                    creation_post_author.what_needs = 'Нет требований'
                name_entities = json.loads(str(creation_post_author.name_entities))
                description_entities = json.loads(str(creation_post_author.desc_entities))
                date_entities = json.loads(str(creation_post_author.date_entities))
                what_needs_entities = json.loads(str(creation_post_author.what_needs_entities))
                footer_text_entities = json.loads(settings.footer_text_entities)
                text = f'{creation_post_author.post_name}\n\n' \
                       f'{creation_post_author.post_desc}\n\n' \
                       f'✅ {creation_post_author.what_needs}\n\n' \
                       f'📆 {creation_post_author.post_date}\n\n' \
                       f'{creation_post_author.hashtags}\n\n' \
                       f'Автор: @{creation_post_author.author_name}\n' \
                       f'{settings.footer_text}'
                count_string_track = 0

                entity = MessageEntity(type="bold",
                                       offset=count_string_track,
                                       length=len(creation_post_author.post_name))
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

                count_string_track += len(str(creation_post_author.post_name)) + 2

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

                count_string_track += len(str(creation_post_author.post_desc)) + len(str('\n\n✅ '))

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

                count_string_track += len(str(creation_post_author.what_needs)) + len(str('\n\n📆 '))

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

                count_string_track += len(str(creation_post_author.post_date)) + 2 + \
                                      len(str(creation_post_author.hashtags)) + 3

                entity = MessageEntity(type="italic",
                                       offset=count_string_track,
                                       length=len('Автор'))
                entity_list.append(entity)

                count_string_track += len(f'Автор: @{creation_post_author.author_name}\n')

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

                if type(creation_post_author.pic_post) is tuple:
                    if creation_post_author.pic_post[0] == '':
                        message_result = await bot.send_message(settings.channel_name, text, entities=entity_list)
                    else:
                        photo = open(creation_post_author.pic_post[0], 'rb')
                        message_result = await bot.send_photo(settings.channel_name,
                                                              photo, caption=text, caption_entities=entity_list)
                else:
                    if creation_post_author.pic_post == '':
                        message_result = await bot.send_message(settings.channel_name, text, entities=entity_list)
                    else:
                        photo = open(creation_post_author.pic_post, 'rb')
                        message_result = await bot.send_photo(settings.channel_name,
                                                              photo, caption=text, caption_entities=entity_list)

                await bot.send_message(message.chat.id, 'Пост был создан и размещен на канале.')

                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute(f"UPDATE posts SET status = 1, message_id = {message_result.message_id} "
                               f"WHERE post_name = '{str(creation_post_author.post_name)}';")
                con.commit()
                con.close()

                delete_state(message.chat.id)
            else:
                await bot.send_message(message.chat.id, "Ты не написал 'Да', поэтому Пост не был размещён.")

                delete_state(message.chat.id)

        elif get_state(message.chat.id) == 9:
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            a = 0
            cursor.execute(f"SELECT author_name, post_name, post_date, post_desc, what_needs, hashtags, "
                           f"pic_post, name_entities, desc_entities, date_entities, what_needs_entities, "
                           f"status FROM posts WHERE post_name = '{message.text}';")
            for author_name, post_name, post_date, post_desc, what_needs, hashtags, \
                pic_post, name_entities, desc_entities, date_entities, \
                what_needs_entities, status in cursor.fetchall():
                a += 1
                unposted_post_author.author_name = author_name
                unposted_post_author.post_name = post_name
                unposted_post_author.post_desc = post_desc
                unposted_post_author.post_date = post_date
                unposted_post_author.what_needs = what_needs
                unposted_post_author.hashtags = hashtags
                unposted_post_author.pic_post = pic_post
                unposted_post_author.name_entities = name_entities
                unposted_post_author.desc_entities = desc_entities
                unposted_post_author.date_entities = date_entities
                unposted_post_author.what_needs_entities = what_needs_entities
                unposted_post_author.status = status

            if a == 0:
                await bot.send_message(message.chat.id, 'Поста с таким названием нет!\nВыберите заново!')
            else:
                unposted_post_author.post_name = message.text
                await preview(bot, message, unposted_post_author, settings)

                post_key = InlineKeyboardMarkup()
                post_key.add(InlineKeyboardButton(text="ДА", callback_data='Разместить пост'),
                             InlineKeyboardButton(text="НЕТ", callback_data='Вернуться в меню размещения'))

                await bot.send_message(message.chat.id, 'Разместить данный пост?',
                                       reply_markup=post_key)
                set_state(message.chat.id, 10)
            con.close()

        elif get_state(message.chat.id) == 10:
            pass

        elif get_state(message.chat.id) == 11:
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            a = 0
            cursor.execute(f"SELECT post_name, message_id FROM posts WHERE post_name = '{message.text}'")
            for post_name, message_id in cursor.fetchall():
                a += 1
                try:
                    await bot.delete_message(settings.channel_name, message_id)
                except:
                    await bot.send_message(message.chat.id, 'Пост не может быть удалён из канала: '
                                                            'он не был там размещён!')
            if a == 0:
                await bot.send_message(message.chat.id,
                                       'Выбранного поста не обнаружено! '
                                       'Выберите его, нажав на соответствующую кнопку')
            else:
                cursor.execute(f"DELETE FROM posts WHERE post_name = '{message.text}';")
                con.commit()

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Добавить новый пост', 'Удалить пост')
                user_markup.row('Редактирование постов', 'Размещение постов')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Пост успешно удален!', reply_markup=user_markup)
                await log(f'Post {message.text} is deleted by {message.chat.id}')
                delete_state(message.chat.id)
            con.close()

        elif get_state(message.chat.id) == 12:
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            a = 0
            cursor.execute(f"SELECT author_name, post_name, post_date, post_desc, what_needs, hashtags, "
                           f"pic_post, name_entities, desc_entities, date_entities, what_needs_entities, "
                           f"status FROM posts WHERE post_name = '{message.text}';")
            for author_name, post_name, post_date, post_desc, what_needs, hashtags, \
                pic_post, name_entities, desc_entities, date_entities, \
                what_needs_entities, status in cursor.fetchall():
                a += 1
                edition_post_author.author_name = author_name
                edition_post_author.post_name = post_name
                edition_post_author.post_desc = post_desc
                edition_post_author.post_date = post_date
                edition_post_author.what_needs = what_needs
                edition_post_author.hashtags = hashtags
                edition_post_author.pic_post = pic_post
                edition_post_author.name_entities = name_entities
                edition_post_author.desc_entities = desc_entities
                edition_post_author.date_entities = date_entities
                edition_post_author.what_needs_entities = what_needs_entities
                edition_post_author.status = status

            if a == 0:
                await bot.send_message(message.chat.id, 'Поста с таким названием нет!\nВыберите заново!')
            else:
                edition_post_author.post_name = message.text
                await preview(bot, message, edition_post_author, settings)

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить тему', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить требования')
                user_markup.row('Изменить баннер', 'Изменить хэштеги')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Теперь выберите, что хотите изменить',
                                       reply_markup=user_markup)
                set_state(message.chat.id, 13)
            con.close()

        elif get_state(message.chat.id) == 14 or get_state(message.chat.id) == 140:
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute(f"UPDATE posts SET post_name = '{message.text}', name_entities = '{str(message)}' "
                           f"WHERE post_name = '{str(edition_post_author.post_name)}';")
            con.commit()

            if get_state(message.chat.id) == 14:
                cursor.execute(f"SELECT author_name, post_name, post_date, post_desc, what_needs, hashtags, "
                               f"pic_post, name_entities, desc_entities, date_entities, what_needs_entities, "
                               f"status, message_id FROM posts WHERE post_name = '{message.text}';")

                for author_name, post_name, post_date, post_desc, what_needs, hashtags, \
                    pic_post, name_entities, desc_entities, date_entities, \
                    what_needs_entities, status, message_id in cursor.fetchall():
                    edition_post_author.author_name = author_name
                    edition_post_author.post_name = post_name
                    edition_post_author.post_desc = post_desc
                    edition_post_author.post_date = post_date
                    edition_post_author.what_needs = what_needs
                    edition_post_author.hashtags = hashtags
                    edition_post_author.pic_post = pic_post
                    edition_post_author.name_entities = name_entities
                    edition_post_author.desc_entities = desc_entities
                    edition_post_author.date_entities = date_entities
                    edition_post_author.what_needs_entities = what_needs_entities
                    edition_post_author.status = status
                    edition_post_author.message_id = message_id

                if edition_post_author.status:
                    await edit_post(bot, message, edition_post_author, settings, 0)
                else:
                    pass

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить тему', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить требования')
                user_markup.row('Изменить баннер', 'Изменить хэштеги')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Тема поста успешно изменена!', reply_markup=user_markup)
                await log(f'Name post {edition_post_author.post_name} is changed by {message.chat.id}')
                set_state(message.chat.id, 13)

            elif get_state(message.chat.id) == 140:
                cursor.execute(f"SELECT post_name, name_entities FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")

                for post_name, name_entities in cursor.fetchall():
                    creation_post_author.post_name = post_name
                    creation_post_author.name_entities = name_entities

                await preview(bot, message, creation_post_author, settings)

                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton(text='ДА', callback_data='Редактировать пост'),
                        InlineKeyboardButton(text='НЕТ', callback_data='Подтвердить пост'))
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                             callback_data='Вернуться в главное меню'))
                await bot.send_message(message.chat.id, 'Хотите ли редактировать пост?', reply_markup=key)
            con.close()

        elif get_state(message.chat.id) == 15 or get_state(message.chat.id) == 150:
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute(f"UPDATE posts SET post_desc = '{message.text}', desc_entities = '{str(message)}' "
                           f"WHERE post_name = '{str(edition_post_author.post_name)}';")
            con.commit()

            if get_state(message.chat.id) == 15:
                cursor.execute(f"SELECT author_name, post_name, post_date, post_desc, what_needs, hashtags, "
                               f"pic_post, name_entities, desc_entities, date_entities, what_needs_entities, "
                               f"status, message_id FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")

                for author_name, post_name, post_date, post_desc, what_needs, hashtags, \
                    pic_post, name_entities, desc_entities, date_entities, \
                    what_needs_entities, status, message_id in cursor.fetchall():
                    edition_post_author.author_name = author_name
                    edition_post_author.post_name = post_name
                    edition_post_author.post_desc = post_desc
                    edition_post_author.post_date = post_date
                    edition_post_author.what_needs = what_needs
                    edition_post_author.hashtags = hashtags
                    edition_post_author.pic_post = pic_post
                    edition_post_author.name_entities = name_entities
                    edition_post_author.desc_entities = desc_entities
                    edition_post_author.date_entities = date_entities
                    edition_post_author.what_needs_entities = what_needs_entities
                    edition_post_author.status = status
                    edition_post_author.message_id = message_id

                if edition_post_author.status:
                    await edit_post(bot, message, edition_post_author, settings, 0)
                else:
                    pass

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить тему', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить требования')
                user_markup.row('Изменить баннер', 'Изменить хэштеги')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Описание поста успешно изменено!', reply_markup=user_markup)
                await log(f'Description post {edition_post_author.post_name} is changed by {message.chat.id}')
                set_state(message.chat.id, 13)
            elif get_state(message.chat.id) == 150:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute(f"SELECT post_desc, desc_entities FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")
                for post_desc, desc_entities in cursor.fetchall():
                    creation_post_author.post_desc = post_desc
                    creation_post_author.desc_entities = desc_entities
                con.close()

                await preview(bot, message, creation_post_author, settings)

                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton(text='ДА', callback_data='Редактировать пост'),
                        InlineKeyboardButton(text='НЕТ', callback_data='Подтвердить пост'))
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                             callback_data='Вернуться в главное меню'))
                await bot.send_message(message.chat.id, 'Хотите ли редактировать пост?', reply_markup=key)
            con.close()

        elif get_state(message.chat.id) == 16 or get_state(message.chat.id) == 160:
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute(f"UPDATE posts SET post_date = '{message.text}', date_entities = '{str(message)}' "
                           f"WHERE post_name = '{str(edition_post_author.post_name)}';")
            con.commit()

            if get_state(message.chat.id) == 16:
                cursor.execute(f"SELECT author_name, post_name, post_date, post_desc, what_needs, hashtags, "
                               f"pic_post, name_entities, desc_entities, date_entities, what_needs_entities, "
                               f"status, message_id FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")

                for author_name, post_name, post_date, post_desc, what_needs, hashtags, \
                    pic_post, name_entities, desc_entities, date_entities, \
                    what_needs_entities, status, message_id in cursor.fetchall():
                    edition_post_author.author_name = author_name
                    edition_post_author.post_name = post_name
                    edition_post_author.post_desc = post_desc
                    edition_post_author.post_date = post_date
                    edition_post_author.what_needs = what_needs
                    edition_post_author.hashtags = hashtags
                    edition_post_author.pic_post = pic_post
                    edition_post_author.name_entities = name_entities
                    edition_post_author.desc_entities = desc_entities
                    edition_post_author.date_entities = date_entities
                    edition_post_author.what_needs_entities = what_needs_entities
                    edition_post_author.status = status
                    edition_post_author.message_id = message_id

                if edition_post_author.status:
                    await edit_post(bot, message, edition_post_author, settings, 0)
                else:
                    pass

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить тему', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить требования')
                user_markup.row('Изменить баннер', 'Изменить хэштеги')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Дата события успешно изменена!',
                                       reply_markup=user_markup)
                await log(f'Date post {edition_post_author.post_name} is changed by {message.chat.id}')
                set_state(message.chat.id, 13)
            elif get_state(message.chat.id) == 160:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute(f"SELECT post_date, date_entities FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")
                for post_date, date_entities in cursor.fetchall():
                    creation_post_author.post_date = post_date
                    creation_post_author.date_entities = date_entities
                con.close()

                await preview(bot, message, creation_post_author, settings)

                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton(text='ДА', callback_data='Редактировать пост'),
                        InlineKeyboardButton(text='НЕТ', callback_data='Подтвердить пост'))
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                             callback_data='Вернуться в главное меню'))
                await bot.send_message(message.chat.id, 'Хотите ли редактировать пост?', reply_markup=key)
            con.close()

        elif get_state(message.chat.id) == 17 or get_state(message.chat.id) == 170:
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute(f"UPDATE posts SET what_needs = '{message.text}', what_needs_entities = '{str(message)}' "
                           f"WHERE post_name = '{str(edition_post_author.post_name)}';")
            con.commit()

            if get_state(message.chat.id) == 17:
                cursor.execute(f"SELECT author_name, post_name, post_date, post_desc, what_needs, hashtags, "
                               f"pic_post, name_entities, desc_entities, date_entities, what_needs_entities, "
                               f"status, message_id FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")

                for author_name, post_name, post_date, post_desc, what_needs, hashtags, \
                    pic_post, name_entities, desc_entities, date_entities, \
                    what_needs_entities, status, message_id in cursor.fetchall():
                    edition_post_author.author_name = author_name
                    edition_post_author.post_name = post_name
                    edition_post_author.post_desc = post_desc
                    edition_post_author.post_date = post_date
                    edition_post_author.what_needs = what_needs
                    edition_post_author.hashtags = hashtags
                    edition_post_author.pic_post = pic_post
                    edition_post_author.name_entities = name_entities
                    edition_post_author.desc_entities = desc_entities
                    edition_post_author.date_entities = date_entities
                    edition_post_author.what_needs_entities = what_needs_entities
                    edition_post_author.status = status
                    edition_post_author.message_id = message_id

                if edition_post_author.status:
                    await edit_post(bot, message, edition_post_author, settings, 0)
                else:
                    pass

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить тему', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить требования')
                user_markup.row('Изменить баннер', 'Изменить хэштеги')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Условия участия успешно изменены!', reply_markup=user_markup)
                await log(f'Requirements {edition_post_author.post_name} is changed by {message.chat.id}')
                set_state(message.chat.id, 13)
            elif get_state(message.chat.id) == 170:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute(f"SELECT what_needs, what_needs_entities FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")
                for what_needs, what_needs_entities in cursor.fetchall():
                    creation_post_author.what_needs = what_needs
                    creation_post_author.what_needs_entities = what_needs_entities
                con.close()

                await preview(bot, message, creation_post_author, settings)

                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton(text='ДА', callback_data='Редактировать пост'),
                        InlineKeyboardButton(text='НЕТ', callback_data='Подтвердить пост'))
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                             callback_data='Вернуться в главное меню'))
                await bot.send_message(message.chat.id, 'Хотите ли редактировать пост?', reply_markup=key)
            con.close()

        elif get_state(message.chat.id) == 18 or get_state(message.chat.id) == 180:
            '''download photo'''
            src = ''
            if message.text == '/empty':
                edition_post_author.pic_post = ''
            elif message.document:
                file_info = await bot.get_file(message.document.file_id)
                downloaded_file = await bot.download_file(file_info.file_path)

                src = f'data/media/posts_media/pic for post - {edition_post_author.post_name}.jpeg'
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file.getvalue())

                edition_post_author.pic_post = src
                await bot.send_message(message.chat.id, 'Изображение загружено.')
            elif message.photo:
                file_info = await bot.get_file(message.photo[-1].file_id)
                downloaded_file = await bot.download_file(file_info.file_path)

                src = f'data/media/posts_media/pic for post - {edition_post_author.post_name}.jpeg'
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file.getvalue())

                edition_post_author.pic_post = src
                await bot.send_message(message.chat.id, 'Изображение загружено.')

            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute(f"UPDATE posts SET pic_post = '{src}' "
                           f"WHERE post_name = '{str(edition_post_author.post_name)}';")
            con.commit()

            if get_state(message.chat.id) == 18:
                cursor.execute(f"SELECT author_name, post_name, post_date, post_desc, what_needs, hashtags, "
                               f"pic_post, name_entities, desc_entities, date_entities, what_needs_entities, "
                               f"status, message_id FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")

                for author_name, post_name, post_date, post_desc, what_needs, hashtags, \
                    pic_post, name_entities, desc_entities, date_entities, \
                    what_needs_entities, status, message_id in cursor.fetchall():
                    edition_post_author.author_name = author_name
                    edition_post_author.post_name = post_name
                    edition_post_author.post_desc = post_desc
                    edition_post_author.post_date = post_date
                    edition_post_author.what_needs = what_needs
                    edition_post_author.hashtags = hashtags
                    edition_post_author.pic_post = pic_post
                    edition_post_author.name_entities = name_entities
                    edition_post_author.desc_entities = desc_entities
                    edition_post_author.date_entities = date_entities
                    edition_post_author.what_needs_entities = what_needs_entities
                    edition_post_author.status = status
                    edition_post_author.message_id = message_id

                if edition_post_author.status:
                    await edit_post(bot, message, edition_post_author, settings, 1)
                else:
                    pass

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить тему', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить требования')
                user_markup.row('Изменить баннер', 'Изменить хэштеги')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Баннер поста успешно изменен!', reply_markup=user_markup)
                await log(f'Picture {edition_post_author.post_name} is changed by {message.chat.id}')
                set_state(message.chat.id, 13)
            elif get_state(message.chat.id) == 180:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute(f"SELECT pic_post FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")
                for pic_post in cursor.fetchall():
                    creation_post_author.pic_post = pic_post
                con.close()

                await preview(bot, message, creation_post_author, settings)

                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton(text='ДА', callback_data='Редактировать пост'),
                        InlineKeyboardButton(text='НЕТ', callback_data='Подтвердить пост'))
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                             callback_data='Вернуться в главное меню'))
                await bot.send_message(message.chat.id, 'Хотите ли редактировать пост?', reply_markup=key)
            con.close()

        elif get_state(message.chat.id) == 19 or get_state(message.chat.id) == 190:
            con = sqlite3.connect(files.main_db)
            cursor = con.cursor()
            cursor.execute(f"UPDATE posts SET hashtags = '{message.text}' "
                           f"WHERE post_name = '{str(edition_post_author.post_name)}';")
            con.commit()

            if get_state(message.chat.id) == 19:
                cursor.execute(f"SELECT author_name, post_name, post_date, post_desc, what_needs, hashtags, "
                               f"pic_post, name_entities, desc_entities, date_entities, what_needs_entities, "
                               f"status, message_id FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")

                for author_name, post_name, post_date, post_desc, what_needs, hashtags, \
                    pic_post, name_entities, desc_entities, date_entities, \
                    what_needs_entities, status, message_id in cursor.fetchall():
                    edition_post_author.author_name = author_name
                    edition_post_author.post_name = post_name
                    edition_post_author.post_desc = post_desc
                    edition_post_author.post_date = post_date
                    edition_post_author.what_needs = what_needs
                    edition_post_author.hashtags = hashtags
                    edition_post_author.pic_post = pic_post
                    edition_post_author.name_entities = name_entities
                    edition_post_author.desc_entities = desc_entities
                    edition_post_author.date_entities = date_entities
                    edition_post_author.what_needs_entities = what_needs_entities
                    edition_post_author.status = status
                    edition_post_author.message_id = message_id

                if edition_post_author.status:
                    await edit_post(bot, message, edition_post_author, settings, 0)
                else:
                    pass

                user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                user_markup.row('Изменить тему', 'Изменить описание')
                user_markup.row('Изменить дату', 'Изменить требования')
                user_markup.row('Изменить баннер', 'Изменить хэштеги')
                user_markup.row('Вернуться в главное меню')
                await bot.send_message(message.chat.id, 'Хэштеги успешно изменены!', reply_markup=user_markup)
                await log(f'Hashtags {edition_post_author.post_name} is changed by {message.chat.id}')
                set_state(message.chat.id, 13)
            elif get_state(message.chat.id) == 190:
                con = sqlite3.connect(files.main_db)
                cursor = con.cursor()
                cursor.execute(f"SELECT hashtags FROM posts "
                               f"WHERE post_name = '{str(edition_post_author.post_name)}';")
                for hashtags in cursor.fetchall():
                    creation_post_author.hashtags = hashtags[0]
                con.close()

                await preview(bot, message, creation_post_author, settings)

                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton(text='ДА', callback_data='Редактировать пост'),
                        InlineKeyboardButton(text='НЕТ', callback_data='Подтвердить пост'))
                key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                             callback_data='Вернуться в главное меню'))
                await bot.send_message(message.chat.id, 'Хотите ли редактировать пост?', reply_markup=key)
            con.close()


async def author_inline(bot, callback_data, chat_id, message_id, settings):
    if callback_data == 'Вернуться в главное меню':
        if get_state(chat_id):
            delete_state(chat_id)
        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('Посты')
        user_markup.row('Списки')

        await bot.delete_message(chat_id, message_id)  # удаляется старое сообщение
        await bot.send_message(chat_id, 'Вы в главном меню бота.',
                               reply_markup=user_markup)

    elif callback_data == 'Есть дата проведения':
        await bot.delete_message(chat_id, message_id)
        key = InlineKeyboardMarkup()
        key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                     callback_data='Вернуться в главное меню'))
        await bot.send_message(chat_id, 'Введите дату проведения события или дедлайн', reply_markup=key)

        set_state(chat_id, 3)

    elif callback_data == 'Нет даты проведения':
        await bot.delete_message(chat_id, message_id)
        creation_post_author.post_date = ''
        key = InlineKeyboardMarkup()
        key.row(InlineKeyboardButton(text='ДА', callback_data='Есть требования'),
                InlineKeyboardButton(text='НЕТ', callback_data='Нет требований'))
        key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                     callback_data='Вернуться в главное меню'))
        await bot.send_message(chat_id, 'Нужно ли что-то сделать для участия?', reply_markup=key)

    elif callback_data == 'Есть требования':
        await bot.delete_message(chat_id, message_id)
        key = InlineKeyboardMarkup()
        key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                     callback_data='Вернуться в главное меню'))
        await bot.send_message(chat_id, 'Введите что нужно сделать для участия', reply_markup=key)

        set_state(chat_id, 4)

    elif callback_data == 'Нет требований':
        await bot.delete_message(chat_id, message_id)
        creation_post_author.what_needs = ''
        key = InlineKeyboardMarkup()
        key.add(InlineKeyboardButton(text='Отменить и вернуться в главное меню',
                                     callback_data='Вернуться в главное меню'))
        await bot.send_message(chat_id, 'Вставьте баннер (изображение) поста.'
                                        'Или если нет баннера, то пропишите /empty', reply_markup=key)

        set_state(chat_id, 5)

    elif callback_data == 'Редактировать пост':
        edition_post_author.post_name = creation_post_author.post_name

        await bot.delete_message(chat_id, message_id)

        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('Изменить тему', 'Изменить описание')
        user_markup.row('Изменить дату', 'Изменить требования')
        user_markup.row('Изменить баннер', 'Изменить хэштеги')
        user_markup.row('Вернуться в главное меню')
        await bot.send_message(chat_id, 'Теперь выберите, что хотите изменить',
                               reply_markup=user_markup)
        set_state(chat_id, 130)

    elif callback_data == 'Подтвердить пост':
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, "В качестве подтверждения размещения поста сейчас напишите 'Да'. "
                                        "Если не хотите размещать пост сейчас - напишите что-нибудь другое")
        set_state(chat_id, 7)

    elif callback_data == 'Разместить пост':
        await bot.delete_message(chat_id, message_id)
        entity_list = []
        if unposted_post_author.post_date == '':
            unposted_post_author.post_date = 'Нет даты проведения'
        if unposted_post_author.what_needs == '':
            unposted_post_author.what_needs = 'Нет требований'
        name_entities = json.loads(str(unposted_post_author.name_entities))
        description_entities = json.loads(str(unposted_post_author.desc_entities))
        date_entities = json.loads(str(unposted_post_author.date_entities))
        what_needs_entities = json.loads(str(unposted_post_author.what_needs_entities))
        footer_text_entities = json.loads(settings.footer_text_entities)
        text = f'{unposted_post_author.post_name}\n\n' \
               f'{unposted_post_author.post_desc}\n\n' \
               f'✅ {unposted_post_author.what_needs}\n\n' \
               f'📆 {unposted_post_author.post_date}\n\n' \
               f'{unposted_post_author.hashtags}\n\n' \
               f'Автор: @{unposted_post_author.author_name}\n' \
               f'{settings.footer_text}'
        count_string_track = 0

        entity = MessageEntity(type="bold",
                               offset=count_string_track,
                               length=len(unposted_post_author.post_name))
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

        count_string_track += len(str(unposted_post_author.post_name)) + 2

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

        count_string_track += len(str(unposted_post_author.post_desc)) + len(str('\n\n✅ '))

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

        count_string_track += len(str(unposted_post_author.what_needs)) + len(str('\n\n📆 '))

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

        count_string_track += len(str(unposted_post_author.post_date)) + 2 + \
                              len(str(unposted_post_author.hashtags)) + 3

        entity = MessageEntity(type="italic",
                               offset=count_string_track,
                               length=len('Автор'))
        entity_list.append(entity)

        count_string_track += len(f'Автор: @{unposted_post_author.author_name}\n')

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

        if type(creation_post_author.pic_post) is tuple:
            if creation_post_author.pic_post[0] == '':
                message_result = await bot.send_message(settings.channel_name, text, entities=entity_list)
            else:
                photo = open(creation_post_author.pic_post[0], 'rb')
                message_result = await bot.send_photo(settings.channel_name,
                                                      photo, caption=text, caption_entities=entity_list)
        else:
            if creation_post_author.pic_post == '':
                message_result = await bot.send_message(settings.channel_name, text, entities=entity_list)
            else:
                photo = open(creation_post_author.pic_post, 'rb')
                message_result = await bot.send_photo(settings.channel_name,
                                                      photo, caption=text, caption_entities=entity_list)

        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('Посты')
        user_markup.row('Списки')

        await bot.send_message(chat_id, 'Пост был размещен на канале.', reply_markup=user_markup)

        con = sqlite3.connect(files.main_db)
        cursor = con.cursor()
        cursor.execute(f"UPDATE posts SET status = 1, message_id = {str(message_result.message_id)} "
                       f"WHERE post_name = '{str(unposted_post_author.post_name)}';")
        con.commit()
        con.close()

        delete_state(chat_id)

    elif callback_data == 'Вернуться в меню размещения':
        await bot.delete_message(chat_id, message_id)
        con = sqlite3.connect(files.main_db)
        cursor = con.cursor()
        cursor.execute(f"SELECT post_name, status FROM posts WHERE author_id = {chat_id};")
        user_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        a = 0
        for post_name, status in cursor.fetchall():
            if status:
                pass
            else:
                a += 1
                user_markup.row(str(post_name))
        if a == 0:
            await bot.send_message(chat_id, 'Не размещенных постов нет!', reply_markup=user_markup)
        else:
            user_markup.row('Вернуться в главное меню')
            await bot.send_message(chat_id, 'Какой пост хотите разместить?',
                                   parse_mode='Markdown', reply_markup=user_markup)
            set_state(chat_id, 9)
        con.close()
