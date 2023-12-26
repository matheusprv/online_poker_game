import socket
import json

BUFFER_SIZE = 1024

PORT = 7891
SERVER = socket.hostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

FORMAT = 'utf-8'

"""
dict_msg = {
    userId
    name
    action
    msgServer
}
"""