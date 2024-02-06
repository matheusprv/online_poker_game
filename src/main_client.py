import socket
from constants import *
import sys
from time import sleep

user_id = None
userName = None

def configNgrok(argv):
    if len(argv) == 1: return 

    ngrokPort = None
    # try:
    ngrokPort = int(argv[1])
    global CLIENT_ADDR_PORT
    CLIENT_ADDR_PORT = (NGROK_ADDR, ngrokPort)

def receiveMessage(client_socket):
    while True:
        buffer = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
        if buffer:
            return buffer

def processJSON(buffer):
    jsons = buffer.split('}')
    jsons.pop(-1)
    jsons = [add + '}' for add in jsons]
    return jsons

# Define the player's name
def sendPlayerNameToServer(client_socket, name):
    name = name.encode(FORMAT)
    client_socket.sendall(name)

# Receive the player id from the server
def receiveIdFromServer(client_socket):
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
    if receivedData["publicMsg"] == "SESSION FINISHED" or (receivedData["privateMsg"] == "SESSION FINISHED" and receivedData["userId"] == user_id):
        print("A sessão que você estava conectado foi finalizada.")
        return "SESSION FINISHED"
    if receivedData["privateMsg"] == "SESSION REMOVED" and receivedData["userId"] == user_id:
        print("Você foi removido da sessão pois ficou sem fichas")
        return "SESSION FINISHED"


    if(receivedData["publicMsg"] != ""):
        print(receivedData["publicMsg"])

    # check whose turn it is
    if receivedData["userId"] == user_id:
        if(receivedData["waitingAnswer"] == True):
            msg = input(receivedData["privateMsg"])
            msg = msg.encode(FORMAT)
            client_socket.sendall(msg)
            
            if msg == "quit": return "quit"
        
        else:
            print(receivedData["privateMsg"])
    
    elif receivedData["userId"] != "" and receivedData["privateMsg"] != "":
        print('Esperando o próximo jogador')


# Play the match 
def playMatch(client_socket):
    # Receving information about the game

    returnValueHandleMessage = ""
    while returnValueHandleMessage != "quit" and returnValueHandleMessage != "SESSION FINISHED": 
        
        buffer = receiveMessage(client_socket)        
        jsons = processJSON(buffer)

        for obj in jsons:
            receivedData = json.loads(obj)
            returnValueHandleMessage = handleMessage(receivedData)
            
            if returnValueHandleMessage == "quit" or returnValueHandleMessage == "SESSION FINISHED":
                break
    
    return returnValueHandleMessage


def chooseSection(client_socket):
    while True:
        buffer = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
        if buffer:
            if buffer == "SESS ACK": 
                break
            elif buffer == "SESS NACK":
                print("Não foi possível se conectar à sessão, pois está cheia ou o jogo já começou.")
                print("Selecione outra ou tente novamente mais tarde.")
            else:
                sess = input(buffer)
                client_socket.sendall(sess.encode(FORMAT))



if __name__ == "__main__":
    
    configNgrok(sys.argv)
    
    # Defining the player's name
    name = input("Digite o seu nome: ")

    readyQuit = ""
    while readyQuit != 'quit':
        # Configuring a socket to use the protocol of internet and use the TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(CLIENT_ADDR_PORT)

        chooseSection(client_socket)
        sendPlayerNameToServer(client_socket, name)
        receiveIdFromServer(client_socket)

        readyQuit = readyQuitMessage(client_socket)

        if readyQuit == 'pronto':
            readyQuit = playMatch(client_socket)
        
        print("Desconectando da sessão...")

        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()

        if readyQuit != "quit":
            sleep(1)