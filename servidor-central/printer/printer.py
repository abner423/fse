import os
from constants.mensages_constants import *

def printa_salas_conectadas(sockets) -> None:
    print(SALAS_DISPONIVEIS)

    for board in sockets:
        print(board)
    
    print(CONSOLE)

def printa_dados_da_sala(dados_sala:dict) -> None:
    print("####################################")
    for dado in dados_sala:
        if dado == 'Placa':
            print(f'# {dado}: \t\t{dados_sala[dado]} #')
        else:
            print(f'# {dado}: \t{dados_sala[dado]} #')
    print("####################################")

def limpa_console() -> None:
    os.system('clear')

def printa_numero_de_pessoas_no_predio(sockets, states) -> None:
    numeroPessoas = 0
    for board in sockets:
        numeroPessoas += int(states[board]['Pessoas'])
    print(f'Qtd de pessoas no prédio: {numeroPessoas}\n')