from player import Player
from session import Session
from constants import *

import threading

class Server:

    def __init__(self, maximunSessions = 4) -> None:
        self.sessionsThreads = []
        self.sessions = []
        self.maximunSessions = maximunSessions
        self.createServer()
        self.playersSockets = []

    
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
    def __createSession(self, id) -> Session:
        if len(self.sessions) == self.maximunSessions: return None

        newSession = Session(id, self.main_socket)
        self.sessions.append(newSession)
        return newSession

    """
        Creates multiple sessions
    """
    def createSessions(self) -> None:
        for i in range(self.maximunSessions):
            self.__createSession(i+1)
            
    """
        Start all the sessions in parallel
    """
    def startSessions(self) -> None:
        for sess in self.sessions:
            thTemp = threading.Thread(target=sess.startGame)
            thTemp.start()
            self.sessionsThreads.append(thTemp)





    def recvMessage(self, socketTarget) -> str:
        while True:
            buffer = socketTarget.recv(BUFFER_SIZE).decode(FORMAT)
            if buffer:
                return buffer

    def receiveNumericSessionNumber(self, playerSocket) -> int:
        #Sending message from number of sessions available
        text = f"Escolha entre as sessões 1, 2, 3 ou 4."
        msg = text.encode(FORMAT)
        playerSocket.sendall(msg)
        
        #Choosed session
        receivedValue = self.recvMessage(playerSocket)
        while not receivedValue.isnumeric():
            errorMessage = f"Valor inválido.\nO número da sessão deve ser entre 1 e {self.maximunSessions}"
            msg = errorMessage.encode(FORMAT)
            playerSocket.sendall(msg)
            receivedValue = self.recvMessage(playerSocket)
        return int(receivedValue)


    #TODO verificar se a sessão pode aceitar jogadores
    def validateSessionChoose(self, playerSocket):
        sessionNumber = -1
        while sessionNumber < 0 or sessionNumber > self.maximunSessions:
            sessionNumber = self.receiveNumericSessionNumber(playerSocket) - 1
            
        msg = "SESS ACK".encode(FORMAT)
        playerSocket.sendall(msg)
        return sessionNumber


    def handleConnection(self, playerSocket):
        # Esperar para ver qual sessão ele quer entrar
        sessionNumber = self.validateSessionChoose(playerSocket)           
        
        choosedSession = self.sessions[sessionNumber]      
        choosedSession.playersSocketStack.append(playerSocket)
        self.sessions[sessionNumber].event.set()

    def connectPlayers(self):
        while True:
            playerSocket, _ = self.main_socket.accept()
            th = threading.Thread(target=self.handleConnection, args=(playerSocket,))
            th.start()

            
