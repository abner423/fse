import threading
import json
from threads.server_thread import *
from time import sleep

class StatesThread(threading.Thread):
    estados: dict
    sockets: dict

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.server = ServerThread(host, port)
        self.server.daemon = True
        self.estados = {}
        self.sockets = {}
    

    def envia_mensagem_servidor_distribuido(self, destiny, message) -> None:
        self.sockets[destiny].send(bytes(message, encoding='utf-8'))

    def recebe_mensagem_servidor_distribuido(self, board) -> None:
        self.sockets[board].recv(4096).decode('utf-8')


    def run(self) -> None:
        self.server.start()
        while True:
            self.sockets = self.server.sockets
            for board in self.sockets:
                self.envia_mensagem_servidor_distribuido(board, 'update')
                self.estados[board] = json.loads(self.sockets[board].recv(4096).decode('utf-8'))
            sleep(2)