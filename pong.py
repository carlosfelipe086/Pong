# init / dependencias
import pygame

# init / janela
WIDTH = 1280
HEIGHT = 720
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong')

# init / parametros de jogabilidade
clock = pygame.time.Clock()
framerate = 60

active_game = True

pygame.init()

def frame_think():
    global active_game
    for event in pygame.event.get():
    # jogo / gerenciador de eventos
        if event.type == pygame.QUIT:
            print("pygame.QUIT")
            active_game = False
            break

def frame_render():
    window.fill( (0,0,0) )
    pygame.display.update()

while active_game:
    # jogo / definir framerate
    clock.tick(framerate)

    frame_think()
    frame_render()

pygame.quit()
        
