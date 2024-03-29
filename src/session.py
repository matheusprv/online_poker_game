from player import Player
from match import Match
from constants import *
import threading
from time import sleep

class Session:
    mutex = threading.Lock()
    MAXIMUN_NUMBER_OF_PLAYERS = 8
    SESSION_IDS = 0

    def __init__(self, id, main_socket) -> None:
        self.sessionId = id
        
        self.server_socket = main_socket

        self.match = Match(id, self.sendMessage, self.recvMessage, self.__quit) 
        self.numberOfPlayers = 0 
        self.playersSocketStack = []
        self.event = threading.Event()

    """
        True if it is possible to connect
        False if not. Because the game has already started or the session is full
    """
    def isPossibleToConnect(self) -> bool:
        if self.numberOfPlayers < self.MAXIMUN_NUMBER_OF_PLAYERS and not self.match.isInProgress():
            return True
        else:
            self.event.set()
            return False

    """
        Awaits for all players connect to the session.
        After all of them are connected and checked as 'pronto' the game begins
    """
    def startGame(self) -> None:
        while True:
            print(f"Start game from session {self.sessionId}")
            self.__playersConnection()
            self.__checkAllPlayersStatus()
            self.event.set() #Waking up the __handlePlayersConnection and finishing it
            self.match.startGame()
            self.__tellPlayersEndOfSession()
            self.__restartSession()

    def __restartSession(self):
        self.match.newMatch()
        self.playersSocketStack = []
        self.numberOfPlayers = 0

    def __tellPlayersEndOfSession(self):
        message = "SESSION FINISHED"
        self.sendMessage(publicMsg = message)

    def __playersConnection(self):
        thread_conexoes = threading.Thread(target=self.__handlePlayersConnection)
        thread_conexoes.start()

    def __handlePlayersConnection(self):
        while True:
            if len(self.playersSocketStack) == 0: self.event.wait() # Await until there is a player in playersSocketStack

            while self.isPossibleToConnect() and len(self.playersSocketStack) > 0:
                playerSocket = self.playersSocketStack.pop()
                self.numberOfPlayers += 1
                
                thread = threading.Thread(target=self.__awaitsPlayerStatus, args=(playerSocket,))
                thread.start()
                print("Cliente conectado na sessão", {self.sessionId})

            self.event.clear()

    """
        Awaits for the player to type "Pronto" or "Sair"
        "Pronto" will put it into the array of players
        "Sair" will not let the player play the game
    """
    def __awaitsPlayerStatus(self, playerSocket) -> None:
        # Esperar pelo nome do usuario
        name = self.recvMessage(playerSocket)

        if name == -1: return

        # Send user id
        player = Player(name, playerSocket)
        with self.mutex:
            self.match.addPlayer(player)

        self.__sendUserId(playerSocket, player.getId())

        # Waiting for pronto or quit
        
        prontoSair = self.__receiveReadyQuit(playerSocket)
        if prontoSair: 
            player.setReady(True)# Pronto
            self.sendMessage(player, privateMsg="Aguardando os demais jogadores...\n")

        else: self.__quit(player) # Quit

    """
        Send the user its Id
    """
    def __sendUserId(self, playerSocket, id) -> None:
        id = id.encode(FORMAT)
        playerSocket.sendall(id)

    """
        receive the player's answer 
        Return True if answer is 'pronto'. False if 'sair'
    """
    def __receiveReadyQuit(self, playerSocket) -> bool:
        buffer = self.recvMessage(playerSocket)
        return True if buffer == 'pronto' else False
    
    """
        Removes the player from the players array
    """
    def __quit(self, player) -> None:
        playerSocket = player.getSocket()
        with self.mutex:
            self.numberOfPlayers -= 1
            
            playerSocket.shutdown(socket.SHUT_RDWR)
            playerSocket.close()

            self.match.removePlayer(player)

    """
        Keeps on an infinite loop until all the connected players check that are ready to start the game
    """
    def __checkAllPlayersStatus(self) -> None:
        while self.match.checkReadyPlayers() == False:
            sleep(2)

    def searchPlayerBySocket(self, socketTarget) -> Player:
        for p in self.match.getPlayers():
            if p.getSocket() == socketTarget:
                return p     
    
    def sendMessage(self, player = None, publicMsg = "", privateMsg = "", waitingAnswer = False) -> None:
                
        playerId = player.getId() if player != None else ""
        messageDict = {
            "userId": playerId,
            "publicMsg" : publicMsg,
            "privateMsg" : privateMsg,
            "waitingAnswer" : waitingAnswer
        }

        msg = json.dumps(messageDict).encode(FORMAT)

        players = self.match.getPlayers()
        for p in players:
            if p.online == False: continue 
            try:
                p.getSocket().sendall(msg) 
            except (ConnectionResetError):
                print(f"O cliente {p.getName()} desconectou de forma inesperada")
                p.setOffline()
        sleep(0.2)  

    def recvMessage(self, socketTarget) -> str:
        try:
            while True:
                buffer = socketTarget.recv(BUFFER_SIZE).decode(FORMAT)
                if buffer:
                    return buffer
        except (ConnectionResetError):
            player = self.searchPlayerBySocket(socketTarget)
            player.setOffline()
            return '-1'