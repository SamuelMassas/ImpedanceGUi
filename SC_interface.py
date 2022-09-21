import socket


class Server:
    def __init__(self):
        self.ipv4 = socket.gethostbyname(socket.gethostname())
        self.PORT = 5050
        self.serversocket = None
        self.online = False
        self.clients = []
        self.ack = bytes([200])  # Acknowledgement byte 200 to 300

    def set_online(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((self.ipv4, self.PORT))
        self.serversocket.listen(5)  # Accept only 5 client connections
        self.online = True

    def start_listening(self):
        """ Getting clients """
        print(f'[SERVER] Server is listening at {self.ipv4}:{self.PORT}...')
        while self.online:
            try:
                client = self.serversocket.accept()
                self.clients.append(client)
                print('[SERVER] New client!!!')
                # self.stream2client(client, "Hello, client")
            except OSError:
                print('[SERVER] Listener stopped')
                break

    def set_offline(self):
        self.serversocket.close()
        self.online = False
        self.clients = []

    def stream2client(self, client, data):
        if self.online:
            data_8bit = str(data).encode('utf-8')
            numBytes = len(data_8bit)
            filling = 15 - len(str(numBytes).encode('utf-8'))
            try:
                client[0].send(str(numBytes).encode('utf-8')+b'_'*filling)
                client[0].send(data_8bit)

            except ConnectionResetError:
                for stored_client in self.clients:
                    if client == stored_client:
                        self.clients.remove(client)
                print(f'[SERVER] {client} lost the connection')


class Client:
    def __init__(self, ipv4='192.168.32.28', port=5050):
        self.ipv4 = ipv4
        self.PORT = port
        self.client = None
        self.online = False

    def connect_client(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.ipv4, self.PORT))
        self.online = True
        print(f'[CLIENT] client is connected !!!')

    def close_connection(self):
        self.client.close()
        self.online = False

    def start_listening(self):
        if self.online:
            try:
                numBytes = self.client.recv(15)
                numBytes = int(float(numBytes.decode('utf-8').replace('_', '')))
                data = self.client.recv(numBytes)
                print(f'[SERVER] {data}')

                return data.decode('utf-8')
            except ConnectionAbortedError:
                self.client = None
                print(f'[CLIENT] client no longer connected to SERVER')
