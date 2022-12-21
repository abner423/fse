from room import Room
from threads.connection_thread import ConnectionThread
import sys

def main():
    json_file = sys.argv[1]
    ct = ConnectionThread(Room(json_file))
    ct.start()


if __name__ == '__main__':
    main()