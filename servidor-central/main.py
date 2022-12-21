from threads.console_thread import *

def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    server = ConsoleThread(host, port)
    server.start()
    

if __name__ == '__main__':
    main()
