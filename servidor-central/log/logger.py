from datetime import datetime

def write_log(event:str) -> None:
    with open('servidor-central-log.csv', 'a', encoding='UTF8') as f:
        f.write(f'{event},{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')