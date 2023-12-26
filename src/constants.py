import socket
import json

BUFFER_SIZE = 4096

PORT = 7891
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

FORMAT = 'utf-8'