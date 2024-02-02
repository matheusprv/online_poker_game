from player import Player
from session import Session
from constants import *
from time import sleep 
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


    """
        Receive a message from the client and return what is the message
        The loop is used in case an empty message arrive
    """
    def recvMessage(self, socketTarget) -> str:
        while True:
            buffer = socketTarget.recv(BUFFER_SIZE).decode(FORMAT)
            if buffer: return buffer

    """
        Returns a string with all the sessions that is currently possible to connect
    """    
    def availableSessionsMessage(self) -> str:
        sessionsNumbers = ' '.join([str(i) for i in range(1, self.maximunSessions + 1) if self.sessions[i-1].isPossibleToConnect()])
        text = f"Escolha entre as sessões ({sessionsNumbers}): "
        return text

    """
        Awaits for the player to write a valid session number. It keeps on the loop until a valid value is given
        Return the value that the user typed which is within the range 1 .. maximunSessions
    """
    def receiveNumericSessionNumber(self, playerSocket) -> int:
        #Sending message from number of sessions available
        msg = self.availableSessionsMessage().encode(FORMAT)
        playerSocket.sendall(msg)
        
        #Choosed session
        receivedValue = self.recvMessage(playerSocket)
        while not receivedValue.isnumeric():
            errorMessage = f"Valor inválido.\nO número da sessão deve ser entre 1 e {self.maximunSessions}: "
            msg = errorMessage.encode(FORMAT)
            playerSocket.sendall(msg)
            receivedValue = self.recvMessage(playerSocket)
        return int(receivedValue)



    """
        Validate if the selected session can be connected or not
        If it is possible, the session number is returned, otherwise it will keep waiting for a valid number
    """
    def validateSessionChoose(self, playerSocket):
        while True:
            sessionNumber = -1
            while sessionNumber < 0 or sessionNumber > self.maximunSessions:
                sessionNumber = self.receiveNumericSessionNumber(playerSocket) - 1
            
            if self.sessions[sessionNumber].isPossibleToConnect():
                msg = "SESS ACK".encode(FORMAT)
                playerSocket.sendall(msg)
                return sessionNumber
            
            else:
                msg = "SESS NACK".encode(FORMAT)
                playerSocket.sendall(msg)

    """
        Check what session the player will join and insert it to the player's stack of the session
    """
    def handleConnection(self, playerSocket):
        sessionNumber = self.validateSessionChoose(playerSocket)           
        choosedSession = self.sessions[sessionNumber]      
        choosedSession.playersSocketStack.append(playerSocket)
        self.sessions[sessionNumber].event.set()

    """
        Inifinite loop that will be accpeting new player's connections
    """
    def connectPlayers(self):
        while True:
            playerSocket, playerAddress = self.main_socket.accept()
            print(f"Conexão de jogador com endereço {playerAddress}")
            th = threading.Thread(target=self.handleConnection, args=(playerSocket,))
            th.start()

            
