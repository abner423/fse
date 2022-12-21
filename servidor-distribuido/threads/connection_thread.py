from time import sleep, time
from room import Room
import threading
import socket
import sys

from threads.room_thread import *

class ConnectionThread(threading.Thread):
    def __init__(self, room:Room) -> None:
        super().__init__()
        self.room_thread = RoomThread(room)
        self.room_thread.daemon = True
        self.host = self.room_thread.room.endereco_servidor_central
        self.port = self.room_thread.room.porta_servidor_central
    

    def create_con(self):
        self.central_soc = socket.create_connection((self.host, self.port))
        self.send_message(self.room_thread.room.nome_da_sala)
        print(f'Opa ! Sala conectada - {self.host}')


    def send_message(self, message):
        self.central_soc.send(bytes(message, encoding='utf-8'))
    

    def run(self):
        self.create_con()
        self.room_thread.start()
        print('\n Esperando um comando...')
        while True:
            request = self.central_soc.recv(1024).decode('utf-8')

            if request == 'kys NOW':
                print('Poxa ! O servidor caiu')
                sys.exit()

            elif request == 'update':
                message = self.room_thread.get_json_dump()
                self.send_message(message)
                print('data sent')
            
            elif request == 'L_ON':
                self.room_thread.room.liga_pino('L_01')
                self.room_thread.room.liga_pino('L_02')
                self.send_message('success')
                print('Todas as Luzes foram ligadas !')

            elif request == 'L_OFF':
                self.room_thread.room.desliga_pino('L_01')
                self.room_thread.room.desliga_pino('L_02')
                self.send_message('success')
                print('Todas as Luzes foram desligadas !')

            elif request == 'AC' or request == 'PR' or request == 'L_01' or request == 'L_02':
                self.room_thread.room.toggle_estado_pino(request)
                self.send_message('success')
                print(f'{request} switched')

            elif request == 'all_off':
                self.room_thread.room.desliga_todos_os_pinos()
                self.send_message('success')
                print('Tudo foi desligado !')

            elif request == 'switch_alarm':
                if self.room_thread.room.is_alarme_ativado: 
                    self.room_thread.room.is_alarme_ativado = False
                    self.send_message('success')
                else:
                    self.room_thread.room.is_alarme_ativado = True
                    self.send_message('success')
                    print('Alarme foi disparado !')

