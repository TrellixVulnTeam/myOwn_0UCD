import socket
import threading
import time

key = 8194

shutdown = False
join = False
crypto = False


def receiving(name, sock):
    while not shutdown:
        try:
            while True:
                data, addr = sock.recvfrom(1024)

                if crypto:
                    # Begin
                    decrypt = ""
                    k = False
                    for i in data.decode("utf-8"):
                        if i == ":":
                            k = True
                            decrypt += i
                        elif k == False or i == " ":
                            decrypt += i
                        else:
                            decrypt += chr(ord(i) ^ key)
                    print(decrypt)
                    # End
                else:
                    print(data.decode("utf-8"))

                time.sleep(0.2)
        except:
            pass


# host = socket.gethostbyname(socket.gethostname())
host = "127.0.0.1"
port = 0

server = ("127.0.0.1", 8080)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

alias = input("Name: ")

rT = threading.Thread(target=receiving, args=("RecvThread", s))
rT.start()

while not shutdown:
    if not join:
        s.sendto(("[" + alias + "] => join chat ").encode("utf-8"), server)
        join = True
    else:
        try:
            message = input()

            if crypto:
                # Begin
                crypt = ""
                for i in message:
                    crypt += chr(ord(i) ^ key)
                message = crypt
                # End

            if message != "":
                s.sendto(("[" + alias + "] :: " + message).encode("utf-8"), server)

            time.sleep(0.2)
        except:
            s.sendto(("[" + alias + "] <= left chat ").encode("utf-8"), server)
            shutdown = True

rT.join()
s.close()