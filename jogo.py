import pygame
import socket
import pickle
import time  # Para medir o tempo de resposta

# Configuração da conexão
SERVER_IP = "..."
PORT = 5555

# Inicializa o Pygame
pygame.init()
LARGURA, ALTURA = 1920, 1080
tela = pygame.display.set_mode((LARGURA, ALTURA))

pygame.display.set_caption("Jogo da Cobrinha (LAN)")

# Cores
preto = (0, 0, 0)
roxo = (128, 0, 128)
verde = (0, 255, 0)
vermelho = (255, 0, 0)
azul = (0, 0, 255)
branco = (255, 255, 255)
cinza_claro = (211, 211, 211)
laranja = (255, 165, 0)  # Laranja
amarelo = (255, 255, 0)  # Amarelo
ciano = (0, 255, 255)    # Ciano
rosa = (255, 20, 147)    # Rosa

# Configuração do jogo
TAMANHO_BLOCO = 20
VELOCIDADE = 10

# Fonte personalizada
fonte_grauda = pygame.font.Font("RetroByte.ttf", 200)
fonte = pygame.font.Font("RetroByte.ttf", 30)
fonte_pequena = pygame.font.Font("RetroByte.ttf", 23)
fonte_pontos = pygame.font.Font("RetroByte.ttf", 20)
fonte_ping = pygame.font.Font("RetroByte.ttf", 15)

# Carregar imagem de fundo
background = pygame.image.load("background.jpg")
background = pygame.transform.scale(background, (LARGURA, ALTURA))

# Carregar imagem do sprite para comida
sprite_comida = pygame.image.load("ponto.png")
sprite_comida = pygame.transform.scale(sprite_comida, (TAMANHO_BLOCO, TAMANHO_BLOCO))  # Redimensiona para o tamanho do bloco

def desenha_texto(texto, x, y, cor=branco, fonte=fonte):
    render = fonte.render(texto, True, cor)
    tela.blit(render, (x, y))

# Conectar ao servidor
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((SERVER_IP, PORT))

# Função para calcular o ping
def calcular_ping():
    try:
        start_time = time.time()  # Marca o início do tempo
        cliente.send(pickle.dumps(("ping",)))  # Envia um pacote para o servidor
        cliente.recv(1024)  # Espera a resposta do servidor
        ping = (time.time() - start_time) * 1000  # Calcula o tempo em milissegundos
        return round(ping, 2)  # Retorna o ping arredondado
    except:
        return None  # Retorna None se houver erro de conexão

# Função do menu inicial
def menu_inicial():
    nome = ""
    cores = [verde, azul, vermelho, roxo, branco, laranja, amarelo, ciano, rosa]
    nomes_cores = ["Verde", "Azul", "Vermelho", "Roxo", "Branco", "Laranja", "Amarelo", "Ciano", "Rosa"]
    indice_cor = 0
    rodando = True
    while rodando:
        tela.blit(background, (0, 0))  # Exibir fundo
        # Exibe o título do jogo
        desenha_texto("Snake Online", 380, 300, branco, fonte_grauda)

        desenha_texto("Digite seu nome e pressione Enter para comecar:", 600, 500, cinza_claro)
        desenha_texto(f"Nome: {nome}", 600, 550, cinza_claro)

        # Exibir a cor selecionada
        desenha_texto("Escolha sua cor:", 600, 600, cinza_claro)
        pygame.draw.circle(tela, cores[indice_cor], (830, 610), 20)  # Exibir círculo da cor
        desenha_texto(f"< {nomes_cores[indice_cor]} >", 785, 650, cinza_claro)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN and nome:
                    return nome, cores[indice_cor]  # Retorna nome e cor escolhida
                elif evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                elif evento.key == pygame.K_LEFT:
                    indice_cor = (indice_cor - 1) % len(cores)  # Alternar cor para esquerda
                elif evento.key == pygame.K_RIGHT:
                    indice_cor = (indice_cor + 1) % len(cores)  # Alternar cor para direita
                elif evento.unicode.isprintable():
                    nome += evento.unicode

# Obtém o nome e cor do jogador antes de iniciar
nome_jogador, cor_jogador = menu_inicial()

# Enviar nome e cor do jogador para o servidor
cliente.send(pickle.dumps(("nome_jogador", nome_jogador, cor_jogador)))

# Recebe ID do jogador e informações iniciais
estado = pickle.loads(cliente.recv(4096))
# Verifica se o estado contém os dados esperados
if isinstance(estado, tuple) and len(estado) == 4:
    player_id, comidas, nomes_jogadores, cores_jogadores = estado
else:
    print("Erro: Dados recebidos não estão no formato esperado.")
    exit()

