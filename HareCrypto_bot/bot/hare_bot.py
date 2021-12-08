import asyncio
import logging
import sqlite3
from datetime import datetime
import aioschedule  # библиотека для выставления заданий по расписанию

# подключаем библиотеку для работы с API телеграм бота
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity

# подключение функций из сторонних файлов
from admin_panel import admin_panel, in_admin_panel, admin_inline, first_launch
from config import admin_id
# подключение функций из сторонних файлов
from defs import get_admin_list, log, user_logger, get_moder_list, chat_logger, hot_notification, page_output
from extensions import Token, Event_List, Message_Mem, check_repeated_message, Page_Mem
import files
from mod_panel import moder_panel, in_moder_panel, moder_inline

dateFormatter = "%d.%m.%Y %H:%M"

# объекты классов для работы с сообщениями по командам start, help, event
last_message_start = Message_Mem()
last_message_help = Message_Mem()
last_message_event = Message_Mem()
# объект класса для работы с постраничным выводом
last_page = Page_Mem()

# log
logging.basicConfig(level=logging.INFO)

# настройка и инициализация бота
with Token() as tg_token:
    bot = Bot(token=tg_token)
dp = Dispatcher(bot)


# обработчик команды start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if message.chat.type == 'private':
        user_logger(message.chat.id)
        await bot.send_message(message.chat.id, f"Привет, {message.chat.username}!\n",
                               reply_markup=ReplyKeyboardRemove())
        add_bot_ingroup = InlineKeyboardMarkup()
        add_bot_ingroup.add(InlineKeyboardButton('Добавить бота в группу',
                                                 url='http://t.me/HareCrypta_bot?startgroup=botstart'))
        await bot.send_message(message.chat.id, "Я HareCrypta-бот!\nМожешь использовать меня для слежения "
                                                "за событиями в криптосообществах!\n"
                                                "По команде /help можно получить "
                                                "дополнительную информацию", reply_markup=add_bot_ingroup)
        await log(f'User {message.chat.id} started bot')
    else:
        await check_repeated_message(bot, message, last_message_start)

        user_logger(message.from_user.id)
        try:
            chat_logger(message.chat.id, message.chat.title, message.chat.username)
        except:
            chat_logger(message.chat.id, message.chat.title)
        await bot.send_message(message.chat.id, "Привет всем!\n"
                                                "Я HareCrypta-бот!\nМожете использовать меня для слежения "
                                                "за событиями в криптосообществах!\n"
                                                "По команде /help можно получить "
                                                "дополнительную информацию",
                               reply_markup=ReplyKeyboardRemove())
        await log(f'Member {message.from_user.id} from the group {message.chat.id} started bot')


# обработчик команды help
@dp.message_handler(commands=['help'])
async def process_start_command(message: types.Message):
    await check_repeated_message(bot, message, last_message_help)

    if message.chat.type == 'private':
        user_logger(message.chat.id)
        await bot.send_message(message.chat.id, "Я HareCrypto-бот!\n"
                                                "Можете использовать меня для слежения за событиями на крипторынке, "
                                                "такие как NFT минты, ICO, краудлоны и многое другое. \n"
                                                "По команде /event можно получить информацию о календаре событий.\n\n"
                                                "В этом канале https://t.me/harecrypt\n"
                                                "•Чат✍️:  https://t.me/harecrypta_chat - чат гемов-людей\n"
                                                "•Канал✍️: https://t.me/HareCrypta_lab_ann - Лаборатория идей.\n"
                                                "•YouTube: https://www.youtube.com/c/HareCrypta\n"
                                                "•Inst: https://instagram.com/harecrypta - инста\n")
    else:
        user_logger(message.from_user.id)
        try:
            chat_logger(message.chat.id, message.chat.title, message.chat.username)
        except:
            chat_logger(message.chat.id, message.chat.title)

        await bot.send_message(message.chat.id, "Я HareCrypto-бот!\n"
                                                "Можете использовать меня для слежения за событиями на крипторынке, "
                                                "такие как NFT минты, ICO, краудлоны и многое другое.\n"
                                                "По команде /event можно получить информацию о календаре событий.\n\n"
                                                "В этом канале https://t.me/harecrypt\n"
                                                "•Чат✍️:  https://t.me/harecrypta_chat - чат гемов-людей\n"
                                                "•Канал✍️: https://t.me/HareCrypta_lab_ann - Лаборатория идей.\n"
                                                "•YouTube: https://www.youtube.com/c/HareCrypta\n"
                                                "•Inst: https://instagram.com/harecrypta - инста\n")


# обработчик команды event
# вывод списка событий постранично
@dp.message_handler(commands=["event"])
async def event_handler(message: types.Message):
    await check_repeated_message(bot, message, last_message_event)

    events, entity_list, inline_paginator = await page_output(message, last_page, 1)

    await bot.send_message(message.chat.id, events, entities=entity_list, reply_markup=inline_paginator)

    if message.chat.type == 'private':
        await log(f'User {message.chat.id} requested events list')
    else:
        await log(f'Member {message.from_user.id} from the group {message.chat.id} requested events list')


