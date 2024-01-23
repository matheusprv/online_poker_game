from constants import *
from server import Server

if __name__ == "__main__":

    server = Server()

    gameSession = server.createSession()

    if(gameSession == None): print("Não foi possível criar uma sessão de jogo")
    
    else: gameSession.startGame()





#! Criação de mais salas de jogo

# Servidor inicia
# Cria as sessões
# Cria thread pra ficar escutando as ações do usuário


# Durante o jogo
# Cada mensagem que vem do usuario tem uma id da sessão 
# A mensagem fica no servidor 
# Manda para uma fila de mensagem da sessao especifica
# A função da sessão ela vai ler essa fila 