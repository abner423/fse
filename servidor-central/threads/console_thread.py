import threading
from threads.states_thread import *
from log.logger import *

from datetime import datetime
import threading
import json
import sys

from constants.inputs_constants import *
from printer.printer import *
from constants.lights_constants import *


class ConsoleThread(threading.Thread):
    sockets: dict
    is_alarme_ativado: bool
    contador: int

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.st = StatesThread(host, port)
        self.st.daemon = True
        self.is_alarme_ativado = False
        self.sockets = {}
        self.contador = 0
    

    def envia_mensagem_socket(self, destiny, message) -> None:
        self.sockets[destiny].send(bytes(message, encoding='utf-8'))
    

    def recebe_mensagem_socket(self, board) -> str:
        response = self.sockets[board].recv(4096).decode('utf-8')
        print("Mensagem recebida - " + response)
        return response


    def atualiza_estados(self, board) -> None:
        self.envia_mensagem_socket(board, 'update')
        self.st.estados[board] = json.loads(self.sockets[board].recv(4096).decode('utf-8'))


    def verifica_se_sensores_ligados(self, board) -> bool:
        dic = self.st.estados[board]

        if dic['S. Presença'] == 'Ligado' or\
        dic['S. Fumaça'] == 'Ligado' or\
        dic['S. Janela'] == 'Ligado' or\
        dic['S. Porta'] == 'Ligado':
            return True
        else: return False

    def obtem_mensagem_das_luzes(self, board) -> str:
        msgs_dict = {
            LUZES_VOLTAR : '',
            LUZES_LIGAR_LAMPADA_01: 'L_01',
            LUZES_LIGAR_LAMPADA_02: 'L_02',
            LUZES_LIGAR_TODAS_AS_LAMPADAS: 'L_ON',
            LUZES_DESLIGAR_TODAS_AS_LAMPADAS: 'L_OFF'
        }
        limpa_console()
        printa_dados_da_sala(self.st.estados[board])
        opcao = input(LIGHTS)

        msg = msgs_dict[opcao]
        log = f'{board},{msg} acionado'
        write_log(log)
        return msg


    def room_console(self, board) -> None:
        msgs_dict = {
            INPUT_LIGAR_AR_CONDICIONADO : 'AC',
            INPUT_LIGAR_PROJETOR: 'PR',
            INPUT_DESLIGAR_TUDO: 'all_off',
        }

        while True:
            printa_dados_da_sala(self.st.estados[board])
            opcao = input(CONSOLE_ROOM)

            if(opcao == INPUT_VOLTAR):
                limpa_console()
                return
            elif opcao == '1': msg = self.obtem_mensagem_das_luzes(board)
            elif opcao == INPUT_LIGAR_AR_CONDICIONADO or opcao == INPUT_LIGAR_PROJETOR or opcao == INPUT_DESLIGAR_TUDO:
                msg = msgs_dict[opcao]
                log = f'{board},{msg} acionado'
                write_log(log)
            if opcao == '': limpa_console()
            else:
                self.envia_mensagem_socket(board, msg)
                limpa_console()
                self.recebe_mensagem_socket(board)
                self.atualiza_estados(board)


    def run(self):
        self.st.start()
        log = f'servidor-central, servidor startado'
        write_log(log)
        limpa_console()

        msgs_dict = {
            INPUT_LIGAR_TODAS_AS_LUZES : 'L_ON',
            INPUT_DESLIGAR_ENERGIA: 'all_off',
        }
        
        while True:
            self.sockets = self.st.sockets
            if self.sockets:
                for board in self.sockets:
                    self.atualiza_estados(board)

                printa_salas_conectadas(self.sockets)
                if self.is_alarme_ativado: print('Estado do alarme: Ligado') 
                else:print('Estado do alarme: Desligado')
                printa_numero_de_pessoas_no_predio(self.sockets, self.st.estados)

                choice = input()

                if choice == INPUT_SAIR_DO_PROGRAMA:
                    for board in self.sockets:
                        self.envia_mensagem_socket(board, 'kys NOW')
                    log = f'servidor-central, servidor derrubado'
                    write_log(log)
                    sys.exit()
                elif choice == INPUT_ATIVAR_ALARME:
                    for board in self.sockets:
                        if self.verifica_se_sensores_ligados(board):
                            limpa_console()
                            print('há sensores ativos, Nao foi possivel acionar o alarme')
                        else:
                            self.envia_mensagem_socket(board, 'switch_alarm')
                            limpa_console()
                            self.recebe_mensagem_socket(board)
                    if self.st.estados:
                        if self.is_alarme_ativado:
                            self.is_alarme_ativado = False
                            log = f'servidor-central, alarme desligado'
                            write_log(log)
                        else: 
                            self.is_alarme_ativado = True
                            log = f'servidor-central, alarme ligado'
                            write_log(log)
                elif choice == INPUT_LIGAR_TODAS_AS_LUZES or choice == INPUT_DESLIGAR_ENERGIA:
                    for board in self.sockets:
                        msg = msgs_dict[choice]
                        self.envia_mensagem_socket(board, msg)
                        limpa_console()
                        self.recebe_mensagem_socket(board)
                        write_log(msg)
                else: 
                    limpa_console()
                    for board in self.sockets:
                        if choice == board:
                            self.room_console(board)
