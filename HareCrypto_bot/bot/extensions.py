# класс по работе с токеном
class Token:
    def __init__(self):
        pass

    def __enter__(self):  # обработчик входа в контекстный менеджер
        self.file = open('token.yaml', 'r')  # открываем файл для чтения
        self.name_t = self.file.read(8)  # читаем первые символы с названием конфигурации
        if self.name_t == "TOKEN = ":  # находим конфигурацию токена
            self.TOKEN = self.file.read()  # считываем токен
            return self.TOKEN

    def __exit__(self, exc_type, exc_val, exc_tb):  # обработчик выхода из контекстного менеджера
        self.file.close()


class Event:
    def __init__(self, name=None, description=None, date=None, name_entities=None, description_entities=None):
        self.name = name
        self.description = description
        self.date = date
        self.name_entities = name_entities
        self.description_entities = description_entities


class Event_List:
    def __init__(self):
        self.events_unsorted = {}
        self.events_TBA = []
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


class Message_Mem:
    def __init__(self):
        self.last_message = {}
        self.list_messages = []


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
