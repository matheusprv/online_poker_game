import socket
import threading
from constants import *

NUM_THREADS = 8
sockets_threads_ids = [-1] * NUM_THREADS
mutex = threading.Lock()

class Th_data:
    def __init__(self, thread_no, sock) -> None:
        self.thread_no = thread_no
        self.sock = sock

def conexao(thread):
    # Escutando informação do sistema
    while True:
        # Esperando receber algo
        print("Esperando Mensagem do cliente...")
        data = thread.sock.recv(1024).decode('utf-8')

        if not data:
            break

        print(f"Mensagem recebida do cliente = {data}")

        # Enviando a mensagem para os clientes conectados ao servidor
        if 'quit' not in data:
            print("Enviando mensagem para os outros clientes")

            with mutex:
                for th in sockets_threads_ids:
                    if th != -1 and th != thread.sock:
                        th.sendall(data.encode('utf-8'))
        
        # A mensagem possuía um quit, então finaliza a conexão do cliente com esse servidor
        else:
            break

    with mutex:
        sockets_threads_ids[thread.thread_no] = -1

    print("Fechando a conexão...")
    thread.sock.shutdown(socket.SHUT_RDWR)
    thread.sock.close()

if __name__ == "__main__":
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = ('0.0.0.0', PORT)
    main_socket.bind(server_addr)

    # Colocando o socket em modo de escuta
    main_socket.listen(NUM_THREADS)
    print("Listening")

    threads = []
    for i in range(NUM_THREADS):
        print("Esperando conexao do cliente....")

        # Neste momento o processo fica bloqueado à espera de que alguém se conecte
        # Socket que será usado para conectar com o cliente e endereço do mesmo
        new_socket, addr = main_socket.accept()

        # Atualiza a lista de threads colocando um novo soquet
        with mutex:
            sockets_threads_ids[i] = new_socket

        # Cria uma nova thread e chama a função de conexão
        thread = threading.Thread(target=conexao, args=(Th_data(i, new_socket),))
        thread.start()  # Executa a thread
        threads.append(thread)
        print("Cliente conectou.")

    print("Abriu todas as threads. Esperando a thread terminar para fechar o servidor.")

    # Esperando todas as threads serem finalizadas
    for thread in threads:
        thread.join()

    main_socket.close()