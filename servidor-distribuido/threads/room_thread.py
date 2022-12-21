from time import sleep, time
from room import Room
import threading
import json
import RPi.GPIO as GPIO

class RoomThread(threading.Thread):
    lights_timer : float
    recent_pres : bool

    def __init__(self, room: Room) -> None:
        super().__init__()
        self.room = room
    

    def turn_lights_on(self):
        self.room.liga_pino('L_01')
        self.room.liga_pino('L_02')
        self.lights_timer = time()
        self.recent_pres = True


    def time_lights(self):
        if time() - self.lights_timer > 15.0:
            self.room.desliga_pino('L_01')
            self.room.desliga_pino('L_02')
            self.lights_timer = None
            self.recent_pres = False


    def get_states(self) -> dict:
        dic = {}

        for item in self.room.estados:
            if item == 'L_01':
                dic['Lâmpada 01'] = self.room.estados['L_01']
            elif item == 'L_02':
                dic['Lâmpada 02'] = self.room.estados['L_02']
            elif item == 'PR':
                dic['Projetor'] = self.room.estados['PR']
            elif item == 'AC':
                dic['Ar-Con'] = self.room.estados['AC']
            elif item == 'AL_BZ':
                dic['Sirene'] = self.room.estados['AL_BZ']
        return dic


    def check_sensors(self) -> bool:
        for sensor in self.room.sensores:
            if GPIO.input(self.room.entrada[sensor]):
                return True
    
    def get_sensors(self) -> dict:
        dic = {}

        for sensor in self.room.sensores:
            if sensor == 'SPres':
                nome_sensor = 'S. Presença'
            elif sensor == 'SFum':
                nome_sensor = 'S. Fumaça'
            elif sensor == 'SJan':
                nome_sensor = 'S. Janela'
            elif sensor == 'SPor':
                nome_sensor = 'S. Porta'

            if GPIO.input(self.room.entrada[sensor]):
                dic[nome_sensor] = 'Ligado'
            else:
                dic[nome_sensor] = 'Desligado'
        return dic


    def get_ppl_qty(self) -> dict:
        dic = {'Pessoas': self.room.numero_de_pessoas}
        return dic
    

    def get_temp_humd(self) -> dict:
        dic = {'Temperatura' : f'{self.room.temperatura} ºC', 'Umidade' : f'{self.room.umidade}%',}
        return dic
    
    
    def get_json_dump(self) -> str:
        dic = {'Placa' : self.room.nome_da_sala}
        dic = dic | self.get_states() | self.get_sensors() | self.get_ppl_qty() | self.get_temp_humd() 
        return json.dumps(dic)


    def run(self):
        self.recent_pres = False
        self.lights_timer = 0

        while True:
            self.room.contabiliza_numero_de_pessoas()
            self.room.atualiza_temperatura()
            if self.check_sensors():
                if self.room.is_alarme_ativado:
                    self.room.liga_pino('AL_BZ')
                else:
                    if GPIO.input(self.room.entrada['SPres']):
                        self.turn_lights_on()

                    if GPIO.input(self.room.entrada['SFum']): 
                        self.room.liga_pino('AL_BZ')

            elif self.room.estados['AL_BZ']:
                self.room.desliga_pino('AL_BZ')
            
            if self.recent_pres:
                self.time_lights()
            sleep(0.1)

