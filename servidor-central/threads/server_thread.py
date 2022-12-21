import threading
import socket

class ServerThread(threading.Thread):
    sockets: dict

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.sockets = {}
        self.server = socket.create_server((host, port))


    def run(self) -> None:
        while True:
            sock, addr = self.server.accept()
            room = sock.recv(1024).decode('utf-8')
            self.sockets[room] = sock