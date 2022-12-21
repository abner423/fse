# fse

## Como Rodar

1. Copie as pastas para as placas
2. Nos servidores distribuidos, instale as dependencias que estao no requirements.txt.
3. No servidor central, execute `python3 central.py <host> <port>`, por exemplo python3 central.py 192.168.0.1 8080.
4. Nos servidores distribuídos, execute `python3 control.py nome_sala.json` por exemplo python3 control.py sala3.json
