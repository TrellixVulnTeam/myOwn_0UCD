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
    def __init__(self, name=None, description=None, date=None):
        self.name = name
        self.description = description
        self.date = date


class Event_List:
    def __init__(self):
        self.events_unsorted = {}
        self.events_TBA = []
        self.events_HOT = []
        self.events_PREVIOUS = []
        self.events_TODAY = []
        self.events_UPCOMING = []

    def add_event(self, event_list, event):
        event_list.append(event)
