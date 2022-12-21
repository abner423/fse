import adafruit_dht as DHT
import RPi.GPIO as GPIO
import json
import board

class Room:
    entrada: dict
    saida: dict
    nome_da_sala: str
    endereco_servidor_central: str
    porta_servidor_central: int
    estados: dict
    sensores: dict
    dht22_pin: int
    numero_de_pessoas: int
    temperatura: float
    umidade: float
    is_alarme_ativado: bool

    def inicializa_estados_sensores(self, filename: str) -> None:
        with open(filename, 'r') as f:
            file = json.load(f)

        json_inputs = file['inputs']
        json_outputs = file['outputs']
        
        self.entrada = {} 
        self.saida = {} 

        for input in json_inputs:
            self.entrada[input['type']] = input['gpio']

        for output in json_outputs:
            self.saida[output['type']] = output['gpio']
        
        self.nome_da_sala = file['nome']

        self.endereco_servidor_central = file['ip_servidor_central']
        self.porta_servidor_central = file['porta_servidor_central']

        # creates a dict through dict comprehension to store the state of all outputs
        self.estados = {key: 'Desligado' for key in self.saida}
        self.sensores = ['SPres', 'SFum', 'SJan', 'SPor']
        self.dht22_pin = file['sensor_temperatura'][0]['gpio']
        
        self.dht22 = DHT.DHT22(board.D18, use_pulseio=False) if self.dht22_pin == 18 else DHT.DHT22(board.D4, use_pulseio=False)

        self.numero_de_pessoas = 0
        self.is_alarme_ativado = False

        self.temperatura = 0
        self.umidade = 0



    def inicializa_placa(self) -> None:
        GPIO.setmode(GPIO.BCM)
        for pino in self.saida.values():
            GPIO.setup(pino, GPIO.OUT)

        for pino in self.entrada.values():
            GPIO.setup(pino, GPIO.IN)
        
        GPIO.add_event_detect(self.entrada['SC_IN'], GPIO.RISING)
        GPIO.add_event_detect(self.entrada['SC_OUT'], GPIO.RISING)

        self.desliga_todos_os_pinos()



    def __init__(self, filename: str) -> None:
        self.inicializa_estados_sensores(filename)
        self.inicializa_placa()
        
    

    def desliga_todos_os_pinos(self) -> None:
        for pino in self.saida:
            self.desliga_pino(pino)
    

    def liga_pino(self, pino:str) -> None:
        GPIO.output(self.saida[pino], GPIO.HIGH)
        self.estados[pino] = 'Ligado'


    def desliga_pino(self, pino:str) -> None:
        GPIO.output(self.saida[pino], GPIO.LOW)
        self.estados[pino] = 'Desligado'


    def toggle_estado_pino(self, pino:str) -> None:
        if self.estados[pino] == 'Ligado':
            self.desliga_pino(pino)
        else:
            self.liga_pino(pino)


    def contabiliza_numero_de_pessoas(self) -> None:
        if GPIO.event_detected(self.entrada['SC_IN']):
            self.numero_de_pessoas += 1
        if GPIO.event_detected(self.entrada['SC_OUT']) and self.numero_de_pessoas > 0:
            self.numero_de_pessoas -= 1


    def atualiza_temperatura(self) -> int:
        try:
            self.temperatura = self.dht22.temperature
            self.umidade = self.dht22.humidity
            return 0
        except RuntimeError:
            return 1