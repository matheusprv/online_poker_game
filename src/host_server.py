from constants import *
from server import Server

if __name__ == "__main__":

    server = Server()

    gameSession = server.createSession()

    if(gameSession == None): print("Não foi possível criar uma sessão de jogo")
    
    else: gameSession.startGame()

#! Enviar o relatório da partida
#! Enviar mais informações para os usuários sobre o andamento das partidas
#! Criação de mais salas de jogo
#! ver uma forma de como a funcao "playMatch" do client.py vai ser finalizada
#! Verificar partida começando com somente um jogador caso ele dê pronto e op jogo nao começa quando outro se conecta