# обработчик команды adm
# вход в панель администратора
@dp.message_handler(commands=["adm"])
async def admin_handler(message: types.Message):
    if message.chat.type == 'private':
        user_logger(message.chat.id)
        if message.chat.id == admin_id and await first_launch(bot, message.chat.id) is True:
            await bot.send_message(message.chat.id, "Теперь вы Админ!")
            await log(f'User {message.chat.id} successfully requested admin panel')
        elif (message.chat.id == admin_id or message.chat.id in get_admin_list()) and \
                await first_launch(bot, message.chat.id) is False:
            await bot.send_message(message.chat.id, "Привет, Админ!")
            await log(f'User {message.chat.id} successfully requested admin panel')
            await admin_panel(bot, message.chat.id)
        else:
            await bot.send_message(message.chat.id, "Вы не Админ!")
            await log(f'User {message.chat.id} unsuccessfully requested admin panel')
    else:
        user_logger(message.from_user.id)
        try:
            chat_logger(message.chat.id, message.chat.title, message.chat.username)
        except:
            chat_logger(message.chat.id, message.chat.title)
        await bot.send_message(message.chat.id, "🤨")
        await log(f'Member {message.from_user.id} from the group {message.chat.id} requested admin panel')


# обработчик команды mod
# вход в панель модератора
# (по сравнению с админом, функционал подрезан до создания, удаления и редактирования событий)
@dp.message_handler(commands=["mod"])
async def moder_handler(message: types.Message):
    if message.chat.type == 'private':
        user_logger(message.chat.id)
        if message.chat.id in get_moder_list():
            await bot.send_message(message.chat.id, "Привет, Модератор!")
            await log(f'User {message.chat.id} successfully requested moderator panel')
            await moder_panel(bot, message.chat.id)
        else:
            await bot.send_message(message.chat.id, "Вы не Модератор!")
            await log(f'User {message.chat.id} unsuccessfully requested moderator panel')
    else:
        user_logger(message.from_user.id)
        try:
            chat_logger(message.chat.id, message.chat.title, message.chat.username)
        except:
            chat_logger(message.chat.id, message.chat.title)
        await bot.send_message(message.chat.id, "🤨")
        await log(f'Member {message.from_user.id} from the group {message.chat.id} requested admin panel')


# обработчик входных данных из сообщений
# вход в админ панель
# вход в мод панель
@dp.message_handler(content_types=["text"])
async def actions_handler(message: types.Message):
    if message.chat.type == 'private':
        if message.chat.id == admin_id or message.chat.id in get_admin_list():
            await in_admin_panel(bot, message.chat.id, message)
        elif message.chat.id in get_moder_list():
            await in_moder_panel(bot, message.chat.id, message)
    else:
        pass


# обработчик инлайн событий DELETE
@dp.inline_handler(lambda query: len(query.query) > 0)
async def query_text(query):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="test"))
    results = []
    single_msg = types.InlineQueryResultArticle(
        id="1", title="Press me",
        input_message_content=types.InputTextMessageContent(message_text="Я – сообщение из инлайн-режима"),
        reply_markup=kb
    )
    results.append(single_msg)
    await bot.answer_inline_query(query.id, results)


