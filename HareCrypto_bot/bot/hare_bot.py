import logging
import sqlite3
from datetime import datetime
import pytz

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from bot import config
from bot.admin_panel import first_launch, admin_panel, get_adminlist, in_admin_panel, admin_inline, log, user_logger
from extensions import Token, Event, Event_List
import files

dateFormatter = "%d.%m.%Y %H:%M"

# log
logging.basicConfig(level=logging.INFO)

with Token() as tg_token:
    bot = Bot(token=tg_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if message.chat.type == 'private':
        user_logger(message.chat.id)
        await bot.send_message(message.chat.id, f"Привет, {message.chat.username}!\n", reply_markup=ReplyKeyboardRemove())
        add_bot_ingroup = InlineKeyboardMarkup()
        add_bot_ingroup.add(InlineKeyboardButton('Добавить бота в группу',
                                                 url='http://t.me/telepuzikbot_bot?startgroup=botstart'))
        await bot.send_message(message.chat.id, "Я HareCrypto-бот!\nМожешь использовать меня для слежения "
                                                "за событиями в криптосообществах!\n"
                                                "По команде /help можно получить "
                                                "дополнительную информацию", reply_markup=add_bot_ingroup)
        await log(f'User {message.chat.id} started bot')
    elif message.chat.type == 'group':
        user_logger(message.from_user.id)
        await bot.send_message(message.chat.id, "Привет всем!\n"
                                                "Я HareCrypto-бот!\nМожете использовать меня для слежения "
                                                "за событиями в криптосообществах!\n"
                                                "По команде /help можно получить "
                                                "дополнительную информацию",
                               reply_markup=ReplyKeyboardRemove())
        await log(f'Member {message.from_user.id} from the group {message.chat.id} started bot')


@dp.message_handler(commands=['help'])
async def process_start_command(message: types.Message):
    if message.chat.type == 'private':
        user_logger(message.chat.id)
        await bot.send_message(message.chat.id, "Я HareCrypto-бот!\nМеня можно использовать "
                                                "для слежения за событиями в криптосообществах.\n"
                                                "По команде /event можно получить информацию о календаре событий.")
    elif message.chat.type == 'group':
        user_logger(message.from_user.id)
        await bot.send_message(message.chat.id, "Я HareCrypto-бот!\n"
                                                "Можете использовать меня для слежения "
                                                "за событиями в криптосообществах.\n"
                                                "По команде /event можно получить информацию о календаре событий.")


# @dp.message_handler(content_types=["new_chat_members"])
# async def on_user_joined(message: types.Message):
#     await message.delete()


@dp.message_handler(commands=["event"])
async def event_handler(message: types.Message):
    events_list = Event_List()

    con = sqlite3.connect(files.main_db)
    cursor = con.cursor()
    events = ''
    a = 0
    try:
        cursor.execute("SELECT name, description, date FROM events;")
    except:
        cursor.execute("CREATE TABLE events (id INT, name TEXT, "
                       "description TEXT, date DATETIME);")
    else:
        msk = pytz.timezone('Europe/Moscow')
        now = datetime.now()

        for name, description, date in cursor.fetchall():
            a += 1
            if date == 'TBA':
                events_list.events_unsorted.update({(name, description, date): 'TBA'})
            else:
                date_formatted = datetime.strptime(date, "%d.%m.%Y %H:%M")
                delta = date_formatted - now
                delta = divmod(delta.total_seconds(), 3600)
                events_list.events_unsorted.update({(name, description, date): delta[0]})

        con.close()

        for events_key, events_value in events_list.events_unsorted.items():
            if events_value == 'TBA':
                events_list.events_TBA.append(events_key)
                continue
            if -3 <= events_value <= 23:
                if -3 <= events_value <= 1:
                    events_list.events_HOT.append(events_key)
                    events_list.events_TODAY.append(events_key)
                else:
                    events_list.events_TODAY.append(events_key)
                continue
            if -23 <= events_value < -3:
                events_list.events_PREVIOUS.append(events_key)
                continue
            if events_value > 23:
                events_list.events_UPCOMING.append(events_key)
                continue

        events += "🔴Предыдущие события:\n"
        num_event = 1
        for prev_events in events_list.events_PREVIOUS:
            events += str(num_event) + '. ' + prev_events[0] + \
                      ' - ' + prev_events[2] + ' МСК - ' + prev_events[1] + '\n '
            num_event += 1

        events += "\n🟢Сегодняшние события:\n"
        num_event = 1
        for today_events in events_list.events_TODAY:
            if today_events in events_list.events_HOT:
                events += str(num_event) + '. ' + ' 🔥 ' + today_events[0] + \
                          ' - ' + today_events[2] + ' МСК - ' + today_events[1] + '\n'
            else:
                events += str(num_event) + '. ' + today_events[0] + \
                          ' - ' + today_events[2] + ' МСК - ' + today_events[1] + '\n'
                num_event += 1

        events += "\n🔵Предстоящие события:\n"
        num_event = 1
        for upcom_events in events_list.events_UPCOMING:
            events += str(num_event) + '. ' + upcom_events[0] + \
                      ' - ' + upcom_events[2] + ' МСК - ' + upcom_events[1] + '\n'
            num_event += 1

        events += "\nСобытия без анонса:\n"
        num_event = 1
        for tba_events in events_list.events_TBA:
            events += str(num_event) + '. ' + tba_events[0] + \
                      ' - ' + tba_events[2] + ' МСК - ' + tba_events[1] + '\n'
            num_event += 1

    if a == 0:
        events = "События ещё не созданы!"
    else:
        pass
    await bot.send_message(message.chat.id, events, parse_mode='Markdown')
    if message.chat.type == 'private':
        await log(f'{message.chat.id} requested events list')
    elif message.chat.type == 'group':
        await log(f'Member {message.from_user.id} from the group {message.chat.id} requested events list')


@dp.message_handler(commands=["adm"])
async def admin_handler(message: types.Message):
    if message.chat.type == 'private':
        user_logger(message.chat.id)
        if message.chat.id == config.admin_id and await first_launch(bot, message.chat.id) is True:
            await bot.send_message(message.chat.id, "Теперь вы Админ!")
        elif (message.chat.id == config.admin_id or message.chat.id in get_adminlist()) and \
                await first_launch(bot, message.chat.id) is False:
            await bot.send_message(message.chat.id, "Привет, Админ!")
            await admin_panel(bot, message.chat.id)
        else:
            await bot.send_message(message.chat.id, "Вы не Админ!")
            await log(f'{message.chat.id} requested admin panel')
    elif message.chat.type == 'group':
        user_logger(message.from_user.id)
        await bot.send_message(message.chat.id, "🤨")
        await log(f'Member {message.from_user.id} from the group {message.chat.id} requested admin panel')


@dp.message_handler()
async def actions_handler(message: types.Message):
    if message.chat.id == config.admin_id or message.chat.id in get_adminlist():
        await in_admin_panel(bot, message.chat.id, message.text)


@dp.callback_query_handler(lambda c: True)
async def inline(callback_query: types.CallbackQuery):
    if callback_query.message.chat.id in get_adminlist():
        await bot.answer_callback_query(callback_query.id)
        await admin_inline(bot, callback_query.data, callback_query.message.chat.id, callback_query.message.message_id)


if __name__ == '__main__':
    executor.start_polling(dp)
