# init / dependencias
import pygame
import math
import random
import time
from copy import copy

# init / janela
WIDTH = 1280
HEIGHT = 720
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong')

# init / parametros de jogabilidade
clock = pygame.time.Clock()
# taxa de frames por segundo
framerate = 60

# init / estados de jogo
STATE_MENU = 1 << 0
STATE_PLAYING = 1 << 1
STATE_ROUND_START = 1 << 2
STATE_QUIT = 1 << 3
game_state = STATE_MENU

pygame.init()

# classe de vetores 2d
class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def frame_think():
    global game_state

    for event in pygame.event.get():
    # jogo / buffer de eventos
        if event.type == pygame.QUIT:
            # caso o cliente tente fechar o aplicativo, executar a sequencia abaixo
            print("pygame.QUIT")
            game_state = STATE_QUIT
            break

def frame_render():
    return

while game_state != STATE_QUIT:
    # jogo / definir framerate
    clock.tick(framerate)
    #print("framerate: {0} | tempo desde o último frame: {1}ms (estável em {2}ms)".format(int(1/(frametime/1000)), frametime/1000.0, 1.0/framerate))

    # background preto
    window.fill( (0,0,0) )

    # jogo / diferenciação de estados
    if game_state == STATE_MENU:
        for event in pygame.event.get():
        # jogo / buffer de eventos
            if event.type == pygame.QUIT:
                # caso o cliente tente fechar o aplicativo, executar a sequencia abaixo
                print("pygame.QUIT")
                game_state = STATE_QUIT
                break

    elif game_state == STATE_PLAYING or game_state == STATE_ROUND_START:
        # execução de estágios do frame
        if game_state == STATE_ROUND_START:
            # alterações antes do round recomeçar + tempo de pausa antes da bola se mover
            time.sleep(1)
            game_state = STATE_PLAYING


        frame_think()
        frame_render()
    else:
        pass

    pygame.display.update()

pygame.quit()
