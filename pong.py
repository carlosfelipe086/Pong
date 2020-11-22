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
# init / parametros de jogabilidade
clock = pygame.time.Clock()
# taxa de frames por segundo
framerate = 60
# tempo de execução para cada frame
frametime = 0
# contagem de frames
framecount = 0

# init / estados de jogo
STATE_MENU = 1 << 0
STATE_PLAYING = 1 << 1
STATE_ROUND_START = 1 << 2
STATE_QUIT = 1 << 3
game_state = STATE_MENU# taxa de frames por segundo
framerate = 60
# tempo de execução para cada frame
frametime = 0
# contagem de frames
framecount = 0

# init / estados de jogo
STATE_MENU = 1 << 0
STATE_PLAYING = 1 << 1
STATE_ROUND_START = 1 << 2
STATE_QUIT = 1 << 3
game_state = STATE_MENU

# init / estado do mouse
# [movement, mousedown, mouseup]
mouse_state = [False, False, False]

pygame.init()
pygame.font.init()

# init / poderes possíveis
# clairvoyance : quando a bola está vindo na direção do jogador, ele pode ver a trajetória dela
# strength : quando o usuário bate na bola, o impacto é mais forte
# haste : o personagem se move mais rápido
# exhaust : o inimigo se move mais devagar
powers = ["clairvoyance", "strength", "haste", "exhaust"]

# init / parametros globais
ball_max_vertical_speed = 30
ball_max_horizontal_speed = 15
ball_launch_speed = 5
game_score_win_condition = 10

# classe de vetores 2d
class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # overload de operador para soma, multiplicação e divisão
    # compatível com outro vetor, ou com um número inteiro/float    
    def __add__(self, other):
    if type(other) == Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)
    else:
        return Vector2D(self.x + other, self.y + other)

    def __sub__(self, other):
        if type(other) == Vector2D:
            return Vector2D(self.x - other.x, self.y - other.y)
        else:
            return Vector2D(self.x - other, self.y - other)

    def __mul__(self, other):
        if type(other) == Vector2D:
            return Vector2D(self.x * other.x, self.y * other.y)
        else:
            return Vector2D(self.x * other, self.y * other)

    def __truediv__(self, other):
        if type(other) == Vector2D:
            return Vector2D(self.x / other.x, self.y / other.y)
        else:
            return Vector2D(self.x / other, self.y / other)

    def length(self):
        return self.x**2 + self.y**2

def frame_think():
    global game_state, players, mouse_state

    # resetar o estado do mouse antes de passar pelo buffer de eventos nesse frame
    mouse_state = [False, False, False]

    for event in pygame.event.get():
    # jogo / buffer de eventos
        if event.type == pygame.MOUSEMOTION:
            mouse_state[0] = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_state[1] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_state[2] = True

        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            for player in players:
                # atualizar as teclas pressionadas para cada jogador
                player.update_keys(event.key, event.type == pygame.KEYDOWN)

        if event.type == pygame.QUIT:
            # caso o cliente tente fechar o aplicativo, executar a sequencia abaixo
            print("pygame.QUIT")
            game_state = STATE_QUIT
            break

    for player in players:
        # executar estágio de 'think' para cada jogador
        player.frame_think()

    ball.frame_think()
    #if framecount % 3 == 0:
    simulated.frame_think()
    world.frame_think()

def frame_render():
    global players

    world.frame_render()
    
    for player in players:
        # executar estágio de 'render' para cada jogador
        player.frame_render()

    simulated.frame_render()
    ball.frame_render()    

while game_state != STATE_QUIT:
    # jogo / definir framerate, atualizar frametime
    frametime = clock.tick(framerate)
    #print("framerate: {0} | tempo desde o último frame: {1}ms (estável em {2}ms)".format(int(1/(frametime/1000)), frametime/1000.0, 1.0/framerate))

    # background preto
    window.fill( (0,0,0) )

    # jogo / diferenciação de estados
    if game_state == STATE_MENU:
        # resetar o estado do mouse antes de passar pelo buffer de eventos nesse frame
        mouse_state = [False, False, False]

        for event in pygame.event.get():
        # jogo / buffer de eventos
            if event.type == pygame.MOUSEMOTION:
                mouse_state[0] = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_state[1] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_state[2] = True
            if event.type == pygame.QUIT:
                # caso o cliente tente fechar o aplicativo, executar a sequencia abaixo
                print("pygame.QUIT")
                game_state = STATE_QUIT
                break

        world.frame_think()
        world.frame_render()
        menu.window_handler(retro_font)
    elif game_state == STATE_PLAYING or game_state == STATE_ROUND_START:
        # execução de estágios do frame
        if game_state == STATE_ROUND_START:
            world.should_update = True
            ball.reset_velocity()
            ball.origin = Vector2D(WIDTH/2, HEIGHT/2)
            ball.state = ball.states.index("frozen")
            time.sleep(1)
            ball.state = ball.states.index("active")
            simulated.apply_simulated_data([ball.origin, ball.velocity, ball.theta, ball.time_elapsed, ball.collision_scalars, ball.state])
            game_state = STATE_PLAYING


        frame_think()
        frame_render()
    else:
        pass

    pygame.display.update()
    framecount += 1

pygame.quit()