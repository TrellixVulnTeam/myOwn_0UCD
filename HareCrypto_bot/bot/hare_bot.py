import asyncio
import logging
import sqlite3
from datetime import datetime
import aioschedule

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity
from aiogram.utils.json import json

from admin_panel import admin_panel, in_admin_panel, admin_inline, first_launch
from config import admin_id

from defs import get_admin_list, log, user_logger, get_moder_list
from extensions import Token, Event, Event_List, Message_Mem, check_repeated_message
import files
from mod_panel import moder_panel, in_moder_panel, moder_inline

dateFormatter = "%d.%m.%Y %H:%M"

last_message_start = Message_Mem()
last_message_help = Message_Mem()
last_message_event = Message_Mem()

# log
logging.basicConfig(level=logging.INFO)

with Token() as tg_token:
    bot = Bot(token=tg_token)
dp = Dispatcher(bot)


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
        await bot.send_message(message.chat.id, "Привет всем!\n"
                                                "Я HareCrypta-бот!\nМожете использовать меня для слежения "
                                                "за событиями в криптосообществах!\n"
                                                "По команде /help можно получить "
                                                "дополнительную информацию",
                               reply_markup=ReplyKeyboardRemove())
        await log(f'Member {message.from_user.id} from the group {message.chat.id} started bot')


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
        await bot.send_message(message.chat.id, "Я HareCrypto-бот!\n"
                                                "Можете использовать меня для слежения за событиями на крипторынке, "
                                                "такие как NFT минты, ICO, краудлоны и многое другое.\n"
                                                "По команде /event можно получить информацию о календаре событий.\n\n"
                                                "В этом канале https://t.me/harecrypt\n"
                                                "•Чат✍️:  https://t.me/harecrypta_chat - чат гемов-людей\n"
                                                "•Канал✍️: https://t.me/HareCrypta_lab_ann - Лаборатория идей.\n"
                                                "•YouTube: https://www.youtube.com/c/HareCrypta\n"
                                                "•Inst: https://instagram.com/harecrypta - инста\n")


# @dp.message_handler(content_types=["new_chat_members"])
# async def on_user_joined(message: types.Message):
#     await message.delete()


@dp.message_handler(commands=["event"])
async def event_handler(message: types.Message):
    await check_repeated_message(bot, message, last_message_event)

    events_list = Event_List()
    entity_list = []
    count_string_track = 0

    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    events = ''
    a = 0
    try:
        cursor.execute("SELECT name, description, date, name_entities, description_entities FROM events;")
    except:
        cursor.execute("CREATE TABLE events (id INT, name TEXT, "
                       "description TEXT, date DATETIME, name_entities JSON, description_entities JSON);")
    else:
        now = datetime.now()

        for name, description, date, name_entities, description_entities in cursor.fetchall():
            a += 1
            if date == 'TBA':
                events_list.events_unsorted.update({(name, description, date, name_entities,
                                                     description_entities): 'TBA'})
            else:
                date_formatted = datetime.strptime(date, "%d.%m.%Y %H:%M")
                delta = date_formatted - now
                delta = divmod(delta.total_seconds(), 3600)
                events_list.events_unsorted.update({(name, description, date, name_entities,
                                                     description_entities): int(delta[0])})

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

        events += "\n🔵Предстоящие события:\n"  # 23
        num_event = 1
        count_string_track += len("\n🔵Предстоящие события:\n") + 1

        for upcom_events in events_list.events_types_pair[3][1]:
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

        events += "\nСобытия без анонса:\n"  # 21
        num_event = 1
        count_string_track += len("\nСобытия без анонса:\n") + 0

        for tba_events in events_list.events_TBA:
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

    if a == 0:
        events = "События ещё не созданы!"
    else:
        pass

    await bot.send_message(message.chat.id, events, entities=entity_list)

    if message.chat.type == 'private':
        await log(f'{message.chat.id} requested events list')
    else:
        await log(f'Member {message.from_user.id} from the group {message.chat.id} requested events list')


@dp.message_handler(commands=["adm"])
async def admin_handler(message: types.Message):
    if message.chat.type == 'private':
        user_logger(message.chat.id)
        if message.chat.id == admin_id and await first_launch(bot, message.chat.id) is True:
            await bot.send_message(message.chat.id, "Теперь вы Админ!")
        elif (message.chat.id == admin_id or message.chat.id in get_admin_list()) and \
                await first_launch(bot, message.chat.id) is False:
            await bot.send_message(message.chat.id, "Привет, Админ!")
            await admin_panel(bot, message.chat.id)
        else:
            await bot.send_message(message.chat.id, "Вы не Админ!")
            await log(f'{message.chat.id} requested admin panel')
    else:
        user_logger(message.from_user.id)
        await bot.send_message(message.chat.id, "🤨")
        await log(f'Member {message.from_user.id} from the group {message.chat.id} requested admin panel')


@dp.message_handler(commands=["mod"])
async def moder_handler(message: types.Message):
    if message.chat.type == 'private':
        user_logger(message.chat.id)
        if message.chat.id in get_moder_list():
            await bot.send_message(message.chat.id, "Привет, Модератор!")
            await moder_panel(bot, message.chat.id)
        else:
            await bot.send_message(message.chat.id, "Вы не Модератор!")
            await log(f'{message.chat.id} requested moderator panel')
    else:
        user_logger(message.from_user.id)
        await bot.send_message(message.chat.id, "🤨")
        await log(f'Member {message.from_user.id} from the group {message.chat.id} requested admin panel')


@dp.message_handler()
async def actions_handler(message: types.Message):
    if message.chat.id == admin_id or message.chat.id in get_admin_list():
        await in_admin_panel(bot, message.chat.id, message)
    elif message.chat.id in get_moder_list():
        await in_moder_panel(bot, message.chat.id, message)


@dp.callback_query_handler(lambda c: True)
async def inline(callback_query: types.CallbackQuery):
    if callback_query.message.chat.id in get_admin_list():
        await bot.answer_callback_query(callback_query.id)
        await admin_inline(bot, callback_query.data, callback_query.message.chat.id, callback_query.message.message_id)
    if callback_query.message.chat.id in get_moder_list():
        await bot.answer_callback_query(callback_query.id)
        await moder_inline(bot, callback_query.data, callback_query.message.chat.id, callback_query.message.message_id)


async def check_old_events():
    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    events_list = Event_List()

    try:
        cursor.execute("SELECT name, description, date, name_entities, description_entities FROM events;")
    except:
        cursor.execute("CREATE TABLE events (id INT, name TEXT, "
                       "description TEXT, date DATETIME, name_entities JSON, description_entities JSON);")
    else:
        now = datetime.now()

        for name, description, date, name_entities, description_entities in cursor.fetchall():
            if date == 'TBA':
                events_list.events_unsorted.update({(name, description, date, name_entities,
                                                     description_entities): 'TBA'})
            else:
                date_formatted = datetime.strptime(date, "%d.%m.%Y %H:%M")
                delta = date_formatted - now
                delta = divmod(delta.total_seconds(), 3600)
                events_list.events_unsorted.update({(name, description, date, name_entities,
                                                     description_entities): int(delta[0])})

        for events_key, events_value in events_list.events_unsorted.items():
            name = events_key[0]

            if events_value == 'TBA':
                continue
            if events_value < -336:
                cursor.execute("DELETE FROM events WHERE name = " + "'" + str(name) + "';")
                con.commit()

        con.close()


async def scheduler():
    aioschedule.every().day.at("00:00").do(check_old_events)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(60)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
