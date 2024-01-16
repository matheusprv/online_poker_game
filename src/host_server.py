from constants import *
from server import Server

if __name__ == "__main__":

    server = Server()

    gameSession = server.createSession()

    if(gameSession == None): print("Não foi possível criar uma sessão de jogo")
    
    else: gameSession.startGame()

#! Enviar o relatório da partida
#! Criação de mais salas de jogo