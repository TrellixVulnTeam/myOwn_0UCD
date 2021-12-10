import files
import yaml


# класс по настройке бота
class Settings:
    def __init__(self):
        self.file_settings = open(files.settings, 'r')  # открываем файл для чтения
        self.settings = yaml.safe_load(self.file_settings)
        self.new_event_setting = self.settings['Settings']['NewEventNotification']
        self.hot_event_setting = self.settings['Settings']['HotEventNotification']
        self.file_settings.close()

        self.file_help_text = open('data/help.txt', encoding='utf-8')
        self.help_text = self.file_help_text.read()
        self.file_help_text.close()

    def __enter__(self):  # обработчик входа в контекстный менеджер
        self.file_token = open(files.token, 'r')  # открываем файл для чтения
        self.TOKEN = yaml.safe_load(self.file_token)
        return self.TOKEN['TOKEN']

    def __exit__(self, exc_type, exc_val, exc_tb):  # обработчик выхода из контекстного менеджера
        self.file_token.close()


# класс события (используется при создании события и редактирования, как хранилище данных до записи в базу)
class Event:
    def __init__(self, name=None, description=None, date=None, name_entities=None,
                 description_entities=None, type_event=None):
        self.name = name
        self.description = description
        self.date = date
        self.name_entities = name_entities
        self.description_entities = description_entities
        self.type_event = type_event


# класс для списков событий, внутри него происходит сбор и
# дальнейшая сортировка событий по времени
class Event_List:
    def __init__(self):
        self.events_unsorted = {}
        self.events_TBA = []
        self.events_TT = []
        self.events_HOT = {}
        self.events_HOT_unsorted = {}
        self.events_PREVIOUS = {}
        self.events_PREVIOUS_unsorted = {}
        self.events_TODAY = {}
        self.events_TODAY_unsorted = {}
        self.events_UPCOMING = {}
        self.events_UPCOMING_unsorted = {}
        self.events_types_pair = [[self.events_HOT_unsorted, self.events_HOT],
                                  [self.events_PREVIOUS_unsorted, self.events_PREVIOUS],
                                  [self.events_TODAY_unsorted, self.events_TODAY],
                                  [self.events_UPCOMING_unsorted, self.events_UPCOMING]]

    def sort_out_all_groups(self):
        for events_types in self.events_types_pair:
            events_types[1] = dict(sorted(events_types[0].items(), key=lambda item: item[1]))


class Page_Mem:
    def __init__(self):
        self.last_page = {}
        self.list_pages = []


class Message_Mem:
    def __init__(self):
        self.last_message = {}
        self.list_messages = []


# проверка и удаление старых сообщений со списками событий
async def check_repeated_message(bot, message, last_message):
    if message.chat.id in last_message.last_message.keys():
        last_message_start_id = last_message.last_message.get(message.chat.id)
        if message.message_id + 1 - 300 > last_message_start_id:
            last_message.last_message[message.chat.id] = message.message_id + 1
        elif message.message_id + 1 - 300 <= last_message_start_id:
            try:
                await bot.delete_message(message.chat.id, last_message.last_message[message.chat.id])
            except:
                last_message.last_message[message.chat.id] = message.message_id + 1
            else:
                last_message.last_message[message.chat.id] = message.message_id + 1
    else:
        last_message.last_message[message.chat.id] = message.message_id + 1