# обработчик коллбэков от инлайн кнопок
@dp.callback_query_handler(lambda c: True)
async def callback(callback_query: types.CallbackQuery):
    if callback_query.message:
        if callback_query.message.chat.type == 'private':
            if callback_query.message.chat.id in get_admin_list():
                await admin_inline(bot, callback_query.data, callback_query.message.chat.id,
                                   callback_query.message.message_id)
            elif callback_query.message.chat.id in get_moder_list():
                await moder_inline(bot, callback_query.data, callback_query.message.chat.id,
                                   callback_query.message.message_id)

            if callback_query.data == "forward":
                page_num = last_page.last_page[callback_query.message.message_id - 1] + 1

                if callback_query.message.message_id - 1 in last_page.last_page.keys() and page_num != 7:
                    last_page.last_page[callback_query.message.message_id - 1] += 1
                    page_num = last_page.last_page[callback_query.message.message_id-1]

                    events, entity_list, inline_paginator = \
                        await page_output(callback_query.message, last_page, page_num)

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                text=events, entities=entity_list, reply_markup=inline_paginator)
                elif callback_query.message.message_id-1 in last_page.last_page.keys() and page_num == 7:
                    last_page.last_page[callback_query.message.message_id - 1] = 1
                    page_num = last_page.last_page[callback_query.message.message_id - 1]

                    events, entity_list, inline_paginator = \
                        await page_output(callback_query.message, last_page, page_num)

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                text=events, entities=entity_list, reply_markup=inline_paginator)

            if callback_query.data == "backward":
                page_num = last_page.last_page[callback_query.message.message_id-1] - 1

                if callback_query.message.message_id - 1 in last_page.last_page.keys() and page_num != 0:
                    last_page.last_page[callback_query.message.message_id - 1] -= 1
                    page_num = last_page.last_page[callback_query.message.message_id - 1]

                    events, entity_list, inline_paginator = \
                        await page_output(callback_query.message, last_page, page_num)

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                text=events, entities=entity_list, reply_markup=inline_paginator)
                elif callback_query.message.message_id - 1 in last_page.last_page.keys() and page_num == 0:
                    last_page.last_page[callback_query.message.message_id - 1] = 6
                    page_num = last_page.last_page[callback_query.message.message_id - 1]

                    events, entity_list, inline_paginator = \
                        await page_output(callback_query.message, last_page, page_num)

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                text=events, entities=entity_list, reply_markup=inline_paginator)

            await bot.answer_callback_query(callback_query.id)

        else:
            if callback_query.data == "forward":
                page_num = last_page.last_page[callback_query.message.message_id - 1] + 1

                if callback_query.message.message_id - 1 in last_page.last_page.keys() and page_num != 7:
                    last_page.last_page[callback_query.message.message_id - 1] += 1
                    page_num = last_page.last_page[callback_query.message.message_id - 1]

                    events, entity_list, inline_paginator = \
                        await page_output(callback_query.message, last_page, page_num)

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                text=events, entities=entity_list, reply_markup=inline_paginator)
                elif callback_query.message.message_id - 1 in last_page.last_page.keys() and page_num == 7:
                    last_page.last_page[callback_query.message.message_id - 1] = 1
                    page_num = last_page.last_page[callback_query.message.message_id - 1]

                    events, entity_list, inline_paginator = \
                        await page_output(callback_query.message, last_page, page_num)

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                text=events, entities=entity_list, reply_markup=inline_paginator)

            if callback_query.data == "backward":
                page_num = last_page.last_page[callback_query.message.message_id - 1] - 1

                if callback_query.message.message_id - 1 in last_page.last_page.keys() and page_num != 0:
                    last_page.last_page[callback_query.message.message_id - 1] -= 1
                    page_num = last_page.last_page[callback_query.message.message_id - 1]

                    events, entity_list, inline_paginator = \
                        await page_output(callback_query.message, last_page, page_num)

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                text=events, entities=entity_list, reply_markup=inline_paginator)
                elif callback_query.message.message_id - 1 in last_page.last_page.keys() and page_num == 0:
                    last_page.last_page[callback_query.message.message_id - 1] = 6
                    page_num = last_page.last_page[callback_query.message.message_id - 1]

                    events, entity_list, inline_paginator = \
                        await page_output(callback_query.message, last_page, page_num)

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                text=events, entities=entity_list, reply_markup=inline_paginator)

            await bot.answer_callback_query(callback_query.id)

    elif callback_query.inline_message_id:
        if callback_query.data == "test":
            await bot.edit_message_text(inline_message_id=callback_query.inline_message_id,
                                        text="INLINE MODE")


# проверка и удаление старых событий
async def check_old_events():
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    events_list = Event_List()

    try:
        cursor.execute("SELECT name, description, date, name_entities, description_entities, "
                       "type_event FROM events;")
    except:
        cursor.execute("CREATE TABLE events (id INT, name TEXT, "
                       "description TEXT, date DATETIME, name_entities JSON, description_entities JSON, "
                       "type_event TEXT);")
    else:
        now = datetime.now()

        for name, description, date, name_entities, description_entities, type_event in cursor.fetchall():
            if date == 'TBA':
                events_list.events_unsorted.update({(name, description, date, name_entities,
                                                     description_entities, type_event): 'TBA'})
            else:
                date_formatted = datetime.strptime(date, "%d.%m.%Y %H:%M")
                delta = date_formatted - now
                delta = divmod(delta.total_seconds(), 3600)
                events_list.events_unsorted.update({(name, description, date, name_entities,
                                                     description_entities, type_event): int(delta[0])})

        for events_key, events_value in events_list.events_unsorted.items():
            name = events_key[0]

            if events_value == 'TBA':
                continue
            if events_value < -336:
                cursor.execute("DELETE FROM events WHERE name = " + "'" + str(name) + "';")
                con.commit()

        con.close()


# проверка приближающихся событий (каждую минуту проверяется, остается ли 59 минут до события)
async def check_hot_events():
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()

    try:
        cursor.execute("SELECT name, description, date, name_entities, description_entities, "
                       "type_event FROM events;")
    except:
        cursor.execute("CREATE TABLE events (id INT, name TEXT, "
                       "description TEXT, date DATETIME, name_entities JSON, description_entities JSON, "
                       "type_event TEXT);")
    else:
        now = datetime.now()

        for name, description, date, name_entities, description_entities, type_event in cursor.fetchall():
            if date == 'TBA':
                continue
            else:
                date_formatted = datetime.strptime(date, "%d.%m.%Y %H:%M")
                delta = date_formatted - now
                delta = divmod(delta.total_seconds(), 60)
                event = (name, description, date, name_entities, description_entities, type_event)
                if delta[0] == 59:
                    await hot_notification(bot, event)

        con.close()


# расписание задач
async def scheduler():
    aioschedule.every().day.at("00:00").do(check_old_events)
    aioschedule.every(1).minutes.do(check_hot_events)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)


# функция при запуске боте
async def on_startup(_):
    asyncio.create_task(scheduler())


# входная точка программы
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
