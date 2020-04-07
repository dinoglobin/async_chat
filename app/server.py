import asyncio
from asyncio import transports
from typing import Optional


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        print(data.decode('utf8').strip())

        decoded = data.decode('utf8').strip()

        if self.login is not None:
            if decoded:
                self.send_message(decoded)
                message_to_history = f"<{self.login}>: {decoded}"
                self.server.messages.append(message_to_history)
            else:
                self.transport.write("Вы не ввели сообщение!\r\n".encode())
        else:
            if decoded:
                if decoded.startswith("login:"):
                    temp_login = decoded.replace("login:", "").replace("\r\n", "")
                    unique = True   # переменная уникальности
                    # сравнение введённого логина с имеющимися в списке пользователей
                    for i in range(len(self.server.clients)):
                        if self.server.clients[0].login == temp_login:
                            unique = False
                    # если логин уникальный, то присваивается пользователю, иначе - выводится информационное сообщение
                    if unique:
                        self.login = temp_login
                        self.transport.write(
                            f"Привет, {self.login}!\r\n".encode()
                        )
                        self.send_history()
                    else:
                        self.transport.write("Этот логин уже занят! Выберите другой!\r\n".encode())
                else:
                    self.transport.write("Неправильный логин\r\n".encode())
            else:
                self.transport.write("Вы не ввели логин!\r\n".encode())

    def connection_made(self, transport: transports.BaseTransport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришёл новый клиент")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print(f"Клиент {self.login} вышел")

    def send_message(self, content: str):
        message = f"{self.login}: {content}\r\n"
        message_for_me = f"Your: {content}\r\n"

        for user in self.server.clients:
            if user.login == self.login:
                user.transport.write(message_for_me.encode())
            else:
                user.transport.write(message.encode())

    def send_history(self):
        history_size = len(self.server.messages)  # количество сообщений в истории чата
        if history_size == 0:
            self.transport.write("Чат пуст\r\n".encode())
        elif history_size < 10:
            self.transport.write(f"Держи последние {history_size} сообщений)\r\n".encode())
            for i in self.server.messages:
                self.transport.write(f"*****{i}\r\n".encode())
        else:
            self.transport.write("Держи последние 10 сообщений)\r\n".encode())
            for i in range(history_size - 10, history_size, 1):
                self.transport.write(f"*****{self.server.messages[i]}\r\n".encode())


class Server:
    clients: list
    messages: list  # переменная для хранения сообещния

    def __init__(self):
        self.clients = []
        self.messages = []  # список сообщений

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            "127.0.0.1",
            8888
        )

        print("Сервер запущен...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")