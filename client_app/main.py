import time

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label

from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.config import Config

# Импорт приложения клиента для взаимодествия с сервером.
from client import ClientAPI
# Флаги преднастройки приложения для платформы.
desktop = 1
phone = 0

if desktop:
    # Конфигурации настроек графического отображения главного окна приложения для ПК.
    Window.size = (1080, 720)
if phone:
    # Конфигурации настроек графического отображения главного окна приложения для телефона.
    Window.size = (720, 1280)
    Config.set('kivy', 'keyboard_mode', 'systemanddock')

# Словарь с пользователями.
# TODO Подключить базу данных вместо словаря.
users = {
    'san': '1234',
    'dim': '1111',
    'vla': '2222',
}


# Основной класс интерфейса приложения.
class ClientInterfaceApp(App):
    # Функция отправки сообщений на сервер.
    def send_message(self, instance):
        if self.message_field.text == "":
            pass
        else:
            self.client.sending(self.message_field.text)
            self.message_field.text = ""

    # Очистка поля полученных сообщений.
    def clear_receive_window(self, instance):
        self.input_message.text = ''

    # Функция печати сообщений в поле полученных сообщений.
    # Печатаются как сообщения пользователя так и сообщения других
    # участников чата (метод вызывается из класса приложения клиента).
    def print_received_message(self, mess):
        self.input_message.text = self.input_message.text + '\n' + mess

    # Функция проверки состояния кнопки Подключения к серверу.
    # При авторизации кнопка уже зажата (down) и состояние Connected
    def check_button(self, instance):
        state = self.client.get_state_socket()
        if self.connection_button.state == 'normal' and state:
            self.client.close_socket(0)
            self.connection_button.text = 'Disconnected'
        else:
            self.client.open_socket(0)
            self.connection_button.text = 'Connected'

    # Создание окна чата после авторизации.
    def chatting_window(self, login):
        self.main_layout.remove_widget(self.lbl)
        self.window_chat = BoxLayout(orientation="vertical")

        self.input_message = TextInput(readonly=True, font_size='24sp', background_color=[1, 1, 1, .8])
        self.window_chat.add_widget(self.input_message)
        self.message_field = TextInput(hint_text="Text", size_hint=[1, .20], font_size=24, multiline=False)
        self.message_field.bind(on_text_validate=self.send_message)
        self.window_chat.add_widget(self.message_field)
        field_toolbar = BoxLayout(orientation="horizontal", size_hint=[1, .10])
        field_toolbar.add_widget(Button(text="Send", font_size='24sp', on_press=self.send_message))
        field_toolbar.add_widget(Button(text="Clear", font_size='24sp', on_press=self.clear_receive_window))
        field_toolbar.add_widget(Label(text=f"{login}", font_size='24sp'))
        self.connection_button = ToggleButton(text="Connected",
                                              font_size='24sp',
                                              state="down",
                                              on_press=self.check_button)
        field_toolbar.add_widget(self.connection_button)

        self.window_chat.add_widget(field_toolbar)

        self.main_layout.add_widget(self.window_chat)

    # Поле ввода логина и пароля, где осуществляется идентификация пользователя и далее авторизация в приложении
    def enter(self, instance):
        login = str(self.login.text)
        password = str(self.password.text)

        if login in users.keys():
            if password == users.get(login):
                self.main_layout.remove_widget(self.field_enter)

                self.client = ClientAPI(self, login)
                self.client.open_socket(login)
                print('socket is opened')

                self.lbl = Label(text=f'Hello {login}', font_size='30sp')
                self.main_layout.add_widget(self.lbl)
                time.sleep(0.5)

                self.chatting_window(login)

            else:
                self.main_layout.remove_widget(self.field_enter)

                self.field_enter = BoxLayout(orientation="vertical", size_hint=[.45, .45])
                self.field_enter.add_widget(Label(text='Wrong login', font_size='30sp'))
                self.login = TextInput(hint_text="Login", font_size='24sp', multiline=False)
                self.field_enter.add_widget(self.login)
                self.password = TextInput(hint_text="Password", font_size='24sp', multiline=False)
                self.password.bind(on_text_validate=self.enter)
                self.field_enter.add_widget(self.password)
                self.field_enter.add_widget(Button(text="Enter", font_size='24sp', on_press=self.enter))
                self.main_layout.add_widget(self.field_enter)

        else:
            self.main_layout.remove_widget(self.field_enter)

            self.field_enter = BoxLayout(orientation="vertical", size_hint=[.45, .45])
            self.field_enter.add_widget(Label(text='Wrong login', font_size='30sp'))
            self.login = TextInput(hint_text="Login", font_size='24sp', multiline=False)
            self.field_enter.add_widget(self.login)
            self.password = TextInput(hint_text="Password", font_size='24sp', multiline=False)
            self.password.bind(on_text_validate=self.enter)
            self.field_enter.add_widget(self.password)
            self.field_enter.add_widget(Button(text="Enter", font_size='24sp', on_press=self.enter))
            self.main_layout.add_widget(self.field_enter)

    # Метод создания первичного отображения окна авторизации в приложении.
    def build(self):
        self.title = 'X-mess (message exchanger) by AlexDead'
        self.main_layout = AnchorLayout()
        self.field_enter = BoxLayout(orientation="vertical", size_hint=[.45, .35])

        self.login = TextInput(hint_text="Login", font_size='24sp', multiline=False)
        self.field_enter.add_widget(self.login)
        self.password = TextInput(hint_text="Password", font_size='24sp', multiline=False)
        self.password.bind(on_text_validate=self.enter)
        self.field_enter.add_widget(self.password)

        self.field_enter.add_widget(Button(text="Enter", font_size='24sp', on_press=self.enter))
        self.main_layout.add_widget(self.field_enter)

        return self.main_layout


if __name__ == "__main__":
    kivy_app = ClientInterfaceApp()
    kivy_app.run()