# Estado do jogo
cobra = [(LARGURA // 4, ALTURA // 2)]
direcao = (0, -TAMANHO_BLOCO)
crescer = False 

# Dicionário de pontos de cada jogador
pontos_jogadores = {player_id: 0}

def desenha_cobrinha(cobra, cor, nome):
    for parte in cobra:
        pygame.draw.rect(tela, cor, [parte[0], parte[1], TAMANHO_BLOCO, TAMANHO_BLOCO])
    desenha_texto(nome, cobra[0][0] - 10, cobra[0][1] + 15, branco, fonte_pequena)

def desenha_tabela_pontos():
    y_offset = 50  # Posição inicial no eixo Y
    for pid, pontos in pontos_jogadores.items():
        nome_jogador = nomes_jogadores.get(pid, "Jogador")
        desenha_texto(f"{nome_jogador}: {pontos} pontos", LARGURA - 150, y_offset, cinza_claro, fonte_pontos)
        y_offset += 30  # Move a posição Y para a próxima linha

# Função para exibir o ping no canto inferior esquerdo
def desenha_ping(ping):
    if ping is not None:
        desenha_texto(f"Ping: {ping} ms", 20, 20, branco, fonte_ping)
    else:
        desenha_texto("Sem conexão", 20, 20, vermelho, fonte_ping)

# Função de tela de "Você morreu"
def tela_de_morte(pontos):
    rodando = True
    while rodando:
        tela.fill(preto)
        desenha_texto("Voce morreu", LARGURA // 2 - 630, ALTURA // 3, vermelho, fonte_grauda)
        desenha_texto(f"Pontuacao: {pontos}", LARGURA // 2 - 100, ALTURA // 2, branco, fonte)
        desenha_texto("Pressione R para Recomecar ou ESC para Sair", LARGURA // 2 - 300, ALTURA // 1.5, branco, fonte)
        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return "recomeçar"
                elif evento.key == pygame.K_ESCAPE:
                    return "sair"

rodando = True
clock = pygame.time.Clock()

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                rodando = False
            elif evento.key == pygame.K_LEFT and direcao != (TAMANHO_BLOCO, 0):
                direcao = (-TAMANHO_BLOCO, 0)
            elif evento.key == pygame.K_RIGHT and direcao != (-TAMANHO_BLOCO, 0):
                direcao = (TAMANHO_BLOCO, 0)
            elif evento.key == pygame.K_UP and direcao != (0, TAMANHO_BLOCO):
                direcao = (0, -TAMANHO_BLOCO)
            elif evento.key == pygame.K_DOWN and direcao != (0, -TAMANHO_BLOCO):
                direcao = (0, TAMANHO_BLOCO)

    cabeca = (cobra[0][0] + direcao[0], cobra[0][1] + direcao[1])
    
    if cabeca in cobra or cabeca[0] < 0 or cabeca[0] >= LARGURA or cabeca[1] < 0 or cabeca[1] >= ALTURA:
        # Jogador morreu
        resultado = tela_de_morte(pontos_jogadores[player_id])
        if resultado == "recomeçar":
            # Reiniciar o jogo
            cobra = [(LARGURA // 4, ALTURA // 2)]
            direcao = (0, -TAMANHO_BLOCO)
            crescer = False
            pontos_jogadores[player_id] = 0
        elif resultado == "sair":
            rodando = False
        continue

    cobra.insert(0, cabeca)

    if cabeca in comidas:
        cliente.send(pickle.dumps(("comida_consumida", cabeca)))  
        crescer = True  

        # Atualiza os pontos do jogador
        pontos_jogadores[player_id] += 10

    if not crescer:
        cobra.pop()  
    else:
        crescer = False  

    cliente.send(pickle.dumps({"player_id": player_id, "cobra": cobra}))

    try:
        estado = pickle.loads(cliente.recv(4096))
        comidas = estado["comidas"]
        jogadores = estado["jogadores"]
        nomes_jogadores = estado["nomes_jogadores"]
        cores_jogadores = estado["cores_jogadores"]
    except:
        pass

    # Desenha a tela
    tela.blit(background, (0, 0))  # Desenhar fundo

    for pid, corpo in jogadores.items():
        cor = cores_jogadores.get(pid, verde)  # Usa a cor do jogador, ou verde por padrão
        desenha_cobrinha(corpo, cor, nomes_jogadores.get(pid, ""))

    # Desenhar as comidas com o sprite
    for comida in comidas:
        tela.blit(sprite_comida, (comida[0], comida[1]))  # Desenhar o sprite na posição da comida

    # Desenhar a tabela de pontos no canto superior direito
    desenha_tabela_pontos()

    # Exibir o ping
    ping = calcular_ping()
    desenha_ping(ping)

    pygame.display.update()
    clock.tick(VELOCIDADE)

cliente.close()
pygame.quit()
