import socket
from constants import *
import sys

user_id = None
userName = None

# Define the player's name
def setPlayerName(client_socket, name):
    name = name.encode(FORMAT)
    client_socket.sendall(name)

# Receive the player id from the server
def receiveId(client_socket):
    while True:
        buffer = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
        if buffer:
            global user_id
            user_id = buffer
            break

# The player will input 'Pronto' to start the game or 'Quit' to quit the game
def readyQuitMessage(client_socket):
    readyQuit = "" 
    
    while readyQuit != 'pronto' and readyQuit != 'quit':
        readyQuit = input("Digite 'Pronto' para começar ou 'Quit' para sair do jogo: ").lower()

    # Send an answer to the server
    client_socket.sendall(readyQuit.encode(FORMAT))

    return readyQuit

def handleMessage(receivedData):
    if(receivedData["publicMsg"] != ""):
        print(receivedData["publicMsg"])

    # check whose turn it is
    if receivedData["userId"] == user_id:
        if(receivedData["waitingAnswer"] == True):
            msg = input(receivedData["privateMsg"])
            msg = msg.encode(FORMAT)
            client_socket.sendall(msg)
            
            if msg == "quit":
                return "quit"
        
        else:
            print(receivedData["privateMsg"])
    
    elif receivedData["userId"] != "":
        print('Esperando o próximo jogador')


# Play the match 
def playMatch(client_socket):
    # Receving information about the game

    returnValue = ""
    while returnValue != "quit": 
        buffer = None

        while True:
            buffer = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
            if buffer:
                break

        jsons = buffer.split('}')
        jsons.pop(-1)
        jsons = [add + '}' for add in jsons]

        for obj in jsons:
            receivedData = json.loads(obj)
            returnValue = handleMessage(receivedData)
            
            if returnValue == "quit":
                break


def configNgrok(argv):
    if len(argv) == 1: return 

    ngrokPort = None
    # try:
    ngrokPort = int(argv[1])
    global CLIENT_ADDR_PORT
    CLIENT_ADDR_PORT = (NGROK_ADDR, ngrokPort)

    # except:
    #     print("Não foi possível identificar a porta do NGrok.\nUsando a conexão local.")
    #     return

if __name__ == "__main__":
    
    configNgrok(sys.argv)
    
    # Defining the player's name
    name = input("Digite o seu nome: ")
    
    # Configuring a socket to use the protocol of internet and use the TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(CLIENT_ADDR_PORT)

    print("Enviando o nome")
    setPlayerName(client_socket, name)

    # Receiving the id that the server is going ot generate to the current player
    print("Esperando pelo ID")
    receiveId(client_socket)

    # Checking whether the player is ready to play or not
    readyQuit = readyQuitMessage(client_socket)

    if readyQuit == 'pronto':
        playMatch(client_socket)
        
    client_socket.close()