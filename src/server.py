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




    #TODO: Chamar a função em uma thread no construtor
    """
        From time to time the server will check if a session contains at least one player
        If it doesn't then the session will be finished
    """
    def checkSessions(self):
        pass

    # def sendMessage(self, player = None, publicMsg = "", privateMsg = "", waitingAnswer = False) -> None:
    #     playerId = player.getId() if player != None else ""
    #     messageDict = {
    #         "userId": playerId,
    #         "publicMsg" : publicMsg,
    #         "privateMsg" : privateMsg,
    #         "waitingAnswer" : waitingAnswer
    #     }

    #     msg = json.dumps(messageDict).encode(FORMAT)

    #     for p in self.match.getPlayers():
    #         p.getSocket().sendall(msg) 
        
    #     sleep(0.2)  

    # def recvMessage(self, socketTarget) -> str:
    #     while True:
    #         buffer = socketTarget.recv(BUFFER_SIZE).decode(FORMAT)
    #         if buffer:
    #             return buffer
            
