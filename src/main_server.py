from constants import *
from server import Server

if __name__ == "__main__":

    server = Server()

    server.createSessions()
    server.startSessions()
    server.connectPlayers()
