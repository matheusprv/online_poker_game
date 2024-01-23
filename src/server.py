from player import Player
from session import Session
from constants import *

import threading
from time import sleep

class Server:

    def __init__(self, maximunSessions = 4) -> None:
        self.sessions = []
        self.maximunSessions = maximunSessions
        self.createServer()
        

    """
        Creates a socket and bind it to an address
    """
    def createServer(self):
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.bind(SERVER_ADDR_PORT)
        self.main_socket.listen(2^32)


    """
        Creates a new game session
    """
    def createSession(self) -> Session:
        if len(self.sessions) == self.maximunSessions: return None

        newSession = Session(self.main_socket)
        self.sessions.append(newSession)
        return newSession