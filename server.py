import socket
import threading
import pickle
import random

# Configuração do servidor
HOST = "0.0.0.0"
PORT = 5555

# Configurações do jogo
LARGURA, ALTURA = 1920, 1080
TAMANHO_BLOCO = 20

# Variáveis globais
jogadores = {}
nomes_jogadores = {}
cores_jogadores = {}  # Dicionário para armazenar as cores dos jogadores
comidas = [(random.randint(0, (LARGURA // TAMANHO_BLOCO) - 1) * TAMANHO_BLOCO, 
            random.randint(0, (ALTURA // TAMANHO_BLOCO) - 1) * TAMANHO_BLOCO) for _ in range(10)]

lock = threading.Lock()

def handle_client(conn, addr, player_id):
    global jogadores, comidas, nomes_jogadores, cores_jogadores

    print(f"[NOVA CONEXÃO] Jogador {player_id} conectado de {addr}")
    
    # Recebe o nome e a cor do jogador
    try:
        data = pickle.loads(conn.recv(4096))
        if isinstance(data, tuple) and data[0] == "nome_jogador":
            nomes_jogadores[player_id] = data[1]
            cores_jogadores[player_id] = data[2]  # Recebe a cor do jogador
    except:
        pass

    # Envia para o cliente o ID, comidas e os jogadores (incluindo cores)
    conn.send(pickle.dumps((player_id, comidas, nomes_jogadores, cores_jogadores)))

    while True:
        try:
            dados = pickle.loads(conn.recv(4096))
            if not dados:
                break

            with lock:
                if isinstance(dados, dict):
                    jogadores[player_id] = dados["cobra"]
                elif isinstance(dados, tuple) and dados[0] == "comida_consumida":
                    comidas.remove(dados[1])
                    comidas.append((random.randint(0, (LARGURA // TAMANHO_BLOCO) - 1) * TAMANHO_BLOCO, 
                                    random.randint(0, (ALTURA // TAMANHO_BLOCO) - 1) * TAMANHO_BLOCO))

            # Envia o estado do jogo (jogadores, comidas, nomes e cores)
            for cliente in jogadores.keys():
                try:
                    conn.sendall(pickle.dumps({"jogadores": jogadores, "comidas": comidas, "nomes_jogadores": nomes_jogadores, "cores_jogadores": cores_jogadores}))
                except:
                    pass

        except:
            break

    with lock:
        if player_id in jogadores:
            del jogadores[player_id]
        if player_id in nomes_jogadores:
            del nomes_jogadores[player_id]
        if player_id in cores_jogadores:
            del cores_jogadores[player_id]
    
    conn.close()
    print(f"[DESCONECTADO] Jogador {player_id} saiu.")

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("[SERVIDOR INICIADO] Aguardando conexões...")

    player_id = 0
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr, player_id)).start()
        player_id += 1

start()
