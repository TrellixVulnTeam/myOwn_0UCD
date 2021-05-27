import socket
import time

# host = socket.gethostbyname(socket.gethostname())
host = "127.0.0.1"
port = 8080

clients = []
server_stop = False


def server_settings(host_, port_):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host_, port_))
    time.sleep(3)
    print("[ Server Started ]")
    return s


def server_receiving(s):
    global server_stop
    try:
        data, addr = s.recvfrom(1024)

        if addr not in clients:
            clients.append(addr)

        if "left chat" in data.decode("utf-8"):
            clients.remove(addr)

        itsatime = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())

        print("[" + addr[0] + "]=[" + str(addr[1]) + "]=[" + itsatime + "]/", end="")
        print(data.decode("utf-8"))

        for client in clients:
            if addr != client:
                s.sendto(data, client)
    except:
        print("\n[ Server Error ]")
        print("\n[ Restart Server... ]")
        server_stop = True


while True:
    try:
        server_stop = False
        print("\n[ Server Starting... ]")
        sock = server_settings(host, port)

        while not server_stop:
            server_receiving(sock)
    except:
        sock.close()
        print("\n[ Server Stopped]")
        break
