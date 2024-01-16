import socket
import json

using_ngrok = False

SERVER_ADDR_PORT = None
CLIENT_ADDR_PORT = None

LOCAL_PORT = 9999
LOCAL_SERVER = '0.0.0.0'
SERVER_ADDR_PORT = (LOCAL_SERVER, LOCAL_PORT)

NGROK_ADDR = "0.tcp.sa.ngrok.io"

if using_ngrok:
    NGROK_PORT  = 15770
    CLIENT_ADDR_PORT = (NGROK_ADDR, NGROK_PORT )

else:
    server = socket.gethostbyname(socket.gethostname())
    CLIENT_ADDR_PORT = (server, LOCAL_PORT)



BUFFER_SIZE = 4096
FORMAT = 'utf-8'
