import socket
import numpy as np


port = 5050
ipv4 = '192.168.32.28'
# ipv4 = socket.gethostbyname(socket.gethostname())
_format = 'utf-8'
disconnect_message = '!DISCONNECT'
address = (ipv4, port)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(address)


def _listen():
    print("[CLIENT] is listenning")
    while True:
        msg = client.recv(15).decode(_format)
        data_size = int(msg)

        data = client.recv(data_size)
        print(data)

        if data == disconnect_message:
            break

        data = data.decode(_format)

        data = data.replace('[', '').replace(']', '')

        # with open('socket_coms.txt', 'w') as file:
        #     file.write(data)

        rows = data.split('\n ')

        array = []
        for row in rows:
            columns = row.split(' ')
            array.append([float(item) for item in columns])

        np.array(array)
        print(array)



_listen()

client.close()
