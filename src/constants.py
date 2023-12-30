import socket
import json

using_ngrok = False

BUFFER_SIZE = 4096

SERVER_ADDR_PORT = None
CLIENT_ADDR_PORT = None

if using_ngrok:
    LOCAL_PORT = 9999
    LOCAL_SERVER = '0.0.0.0'
    SERVER_ADDR_PORT = (LOCAL_SERVER, LOCAL_PORT)
    
    NGROK_PORT  = 15770
    NGROK_ADDR = "0.tcp.sa.ngrok.io"
    CLIENT_ADDR_PORT = (NGROK_ADDR, NGROK_PORT )

else:
    LOCAL_PORT = 9999
    LOCAL_SERVER = '0.0.0.0'
    SERVER_ADDR_PORT = (LOCAL_SERVER, LOCAL_PORT)

    SERVER = socket.gethostbyname(socket.gethostname())
    CLIENT_ADDR_PORT = (SERVER, LOCAL_PORT)


FORMAT = 'utf-8'
