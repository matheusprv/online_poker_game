import socket
import json

BUFFER_SIZE = 4096

PORT = 7890
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

FORMAT = 'utf-8'



"""
messageDict = {
    "userId": playerId,
    "publicMsg" : publicMsg,
    "privateMsg" : privateMsg,
    "waitingAnswerFrom": playerId #O valor é copiado para evitar muitas verificações no servidor 
}
"""