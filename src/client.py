import socket
from constants import *

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
        else:
            print(receivedData["privateMsg"])
    
    elif receivedData["userId"] != "":
        print('Esperando o próximo jogador')


# Play the match 
def playMatch(client_socket):
    #!ver uma forma de como a funcao vai ser finalizada
    # Receving information about the game
    while True: 
        buffer = None

        while True:
            buffer = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
            if buffer:
                break

        # print("="*50)
        # print(buffer)
        # print("="*50)

        jsons = buffer.split('}')
        jsons.pop(-1)
        jsons = [add + '}' for add in jsons]

        # print("="*50)
        # print(jsons)
        # print("="*50)

        for obj in jsons:
            receivedData = json.loads(obj)
            handleMessage(receivedData)



if __name__ == "__main__":
    # Defining the player's name
    name = input("Digite o seu nome: ")
    
    # Configuring a socket to use the protocol of internet and use the TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(CLIENT_ADDR_PORT)

    setPlayerName(client_socket, name)

    # Receiving the id that the server is going ot generate to the current player
    receiveId(client_socket)

    # Checking whether the player is ready to play or not
    readyQuit = readyQuitMessage(client_socket)

    if readyQuit == 'pronto':
        playMatch(client_socket)
        
    client_socket.close()