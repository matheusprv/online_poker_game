from constants import *
from match import Match
from time import sleep
from player import Player
import threading


class Session:

    mutex = threading.Lock()
    MAXIMUN_NUMBER_OF_PLAYERS = 8
    numberOfPlayers = 0
    sockets_ids = []

    def __init__(self, main_socket) -> None:
        self.server_socket = main_socket
        self.match = Match(self.sendMessage, self.recvMessage)        

    """
        Make threads to await for players connection and their answers to get ready to start the game
    """
    def __playersConnection(self) -> None:
        thread_conexoes = threading.Thread(target=self.__awaitClientsConnections)
        thread_conexoes.start()

    #TODO: Enviar mensagem de erro para o usuário além do break
    """
        Awaits for the players to connect and add them into the match's player's array
        If the numberOfPlayers is equals to the MAXIMUN_NUMBER_OF_PLAYERS or the match started, reject the addition to the match
    """
    def __awaitClientsConnections(self) -> None:
        # Waiting for the players to connect and get ready for the match 
        while self.numberOfPlayers < self.MAXIMUN_NUMBER_OF_PLAYERS and not self.match.isInProgress():
            print("Esperando conexão")

            playerSocket, _ = self.server_socket.accept()

            with self.mutex:
                # The game has alredy began, so the new player can't join
                print(f"Conexão")
                if self.match.isInProgress() or self.numberOfPlayers == self.MAXIMUN_NUMBER_OF_PLAYERS: 
                    playerSocket.shutdown(playerSocket.SHUT_RDWR)
                    playerSocket.close()
                    break

                self.sockets_ids.append(playerSocket)
                self.numberOfPlayers += 1
                
                thread = threading.Thread(target=self.__awaitsPlayerStatus, args=(playerSocket,))
                thread.start()
                print("Cliente conectado")        
        
        print("\nNão aceitando mais conexões\n")

    """
        Awaits for the player to type "Pronto" or "Sair"
        "Pronto" will put it into the array of players
        "Sair" will not let the player play the game
    """
    def __awaitsPlayerStatus(self, playerSocket) -> None:
        # Esperar pelo nome do usuario
        name = self.recvMessage(playerSocket)

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
                self.sockets_ids.remove(playerSocket)
                numberOfPlayers -= 1
                
                playerSocket.shutdown(playerSocket.SHUT_RDWR)
                playerSocket.close()

                self.match.removePlayer(player)

    """
        Keeps on an infinite loop until all the connected players check that are ready to start the game
    """
    def __checkAllPlayersStatus(self) -> None:
        while self.match.checkReadyPlayers() == False:
            sleep(2)

    """
        Awaits for all players connect to the session.
        After all of them are connected and checked as 'pronto' the game begins
    """
    def startGame(self) -> None:
        self.__playersConnection()
        self.__checkAllPlayersStatus()
        self.match.startGame()



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

        for p in self.match.getPlayers():
            p.getSocket().sendall(msg) 
        
        sleep(0.2)  

    def recvMessage(self, socketTarget) -> str:
        while True:
            buffer = socketTarget.recv(BUFFER_SIZE).decode(FORMAT)
            if buffer:
                if buffer == "quit":
                    self.__quit(self.searchPlayerBySocket(socketTarget))

                else:
                    return buffer
