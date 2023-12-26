""""
Ficar no while da main enquanto espera todos se conectarem
a cada conexão cria uma thread para ficar esperando o pronto do usuário
quando todos colocarem pronto ou ter o número de players máximo, então o jogo começa
"""""



from constants import *
from match import Match
from player import Player
import threading
from time import sleep

current_number_of_players = 0
MAXIMUN_NUMBER_OF_PLAYERS = 8
sockets_ids = []
mutex = threading.Lock()


def receiveUserName(playerSocket) -> str:
    while True:
        buffer = playerSocket.recv(BUFFER_SIZE).decode(FORMAT)
        if buffer:
            return buffer

def sendUserId(playerSocket, id) -> None:
    id = id.encode(FORMAT)
    playerSocket.sendall(id)

def receiveReadyQuit(playerSocket) -> str:
    while True:
        buffer = playerSocket.recv(BUFFER_SIZE).decode(FORMAT)

        if buffer == 'pronto':
            return True
        elif buffer == 'quit':
            return False

# Recebe o nome do cliente e verifica se ele ta pronto 
def conexao(playerSocket, match):

    # Esperar pelo nome do usuario
    name = receiveUserName(playerSocket)

    # Enviar id
    player = Player(name, playerSocket)
    with mutex:
        match.addPlayer(player)

    sendUserId(playerSocket, player.getId())

    # Esperando pelo pronto ou quit
    # Pronto
    if receiveReadyQuit:
        player.setReady(True)
    
    # Quit
    else:
        with mutex:
            sockets_ids.remove(playerSocket)
            current_number_of_players -= 1
            
            playerSocket.shutdown(playerSocket.SHUT_RDWR)
            playerSocket.close()

            match.removePlayer(player)


def connectClients(main_socket, match):
    # Putting the socket in listening mode
    main_socket.listen(MAXIMUN_NUMBER_OF_PLAYERS)

    # Waiting for the players to connect and 
    while len(sockets_ids) < MAXIMUN_NUMBER_OF_PLAYERS:
        print("Esperando conexão")

        new_socket, addr = main_socket.accept()

        with mutex:
            # The game has alredy began, so the new player can't enter
            if(match.isInProgress()): break

            sockets_ids.append(new_socket)
            current_number_of_players += 1

            thread = threading.Thread(target=conexao, args=(new_socket, match))
            thread.start()
            print("Cliente conectado")


if __name__ == "__main__":
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = ('0.0.0.0', PORT)
    main_socket.bind(server_addr)

    match = Match()
    
    thread_conexoes = threading.Thread(target=connectClients, args=(main_socket, match))
    thread_conexoes.start()

    #! A thread pode ficar presa no accept, mas todos os jogadores colocaram pronto
    while match.checkReadyPlayers() == False:
        sleep(2)

    match.startGame()

    