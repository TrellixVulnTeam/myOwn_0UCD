import socket
import threading
import time


# Класс приложения клиента для взаимодействия с сервером.
# Принимает в себя объект класса KivyApp и имя авторизированного пользователя.
class ClientAPI:
    def __init__(self, class_app, username):
        self.key = 8194  # крипто-ключ
        self.class_app = class_app
        self.username = username
        self.shutdown = False
        self.join = False
        self.crypto = True  # флаг вкл/выкл шифрование сообщений
        self.socket_state = False

    # Метод получения состояния сокета клиентского приложения.
    def get_state_socket(self):
        return self.socket_state

    # Открытие сокета и соединение с сервером.
    def open_socket(self, instance):
        host = "3.tcp.ngrok.io"
        port = 22655
        # host = "127.0.0.1"
        # port = 8080

        self.server = (host, port)
        # self.server = ("127.0.0.1", 8080)
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err:
            print("Socket creation failed with error %s" % (err))
        else:
            self.s.connect(self.server)
            print("Connected to {}:{}".format(host, port))
            self.s.setblocking(False)
            print('Socket was opened')
            self.socket_state = True

            self.rT = threading.Thread(target=self.receiving, args=("RecvThread", self.s))
            self.rT.start()


        # оповещение чата о новом пользователе
        if not self.join:
            print("[" + self.username + "] => join chat ")
            self.s.sendto(("[" + self.username + "] => join chat ").encode("utf-8"), self.server)
            self.join = True

    # Отправка сообщений на сервер.
    def sending(self, message):
        try:
            self.class_app.print_received_message("[" + self.username + "] :: " + message)
            print("[" + self.username + "] :: " + message)

            # шифрование сообщений
            if self.crypto:
                # Begin
                crypt = ""
                for i in message:
                    crypt += chr(ord(i) ^ self.key)
                message = crypt
                # End

            # отправка сообщения на сервер
            if message != "":
                self.s.sendto(("[" + self.username + "] :: " + message).encode("utf-8"), self.server)

            time.sleep(0.2)

        except:
            self.close_socket(0)

    # Приём сообщений с сервера.
    # Данный метод ставится в другой поток и обрабатывается отдельно.
    def receiving(self, name, sock):
        while not self.shutdown:
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    # дешифрование сообщения и дальнейшая отправка его в окно полученных сообщений
                    if self.crypto:
                        # Begin
                        decrypt = ""
                        k = False
                        for i in data.decode("utf-8"):
                            if i == ":":
                                k = True
                                decrypt += i
                            elif not k or i == " ":
                                decrypt += i
                            else:
                                decrypt += chr(ord(i) ^ self.key)
                        self.received_message = decrypt
                        self.class_app.print_received_message(self.received_message)
                        print(self.received_message)
                        # End
                    else:
                        self.received_message = data.decode("utf-8")
                        self.class_app.print_received_message(self.received_message)
                        print(self.received_message)

                    time.sleep(0.2)
            except:
                pass

    # Закрытие сокета и отсоединение от сервера.
    # Также оповещение чата о выходе пользователя.
    def close_socket(self, instance):
        self.s.sendto(("[" + self.username + "] <= left chat ").encode("utf-8"), self.server)
        print("[" + self.username + "] <= left chat ")
        print('socket is closing...')
        self.s.close()
        print('socket was closed')
        self.socket_state = False
        self.shutdown = True
        self.join = False



