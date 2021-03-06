# init / dependencias
import geometry
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
pygame.mixer.init()

# init / registrar sons
sound_score = pygame.mixer.Sound('audio/pong_score.wav')
sound_hit = pygame.mixer.Sound('audio/pong_hit.wav')

# init / poderes possíveis
# clairvoyance : quando a bola está vindo na direção do jogador, ele pode ver a trajetória dela
# strength : quando o usuário bate na bola, o impacto é mais forte
# haste : o personagem se move mais rápido
# exhaust : o inimigo se move mais devagar
powers = ["none", "clairvoyance", "strength", "haste", "exhaust"]

# init / parametros globais
ball_max_vertical_speed = 15
ball_max_horizontal_speed = 40
ball_launch_speed = 5
game_score_win_condition = 3

# lerp para suavizar a transição de valores
def lerp(a, b, fac):
    return a + (b-a)*fac

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

    def __sub__(self, other):
        if type(other) == Vector2D:
            return Vector2D(self.x - other.x, self.y - other.y)
        else:
            return Vector2D(self.x - other, self.y - other)

    def length(self):
        return self.x**2 + self.y**2

class RetroFont:
    # RETRO FONT © 2013 Larry Serflaten
    # originalmente escrita em Processing.js
    # http://www.khanacademy.org/cs/retro-font/2583796852

    def initialize_letters(self):
        # each string holds the vertical representation of each
        # glyph (in 2-byte hexidecimal notation).
        # 33-47 = "!"#$&%'()*+,-./"
        self.letters[33] = "0018181818001800"  # !
        self.letters[34] = "0066666600000000"  # "
        self.letters[35] = "0066FF6666FF6600"  # # ...
        self.letters[36] = "183E603C067C1800"
        self.letters[37] = "00666C1830664600"
        self.letters[38] = "1C361C386F663B00"
        self.letters[39] = "0018181800000000"
        self.letters[40] = "000E1C18181C0E00"
        self.letters[41] = "0070381818387000"
        self.letters[42] = "00663CFF3C660000"
        self.letters[43] = "0018187E18180000"
        self.letters[44] = "0000000000181830"
        self.letters[45] = "0000007E00000000"
        self.letters[46] = "0000000000181800"
        self.letters[47] = "00060C1830604000"
        # 48-57 = 0-9
        self.letters[48] = "003C666E76663C00"  # 0
        self.letters[49] = "0018381818187E00"  # 1
        self.letters[50] = "003C660C18307E00"  # 2 ...
        self.letters[51] = "007E0C180C663C00"
        self.letters[52] = "000C1C3C6C7E0C00"
        self.letters[53] = "007E607C06663C00"
        self.letters[54] = "003C607C66663C00"
        self.letters[55] = "007E060C18303000"
        self.letters[56] = "003C663C66663C00"
        self.letters[57] = "003C663E060C3800"
        # 58-64 = ":;<=>?@"
        self.letters[58] = "0000181800181800"
        self.letters[59] = "0000181800181830"
        self.letters[60] = "060C1830180C0600"
        self.letters[61] = "00003E00003E0000"
        self.letters[62] = "6030180C18306000"
        self.letters[63] = "003C660C18001800"
        self.letters[64] = "003C666E6E603E00"
        # 65-90 = A-Z
        self.letters[65] = "00183C66667E6600"  # A
        self.letters[66] = "007C667C66667C00"  # B
        self.letters[67] = "003C666060663C00"  # C ...
        self.letters[68] = "00786C66666C7800"
        self.letters[69] = "007E607C60607E00"
        self.letters[70] = "007E607C60606000"
        self.letters[71] = "003E60606E663E00"
        self.letters[72] = "0066667E66666600"
        self.letters[73] = "007E181818187E00"
        self.letters[74] = "0006060606663C00"
        self.letters[75] = "00666C78786C6600"
        self.letters[76] = "0060606060607E00"
        self.letters[77] = "0063777F6B636300"
        self.letters[78] = "0066767E7E6E6600"
        self.letters[79] = "003C666666663C00"
        self.letters[80] = "007C66667C606000"
        self.letters[81] = "003C6666666C3600"
        self.letters[82] = "007C66667C6C6600"
        self.letters[83] = "003C603C06063C00"
        self.letters[84] = "007E181818181800"
        self.letters[85] = "0066666666667E00"
        self.letters[86] = "00666666663C1800"
        self.letters[87] = "0063636B7F776300"
        self.letters[88] = "0066663C3C666600"
        self.letters[89] = "0066663C18181800" 
        self.letters[90] = "007E0C1830607E00"
        # 91-96 = "[\]^_`"   #       ` added for completeness 
        self.letters[91] = "001E181818181E00"
        self.letters[92] = "00406030180C0600"
        self.letters[93] = "0078181818187800"
        self.letters[94] = "00081C3663000000"
        self.letters[95] = "000000000000FF00"
        self.letters[96] = "0018180C00000000"
        # 97-122 = a-z
        self.letters[97] = "00003C063E663E00"
        self.letters[98] = "0060607C66667C00"
        self.letters[99] = "00003C6060603C00"
        self.letters[100] = "0006063E66663E00"
        self.letters[101] = "00003C667E603C00"
        self.letters[102] = "000E183E18181800"
        self.letters[103] = "00003E66663E067C"
        self.letters[104] = "0060607C66666600"
        self.letters[105] = "0018003818183C00"
        self.letters[106] = "000600060606063C"
        self.letters[107] = "0060606C786C6600"
        self.letters[108] = "0038181818183C00"
        self.letters[109] = "0000667F7F6B6300"
        self.letters[110] = "00007C6666666600"
        self.letters[111] = "00003C6666663C00"
        self.letters[112] = "00007C66667C6060"
        self.letters[113] = "00003E66663E0606"
        self.letters[114] = "00007C6660606000"
        self.letters[115] = "00003E603C067C00"
        self.letters[116] = "00187E1818180E00"
        self.letters[117] = "0000666666663E00"
        self.letters[118] = "00006666663C1800"
        self.letters[119] = "0000636B7F3E3600"
        self.letters[120] = "0000663C183C6600"
        self.letters[121] = "00006666663E0C78"
        self.letters[122] = "00007E0C18307E00"
        # 123-126 = "{|}~"  # {} and ~ added for completeness
        self.letters[123] = "1C30306030301C00"
        self.letters[124] = "1818181818181818"
        self.letters[125] = "380C0C060C0C3800"
        self.letters[126] = "000070DB0E000000"

    def draw_letter(self, ltr, x, y, z, col):
        global window
        #ensure letters are prepared
        if len(self.letters.values()) == 0:
            self.initialize_letters()
        # get letter element (string)
        code = self.letters[ord(ltr[0])]

        # verify letter is properly defined
        if type(code) == str and len(code) == 16:
            # calc cell size from letter size
            s = math.floor( z / 8 )
            if s < 1:
                s = 1
            # vert loop
            for i in range(8):
                # get 2-byte hexidemal value
                seg = int(str("0x" + code[i+i : i+i+2]), 16)
                yy = y + (i * s)
                # horz loop
                for xx in range(x + (s * 7), -1, -s):
                    if seg & 1:
                        pygame.draw.rect(window, col, (xx, yy, s, s))
                    seg >>= 1

    # draw_words ( desenha o texto em estilo retro )
    # wrd : texto
    # x : origem x
    # y : origem y
    # z : tamanho do texto
    # col : cor em tuple (r, g, b, a)
    def draw_words(self, wrd, x, y, z, col):
        # validate input
        if type(wrd) == str:
            # calc size (multiple of 8) 
            s = math.floor( z / 8 ) * 8
            if s < 8:
                s = 8
            xx = int(x - (len(wrd) * (z/2)) + (len(wrd) / 2)); 
            # loop through word(s)
            for i in range(len(wrd)):
                self.draw_letter(wrd[i:i+1], xx, (y - z/2), s, col)
                xx += s

    def __init__(self):
        self.letters = {}
        self.initialize_letters()


class Button:
    def __init__(self, x, y, scale):
        self.width = 0
        self.height = 0
        # size serve para guardar os valores originais de altura e comprimento
        self.size = Vector2D(self.width, self.height)
        # scale define o crescimento do botão quando o jogador passa o seu mouse em cima dele
        self.scale = scale
        self.origin = Vector2D(x, y)
        self.should_update = True
        self.text = ""

    def update(self, x, y, scale):
        self.scale = scale
        self.origin = Vector2D(x, y)
        return self

    def create(self, retrofont, wrd):
        global window

        if wrd != self.text:
            self.text = wrd
            self.should_update = True
        
        self.size = Vector2D(len(wrd) * 25, 50)
        if abs(self.width - self.size.x) > self.scale or abs(self.height - self.size.y) > self.scale or self.should_update == True:
            self.width = self.size.x
            self.height = self.size.y
            self.should_update = False

        cursor_position = pygame.mouse.get_pos()
        mouse_over = False

        # compensamos pelo frametime, caso a framerate do programa fique abaixo do esperado
        lerp_factor = 0.1
        lerp_factor *= 1.0/(frametime/1000) * 1/framerate

        if (cursor_position[0] > self.origin.x - self.width/2 
        and cursor_position[0] < self.origin.x + self.width/2 
        and cursor_position[1] > self.origin.y - self.height/2 
        and cursor_position[1] < self.origin.y + self.height/2):
            self.width += (self.size.x + self.scale - self.width) * lerp_factor
            self.height += (self.size.y + self.scale - self.height) * lerp_factor
            mouse_over = True
        elif self.width > self.size.x and self.height > self.size.y:
            self.width += (self.size.x - self.width) * lerp_factor
            self.height += (self.size.y - self.height) * lerp_factor

        pygame.draw.rect(window, (255, 255, 255), (self.origin.x - self.width/2, self.origin.y - self.height/2, self.width, self.height), 0, 5, 5, 5, 5, 5)
        retrofont.draw_words(wrd, self.origin.x, self.origin.y, 25, (0, 0, 0))

        # mouse em cima do botão e botão do mouse liberado
        return mouse_over and mouse_state[2]

class Menu:
    def __init__(self):
        # main : menu principal
        # populate : define humano vs humano, humano vs cpu ou cpu vs cpu
        # settings : configurações
        # quit : sai do jogo
        self.windows = ["main", "populate", "settings", "in_game", "endscreen", "none"]
        self.window = 0
        self.previous_window = 0
        self.width = 100
        self.height = 50
        # 5 botões alocados para serem usandos quando necessário
        self.buttons = [Button(0, 0, 0), Button(0, 0, 0), Button(0, 0, 0), Button(0, 0, 0), Button(0, 0, 0), Button(0, 0, 0), Button(0, 0, 0)]

    def main(self, retrofont):
        # menu principal 
        global game_state
        retrofont.draw_words("PONG", WIDTH/2, HEIGHT/2 - (36 * 7), 72, (255, 255, 255))
        if self.buttons[0].update(WIDTH/2, HEIGHT/2, 50).create(retrofont, "PLAY"):
            self.previous_window = self.window
            self.window = self.windows.index("populate")

        if self.buttons[1].update(WIDTH/2, HEIGHT/2 + 100, 50).create(retrofont, "SETTINGS"):
            self.previous_window = self.window
            self.window = self.windows.index("settings")

    def in_game(self, retrofont):
        # menu de 'pause'
        global game_state, ball, world

        if self.buttons[0].update(WIDTH/2, 2* HEIGHT/6, 50).create(retrofont, "RESUME"):
            self.previous_window = self.window
            self.window = self.windows.index("none")
            
        if self.buttons[1].update(WIDTH/2, 3* HEIGHT/6, 50).create(retrofont, "OPTIONS"):
            self.previous_window = self.window
            self.window = self.windows.index("settings")
        
        if self.buttons[2].update(WIDTH/2, 4* HEIGHT/6, 50).create(retrofont, "MAIN_MENU"):
            world.should_update = True
            game_state = STATE_MENU
            ball = Ball()
            self.previous_window = self.window
            self.window = self.windows.index("main")

    def end_screen(self, retrofont):
        # tela final do jogo
        global game_state, ball, players, game_score_win_condition, world

        winner = players[0] if players[0].score >= game_score_win_condition else players[1]
        retro_font.draw_words(winner.name + "_won!", WIDTH/2, 2* HEIGHT/6, 80, (255, 255, 255))

        if self.buttons[2].update(WIDTH/2, 4* HEIGHT/6, 50).create(retrofont, "MAIN_MENU"):
            world.should_update = True
            game_state = STATE_MENU
            ball = Ball()
            self.previous_window = self.window
            self.window = self.windows.index("main")

    def populate(self, retrofont):
        # modo de jogo
        global game_state, players, world

        if self.buttons[0].update(100, HEIGHT/6, 50).create(retrofont, "BACK"):
            self.window = self.previous_window

        if self.buttons[1].update(WIDTH/2, 2 * HEIGHT/6, 50).create(retrofont, "Human_vs_Human"):
            world.should_update = True
            players = [Player(1, False), Player(2, False)]
            game_state = STATE_ROUND_START
            self.previous_window = self.window
            self.window = self.windows.index("none")

        if self.buttons[2].update(WIDTH/2, 3 * HEIGHT/6, 50).create(retrofont, "Human_vs_CPU"):
            world.should_update = True
            players = [Player(1, False), Player(2, True)]
            game_state = STATE_ROUND_START
            self.previous_window = self.window
            self.window = self.windows.index("none")

        if self.buttons[3].update(WIDTH/2, 4 * HEIGHT/6, 50).create(retrofont, "CPU_vs_CPU"):
            world.should_update = True
            players = [Player(1, True), Player(2, True)]
            game_state = STATE_ROUND_START
            self.previous_window = self.window
            self.window = self.windows.index("none")

    def settings(self, retrofont):
        # configurações
        global game_score_win_condition, ball_max_vertical_speed, ball_max_horizontal_speed

        height_step = 2

        if self.buttons[0].update(100, HEIGHT/6, 50).create(retrofont, "BACK"):
            self.window = self.previous_window
        
        if self.buttons[1].update(WIDTH/2 - 120, height_step * HEIGHT/6, 50).create(retrofont, "-"):
            game_score_win_condition -= 1
        retrofont.draw_words("score_win_condition", WIDTH/2, height_step * HEIGHT/6 - 50, 25, (255, 255, 255))
        retrofont.draw_words(str(game_score_win_condition), WIDTH/2, height_step * HEIGHT/6, 50, (255, 255, 255))
        if self.buttons[2].update(WIDTH/2 + 120, height_step * HEIGHT/6, 50).create(retrofont, "+"):
            game_score_win_condition += 1
        
        height_step += 1

        if self.buttons[3].update(WIDTH/2 - 120, height_step * HEIGHT/6, 50).create(retrofont, "-") and ball_max_vertical_speed > 0:
            ball_max_vertical_speed -= 1
        retrofont.draw_words("ball_max_vertical_speed", WIDTH/2, height_step * HEIGHT/6 - 50, 25, (255, 255, 255))
        retrofont.draw_words(str( int(100/18 * ball_max_vertical_speed) ) + "%", WIDTH/2, height_step * HEIGHT/6, 50, (255, 255, 255))
        if self.buttons[4].update(WIDTH/2 + 120, height_step * HEIGHT/6, 50).create(retrofont, "+") and ball_max_vertical_speed < 18:
            ball_max_vertical_speed += 1
        
        height_step += 1

        if self.buttons[5].update(WIDTH/2 - 120, height_step * HEIGHT/6, 50).create(retrofont, "-") and ball_max_horizontal_speed > 0:
            ball_max_horizontal_speed -= 1
        retrofont.draw_words("ball_max_horizontal_speed", WIDTH/2, height_step * HEIGHT/6 - 50, 25, (255, 255, 255))
        retrofont.draw_words(str( int(100/45 * ball_max_horizontal_speed) ) + "%", WIDTH/2, height_step * HEIGHT/6, 50, (255, 255, 255))
        if self.buttons[6].update(WIDTH/2 + 120, height_step * HEIGHT/6, 50).create(retrofont, "+") and ball_max_horizontal_speed < 45:
            ball_max_horizontal_speed += 1
        
        height_step += 1

    def window_handler(self, retrofont):
        # gerencia qual janela é renderiza no momento

        if self.window == 0:
            self.main(retrofont)
        elif self.window == 1:
            self.populate(retrofont)
        elif self.window == 2:
            self.settings(retrofont)
        elif self.window == 3:
            self.in_game(retrofont)
        elif self.window == 4:
            self.end_screen(retrofont)
        else:
            pass

class PowerBox:
    def __init__(self, x, y):
        self.origin = Vector2D(x, y)
        self.size = 70
        self.destruct = False

    def frame_render(self):
        global window, retro_font

        pygame.draw.rect(window, (255, 255, 255), (self.origin.x, self.origin.y, self.size, self.size))
        retro_font.draw_words("?", self.origin.x + self.size*0.5, self.origin.y + self.size*0.5, 40, (0, 0, 0))

class World:
    def __init__(self):
        self.states = ["idle", "default"]
        self.state = 0
        self.should_update = True
        self.round_time = 0.0
        self.previous_box_spawn_time = 0.0
        self.pre_start_time_remaining = 0
        self.pre_start_time = 0
        self.power_boxes = []

    def frame_think(self):
        if self.should_update:
            if game_state == STATE_MENU:
                self.state = self.states.index("idle")
            elif game_state == STATE_ROUND_START or game_state == STATE_PLAYING:
                if game_state == STATE_ROUND_START:
                    self.round_time = 0.0
                    self.previous_box_spawn_time = 0.0
                self.state = self.states.index("default")
            self.should_update = False

        if self.state == self.states.index("default"):
            # spawnamos uma powerbox após x (8-30) segundos após o ultimo spawn
            if self.round_time > self.previous_box_spawn_time + random.uniform(8, 30) and len(self.power_boxes) <= 0 and ball.collision_info[1] > 0:
                self.power_boxes = [PowerBox( random.randint(140, WIDTH - 140), random.randint(120, HEIGHT - 120) )]
                self.previous_box_spawn_time = copy(self.round_time)
            
            for power_box in self.power_boxes:
                if power_box.destruct == True:
                    self.power_boxes.clear()

            # incrementar para o tempo do round
            self.round_time += frametime/1000
        elif self.state == self.states.index("idle"):
            if len(self.power_boxes) > 0:
                self.power_boxes.clear()

    def round_pre_start(self, retro_font, time):
        # display de pontuações antes do round começar
        global players

        if time > 0:
            self.pre_start_time_remaining = time
            self.pre_start_time = time

        if self.pre_start_time <= 0 or self.pre_start_time_remaining < 0.1:
            return

        rgb = min(255, max(0, 255/self.pre_start_time * self.pre_start_time_remaining))

        retro_font.draw_words(str(players[0].score), 100, 3 * HEIGHT/6, 60, (rgb, rgb, rgb))
        retro_font.draw_words(str(players[1].score), WIDTH - 100, 3 * HEIGHT/6, 60, (rgb, rgb, rgb))
        
        self.pre_start_time_remaining -= frametime/1000

    def render_borders(self, retro_font):
        # renderizar bordas com informações do poder atual de cada player, se este tiver um ativo
        global window, players

        pygame.draw.rect(window, (255, 255, 255), (0, 0, WIDTH, 30))
        pygame.draw.rect(window, (255, 255, 255), (0, HEIGHT - 30, WIDTH, 30))

        if players[0].active_power[0] != 0:
            power_data = players[0].active_power
            rgb = min(255, max(0, (255 - 255/power_data[2] * power_data[1])))
            retro_font.draw_words(powers[power_data[0]], 70, 15, 8, (rgb, rgb, rgb))

        if players[1].active_power[0] != 0:
            power_data = players[1].active_power
            rgb = min(255, max(0, (255 - 255/power_data[2] * power_data[1])))
            retro_font.draw_words(powers[power_data[0]], WIDTH - 70, 15, 8, (rgb, rgb, rgb))

    def frame_render(self):
        # renderizar bordas e power boxes
        global window, retro_font
        if self.state == self.states.index("default"):
            self.render_borders(retro_font)

            for power_box in self.power_boxes:
                power_box.frame_render()
            
class Player:
    # constructor Player
    # self : self
    # index : id do jogador (1 ou 2), define posição e controles
    # bot : define se o jogador é um bot
    def __init__(self, index, bot):
        self.width = 30
        self.height = 150
        
        if index == 1:
            self.origin = Vector2D(self.width, HEIGHT/2 - self.height/2)
            self.name = "CPU_1" if bot else "Player_1"
        else:
            self.origin = Vector2D(WIDTH - self.width * 2, HEIGHT/2 - self.height/2)
            self.name = "CPU_2" if bot else "Player_2"

        self.velocity = Vector2D(0, 0)
        self.max_velocity = math.sqrt(ball_max_horizontal_speed**2 + ball_max_vertical_speed)* 0.15
        
        # utilizada na suavização do movimento do jogador
        self.drag = 0.2
        
        self.id = index
        self.score = 0

        # dados de colisão
        self.collision_data = None

        # variável utilizada para prevenir que o jogador use dados simulados além daqueles que ele deve utilizar
        self.can_predict_collision = True

        self.is_bot = bot
        # active_power = [índice de poder, tempo restante, tempo maximo]
        self.active_power = [powers.index("none"), 0.0, 0.0]

        # keys_pressed = {tecla : boolean}
        self.keys_pressed = {}
    
    def update_keys(self, key, value):
        # se for um bot, ignorar entradas
        if self.is_bot:
            return

        # atualizar entradas
        self.keys_pressed[key] = value

    def is_key_pressed(self, key):
        # verifica se a tecla levantada foi pressionada anteriormente
        return key in self.keys_pressed and self.keys_pressed[key]

    def handle_keys(self):
        if game_state != STATE_PLAYING:
            return

        # atualizar velocidade com base nas teclas pressionadas
        if not self.is_bot:
            if self.id == 2:
                if self.is_key_pressed(pygame.K_UP):
                    self.velocity.y -= math.sqrt(ball_max_horizontal_speed**2 + ball_max_vertical_speed)* 0.15
                if self.is_key_pressed(pygame.K_DOWN):
                    self.velocity.y += math.sqrt(ball_max_horizontal_speed**2 + ball_max_vertical_speed)* 0.15
            else:
                if self.is_key_pressed(pygame.K_w):
                    self.velocity.y -= math.sqrt(ball_max_horizontal_speed**2 + ball_max_vertical_speed)* 0.15
                if self.is_key_pressed(pygame.K_s):
                    self.velocity.y += math.sqrt(ball_max_horizontal_speed**2 + ball_max_vertical_speed)* 0.15
        # atualizar velocidade para bots
        elif len(simulated.simulated_origins) > 1:
            if self.id == 1 and ball.velocity.x < 0:
                # se a bola estiver vindo na direção do bot, procurar pelo primeiro ponto em que a bola passa pela coordenada X do jogador
                if self.can_predict_collision == True:
                    if len(simulated.left_hits) > 0:
                        self.collision_data = simulated.left_hits[0]
                        self.can_predict_collision = False

                if self.collision_data == None:
                    return

                if type(self.collision_data) != Vector2D:
                    self.collision_data = Vector2D(self.collision_data[0], self.collision_data[1])

                # quando acharmos um ponto, o bot tentarar centralizar ele em sua paddle
                self.velocity.y = self.collision_data.y - (self.origin.y + self.height/2)
            elif self.id == 2 and ball.velocity.x > 0:
                if self.can_predict_collision == True:
                    if len(simulated.right_hits) > 0:
                        self.collision_data = simulated.right_hits[0]
                        self.can_predict_collision = False

                if self.collision_data == None:
                    return

                if type(self.collision_data) != Vector2D:
                    self.collision_data = Vector2D(self.collision_data[0], self.collision_data[1])

                self.velocity.y = self.collision_data.y - (self.origin.y + self.height/2)

    def apply_velocity(self):
        # limite de velocidade do jogador
        self.velocity.y = max(min(self.velocity.y, self.max_velocity), -self.max_velocity)

        # aplicar velocidade na origem
        self.origin.x += self.velocity.x * (1/(frametime/1000) * 1/framerate)
        self.origin.y += self.velocity.y * (1/(frametime/1000) * 1/framerate)

        # resetar a velocidade após aplicá-la
        self.velocity = lerp(self.velocity, Vector2D(0, 0), self.drag)

        # manter o objeto dentro das bordas
        self.origin.x = max(0, min(WIDTH - self.width, self.origin.x))
        self.origin.y = max(35, min(HEIGHT - self.height - 35, self.origin.y))

    def process_power(self):
        # decay do tempo de poder ativo do jogador
        if self.active_power[1] > 0.0:
            self.active_power[1] -= frametime/1000
        else:
            self.active_power = [0, 0.0, 0.0]

        if self.active_power[0] == powers.index("haste"):
            if players[ 0 if self.id == 2 else 1 ].active_power[0] == powers.index("exhaust"):
            # se o jogador tiver "haste", mas o inimigo tiver "exhaust", achar um limite de velocidade um pouco acima da velocidade do "exhaust" mas abaixo da velocidade padrão
                self.max_velocity = math.sqrt(ball_max_horizontal_speed**2 + ball_max_vertical_speed)* 0.12
            else:
            # se o jogador tiver "haste", deixar com que ele se mova mais rápido
                self.max_velocity = math.sqrt(ball_max_horizontal_speed**2 + ball_max_vertical_speed)* 0.17
        elif players[ 0 if self.id == 2 else 1 ].active_power[0] == powers.index("exhaust"):
            # se o jogador inimigo tiver "exhaust", limitar a velocidade do jogador abaixo do padrão
            self.max_velocity = math.sqrt(ball_max_horizontal_speed**2 + ball_max_vertical_speed)* 0.1
        else:
            # se nenhuma das condições acima se aplicarem, utilizar a velocidade máxima padrão
            self.max_velocity = math.sqrt(ball_max_horizontal_speed**2 + ball_max_vertical_speed)* 0.15

    def render_power(self):
        if self.active_power[0] == powers.index("clairvoyance"):
            if self.id == 1 and ball.velocity.x > 0 or self.id == 2 and ball.velocity.x < 0:
                return
            # se o jogador tiver o poder "clairvoyance" e a bola estiver vindo na sua direção, procurar o primeiro ponto em que a bola atravessa a sua coordenada X
            if self.can_predict_collision == True:
                if len(simulated.left_hits) > 0 and self.id == 1:
                    self.collision_data = simulated.left_hits[0]
                    self.can_predict_collision = False
                elif len(simulated.right_hits) > 0 and self.id == 2:
                    self.collision_data = simulated.right_hits[0]
                    self.can_predict_collision = False

            if self.collision_data == None:
                    return

            if type(self.collision_data) != Vector2D:
                self.collision_data = Vector2D(self.collision_data[0], self.collision_data[1])

            # quando acharmos um ponto, renderizar 
            pygame.draw.circle(window, (130, 130, 130), (self.collision_data.x, self.collision_data.y), 10)

    def frame_think(self):
        global players

        if game_state != STATE_PLAYING and game_state != STATE_ROUND_START:
            return

        self.process_power()
        self.handle_keys()
        self.apply_velocity()

    def frame_render(self):
        if game_state != STATE_PLAYING and game_state != STATE_ROUND_START:
            return        

        # desenhar o objeto
        pygame.draw.rect( window, (255, 255, 255), (self.origin.x, self.origin.y, self.width, self.height) )

        self.render_power()

class Ball:
    def __init__(self):
        self.states = ["frozen", "active"]
        self.state = 1
        self.origin = Vector2D(WIDTH/2, HEIGHT/2)
        
        # utilizada em efeito visual
        self.origin_history = []

        # utlizada na verificação de colisão
        self.previous_origin = Vector2D(0, 0)
        self.backup_origin = Vector2D(0, 0)

        self.velocity = Vector2D(0, 0)

        # utilizada no aumento gradual da velocidade da bola 
        self.time_elapsed = 0.0

        self.speed = ball_launch_speed
        self.radius = 10

        # utlizada na direção de lançamento da bola
        self.theta = 90

        self.reset_velocity()
        self.collision_scalars = Vector2D(random.uniform(1, 1.3), random.uniform(0.7, 1.5))
        self.color = (255, 255, 255)

        # collision_info = [ "poder", id_jogador ]
        self.collision_info = [ "none", -1 ]

    def apply_power(self, player):
        global players
        
        # não há poder ativo nesse jogador, resetamos o poder registrado na bola e registramos o id do jogador com quem a bola fez contato pela ultima vez
        self.collision_info[1] = player.id
        if player.active_power[0] <= 0:
            self.collision_info[0] = "none"
            return

        # caso o jogador tenha o poder 'strength', aplicamos uma velocidade horizontal maior pós colisão e resetamos o seu poder
        # também registramos esse poder como o atual na bola
        if player.active_power[0] == powers.index("strength"):
            self.collision_scalars.x *= 1.3
            self.collision_info = ["strength", player.id]
            player.active_power[0] = 0

    def render_power(self):
        if self.collision_info[0] == "none":
            return

        # efeito visual do "strength" (trilha atrás da bola)
        if self.collision_info[0] == "strength":
            if len(self.origin_history) > 2:
                for i in range(len(self.origin_history) - 1, -1, -1):
                    pygame.draw.circle(window, (self.color[0]/len(self.origin_history) * i, self.color[1]/len(self.origin_history) * i, self.color[2]/len(self.origin_history) * i), (self.origin_history[i].x, self.origin_history[i].y), self.radius)

    def power_box_collision(self, power_box):
        global players 

        # se a bola não tiver uma última colisão com jogador neste round, retornar
        if self.collision_info[1] <= 0:
            return

        # menor distância entre o centro da bola e as vértices da powerbox
        distances = [ geometry.distPointToSegment((power_box.origin.x, power_box.origin.y), (power_box.origin.x, power_box.origin.y + power_box.size), (self.origin.x, self.origin.y) )]
        distances += [ geometry.distPointToSegment((power_box.origin.x, power_box.origin.y), (power_box.origin.x + power_box.size, power_box.origin.y), (self.origin.x, self.origin.y))]
        distances += [ geometry.distPointToSegment((power_box.origin.x + power_box.size, power_box.origin.y), (power_box.origin.x + power_box.size, power_box.origin.y + power_box.size), (self.origin.x, self.origin.y)) ]
        distances += [ geometry.distPointToSegment((power_box.origin.x, power_box.origin.y + power_box.size), (power_box.origin.x + power_box.size, power_box.origin.y + power_box.size), (self.origin.x, self.origin.y)) ]

        for distance in distances:
            # se a distancia for menor que ou igual ao raio da bola
            if distance <= self.radius:
                # reproduzir o som de "hit"
                sound_hit.play()
                # selecionar um poder aleatório
                random_power = random.randint(1, len(powers) - 1)
                # se o poder for "strength", dar a ele um tempo de 999 segundos, caso o contrário um tempo de 5 a 12 segundos
                time = 999.0 if random_power == powers.index("strength") else random.uniform(5.0, 12.0) 
                # aplicar o poder ao jogador
                players[ self.collision_info[1] - 1 ].active_power = [ random_power, time, time ]
                # destruir a powerbox
                power_box.destruct = True
                break

    def player_collision(self, player):
        global simulated
        
        if game_state == STATE_ROUND_START:
            return

        # se a bola não estiver vindo na direção do jogador, não há porque verificar se a mesma irá colidir com ele
        if player.id == 1 and self.velocity.x > 0 or player.id == 2 and self.velocity.x < 0:
            return

        # adquirir os dados da colisão
        collision_data = self.did_collide(player)

        # verificar se houve colisão
        if collision_data[0] == True:
            # reproduzir som de "hit"
            sound_hit.play()
                
            # quando houver colisão com o jogador, teletransportar a bola para o ponto de colisão, levando em consideração o seu raio
            if player.id == 1:
                self.origin = Vector2D(collision_data[1][0] + self.radius, collision_data[1][1])
            else:
                self.origin = Vector2D(collision_data[1][0] - self.radius, collision_data[1][1])

            # resetamos o histórico de origens da bola assim que houver a colisão, para prevenção de problemas de detecção de colisão momentos após 
            self.previous_origin = copy(self.origin)
            self.backup_origin = copy(self.origin)

            # determinanos um valor de 0 à metade da altura do paddle, este valor representa a distancia do meio do paddle em que a bola atingiu e é utilizado para escalar a velocidade pós impacto
            hit_height = self.origin.y - player.origin.y
            paddle_mid = player.height * 0.5
            hit_delta = min(paddle_mid, abs(hit_height - paddle_mid))

            # definimos os valores de escala para a velocidade pós impacto
            self.collision_scalars = Vector2D(-1.0, 1.0) + (Vector2D(-0.4, 0.2) / paddle_mid * hit_delta)

            # aplicamos o poder, caso haja, nessa colisão
            self.apply_power(player)

            # aplicamos os valores de escala
            self.velocity *= self.collision_scalars

            # permitir que o jogador volte a simular colisões
            player.can_predict_collision = True
        
            # reiniciamos a simulação da bola com os novos valores
            simulated.apply_simulated_data([self.origin, self.velocity, self.theta, self.time_elapsed, self.collision_scalars, self.state])

    def test_collision(self, player, origin, previous_origin):
        collision_data = None

        # teste de intersecção entre 2 segmentos finitos

        if(player.id == 1):
            collision_data = geometry.calculateIntersectPoint((origin.x, origin.y), (previous_origin.x, previous_origin.y), (player.origin.x + player.width, player.origin.y), (player.origin.x + player.width, player.origin.y + player.height))
        else:
            collision_data = geometry.calculateIntersectPoint((origin.x, origin.y), (previous_origin.x, previous_origin.y), (player.origin.x, player.origin.y), (player.origin.x, player.origin.y + player.height))

        if collision_data != None:
            return (True, collision_data)

        return (False, collision_data)

    def did_collide(self, player):
        extrapolated_origin = self.origin + self.velocity
        collision_data = self.test_collision(player, extrapolated_origin, self.backup_origin)
        # segmento entre última origem registrada e posição extrapolada entre 1 ou 2 frames, dependendo da necessidade
        return collision_data if collision_data[0] == True else self.test_collision(player, extrapolated_origin + self.velocity, self.backup_origin)

    def is_launch_acceptable(self, angle):
        # verificamos se o angulo em que a bola será lançada é adequado
        angle = abs(angle - (math.floor((angle + 180)/360))*360)
        if abs(90 - angle) > 45 and abs(180 - angle) > 45:
            return True
        return False

    def reset_velocity(self):
        self.theta = 90
        self.origin_history.clear()
        self.previous_origin = copy(self.origin)
        self.backup_origin = copy(self.origin)
        # lançamos a bola em uma direção aleatória, que se encaixa dentro de um intervalo específico
        while self.is_launch_acceptable(self.theta) == False:
            self.theta = random.randint(11, 45)

        self.velocity = Vector2D(self.speed * math.cos(self.theta * 180/math.pi), -self.speed * math.sin(self.theta* 180/math.pi))

    def handle_collisions(self):
        global players, game_state, world, menu

        for player in players:
            self.player_collision(player)

        for power_box in world.power_boxes:
            self.power_box_collision(power_box)

        # verificar se a bola passou da borda direita           
        if self.origin.x + self.radius > WIDTH:
            # pontuar e se necessário ir para a "endscreen"
            # reiniciar o round
            sound_score.play()
            players[0].score += 1
            self.velocity = Vector2D(0, 0)
            if players[0].score >= game_score_win_condition:
                menu.window = menu.windows.index("endscreen")
            else:
                game_state = STATE_ROUND_START
        elif self.origin.x - self.radius < 0:
            sound_score.play()
            players[1].score += 1
            self.velocity = Vector2D(0, 0)
            if players[1].score >= game_score_win_condition:
                menu.window = menu.windows.index("endscreen")
            else:
                game_state = STATE_ROUND_START

        # verificar se houve colisão com as bordas
        if self.origin.y - self.radius <= 30 or self.origin.y + self.radius >= HEIGHT - 30:
            # reproduzir o som "hit" e lançar a bola no eixo y em sentido oposto
            # aplicar aumento de velocidade gradual
            sound_hit.play()
            if self.origin.y - self.radius <= 30:
                self.origin.y = 30 + self.radius
            else:
                self.origin.y = HEIGHT - self.radius - 30

            for player in players:
                # permitir que o jogador volte a simular colisões
                player.can_predict_collision = True

            self.velocity.x *= 1 + (self.time_elapsed/(10**5))
            self.velocity.y *= -(1 + (self.time_elapsed/(10**5)))
            simulated.apply_simulated_data([self.origin, self.velocity, self.theta, self.time_elapsed, self.collision_scalars, self.state])

    def apply_velocity(self):
        self.origin.x += self.velocity.x * (1/(frametime/1000) * 1/framerate)
        self.origin.y += self.velocity.y * (1/(frametime/1000) * 1/framerate)
        
        # caso o poder atual registrado na bola seja "strength", não limitamos a sua velocidade
        if self.collision_info[0] == "strength":
            return

        # limitar velocidade
        if abs(self.velocity.x) > ball_max_horizontal_speed:
            self.velocity.x = -ball_max_horizontal_speed if self.velocity.x < 0 else ball_max_horizontal_speed
        if abs(self.velocity.y) > ball_max_vertical_speed:
            self.velocity.y = -ball_max_vertical_speed if self.velocity.y < 0 else ball_max_vertical_speed

    def frame_think(self):
        self.color = (255, 255, 255)

        self.apply_velocity()
        self.handle_collisions()

        self.time_elapsed += 0.1
        self.backup_origin = copy(self.previous_origin)
        self.previous_origin = copy(self.origin)

        self.origin_history.append(copy(self.origin))
        if len(self.origin_history) >= 15:
            self.origin_history.pop(0)

    def frame_render(self):
        global window

        # renderizar o poder e, após, a bola
        self.render_power()
        pygame.draw.circle(window, self.color, (self.origin.x, self.origin.y), self.radius)

class SimulatedBall:
    def __init__(self):
        self.states = ["frozen", "active"]
        self.state = 1
        self.origin = Vector2D(WIDTH/2, HEIGHT/2)
        self.previous_origin = Vector2D(0, 0)
        self.backup_origin = Vector2D(0, 0)
        self.velocity = Vector2D(0, 0)
        self.time_elapsed = 0.0
        self.speed = ball_launch_speed
        self.radius = 10
        self.theta = random.randint(0, 360)
        self.reset_velocity()
        self.collision_scalars = Vector2D(random.uniform(1, 1.3), random.uniform(0.7, 1.5))
        self.color = (255, 0, 0, 80)
        self.simulated_origins = []

        # utilizadas para registrar quando a bola simulada atravessa a coordenada X dos jogadores
        self.left_hits = []
        self.right_hits = []

    def player_collision(self, player):
        if game_state == STATE_ROUND_START:
            return

        collision_data = self.did_collide(player)

        if collision_data[0] == True:
            # quando houver colisão com o jogador, teletransportar a bola para o ponto de colisão, levando em consideração o seu raio
            if player.id == 1:
                self.origin = Vector2D(collision_data[1][0] + self.radius, collision_data[1][1])
            else:
                self.origin = Vector2D(collision_data[1][0] - self.radius, collision_data[1][1])

            # resetamos o histórico de origens da bola assim que houver a colisão, para prevenção de problemas de detecção de colisão momentos após 
            self.previous_origin = copy(self.origin)
            self.backup_origin = copy(self.origin)

            # determinanos um valor de 0 à metade da altura do paddle, este valor representa a distancia do meio do paddle em que a bola atingiu e é utilizado para escalar a velocidade pós impacto
            hit_height = self.origin.y - player.origin.y
            paddle_mid = player.height * 0.5
            hit_delta = min(paddle_mid, abs(hit_height - paddle_mid))

            # definimos os valores de escala para a velocidade pós impacto
            self.collision_scalars = Vector2D(-1.0, 1.0) + (Vector2D(-0.4, 0.2) / paddle_mid * hit_delta)

            # aplicamos os valores de escala
            self.velocity *= self.collision_scalars

    def test_collision(self, player, origin, previous_origin):
        collision_data = None

        if(player.id == 1):
            collision_data = geometry.calculateIntersectPoint((origin.x, origin.y), (previous_origin.x, previous_origin.y), (player.origin.x + player.width, player.origin.y), (player.origin.x + player.width, player.origin.y + player.height))
        else:
            collision_data = geometry.calculateIntersectPoint((origin.x, origin.y), (previous_origin.x, previous_origin.y), (player.origin.x, player.origin.y), (player.origin.x, player.origin.y + player.height))

        if collision_data != None:
            return (True, collision_data)

        return (False, collision_data)

    def did_collide(self, player):
        extrapolated_origin = self.origin + self.velocity
        collision_data = self.test_collision(player, extrapolated_origin, self.backup_origin)
        return collision_data if collision_data[0] == True else self.test_collision(player, extrapolated_origin + self.velocity, self.backup_origin)

    def reset_velocity(self):
        self.theta = random.randint(0, 360)
        self.velocity = Vector2D(self.speed * math.cos(self.theta), -self.speed * math.sin(self.theta))

    def handle_collisions(self):
        global players, game_state

        for player in players:
            self.player_collision(player)

        if self.origin.x + self.radius >= WIDTH - 65:
            self.right_hits.append(Vector2D(WIDTH - 60, self.origin.y))
        elif self.origin.x - self.radius <= 65:
            self.left_hits.append(Vector2D(60, self.origin.y))

        # caso a bola atravesse a borda direita/esquerda, finalizar a simulação
        if self.origin.x + self.radius > WIDTH:
            self.velocity = Vector2D(0, 0)
            self.state = self.states.index("frozen")
        elif self.origin.x - self.radius < 0:
            self.velocity = Vector2D(0, 0)
            self.state = self.states.index("frozen")

        if self.origin.y - self.radius <= 30 or self.origin.y + self.radius >= HEIGHT - 30:
            if self.origin.y - self.radius <= 30:
                self.origin.y = 30 + self.radius
            else:
                self.origin.y = HEIGHT - self.radius - 30

            self.velocity.x *= 1 + (self.time_elapsed/(10**5))
            self.velocity.y *= -(1 + (self.time_elapsed/(10**5)))

    def apply_simulated_data(self, data):
        self.origin = copy(data[0])
        self.velocity = copy(data[1])
        self.theta = copy(data[2])
        self.time_elapsed = copy(data[3])
        self.collision_scalars = copy(data[4])
        self.state = copy(data[5])
        self.simulated_origins = []
        self.left_hits = []
        self.right_hits = []

    def quick_apply_simulated_data(self, data):
        self.origin = copy(data[0])
        self.velocity = copy(data[1])
        self.theta = copy(data[2])
        self.time_elapsed = copy(data[3])
        self.collision_scalars = copy(data[4])

    def apply_velocity(self):
        # fazer com que a simulação viaje em uma velocidade substancialmente maior para uma melhora em performance
        self.origin.x += (self.velocity.x * 25) * (1/(frametime/1000) * 1/framerate)
        self.origin.y += (self.velocity.y * 25) * (1/(frametime/1000) * 1/framerate)

    def frame_think(self):
        prediction_time = 0.0
        # verificar o estado da bola, se o estado não for 'frozen' limitar o tempo de simulação para 6 segundos à fim de otimizar a simulação
        while self.state != self.states.index("frozen") and prediction_time <= 6.0:
            self.apply_velocity()
            self.handle_collisions()

            self.time_elapsed += 0.1 * (1/(frametime/1000) * 1/framerate)
            prediction_time += frametime/1000
            self.simulated_origins.append([copy(self.origin), copy(self.time_elapsed), copy(self.velocity)])
            self.backup_origin = copy(self.previous_origin)
            self.previous_origin = copy(self.origin)

    def frame_render(self):
        global window

        pending_deletion = []

        # deletamos os dados da simulação pelos quais a bola já passou
        for idx in range(len(self.simulated_origins)):
            origin = self.simulated_origins[idx][0]
            self.color = (255/len(self.simulated_origins) * idx, 0, 0)
            pygame.draw.circle(window, self.color, (origin.x, origin.y), self.radius)
            if self.simulated_origins[idx][1] <= ball.time_elapsed:
                pending_deletion.append(idx)

        for idx in pending_deletion:
            if len(self.simulated_origins) > idx:
                self.simulated_origins.pop(idx)

# init / instanciando classes
world = World()
players = []
ball = Ball()
simulated = SimulatedBall()
menu = Menu()
retro_font = RetroFont()

def frame_think():
    global game_state, players, mouse_state
    if menu.window != menu.windows.index("none"):
        return

    for player in players:
        # executar estágio de 'think' para cada jogador
        player.frame_think()

    # executar estágio de 'think' da bola
    ball.frame_think()

    # a cada 5 frames, refazer a simulação (caso existam novas colisões ou mudanças no trajeto que não foram consideradas antes)
    if framecount % 5 == 0:
        simulated.apply_simulated_data([ball.origin, ball.velocity, ball.theta, ball.time_elapsed, ball.collision_scalars, ball.state])
    
    # simular
    simulated.frame_think()
    
    # estágio de 'think' do mundo (caso queiramos adicionar obstáculos ou elementos diferentes)
    world.frame_think()

def frame_render():
    global players

    # renderizar o mundo primeiro
    world.frame_render()
    world.round_pre_start(retro_font, -1)
    
    for player in players:
        # executar estágio de 'render' para cada jogador
        player.frame_render()

    # executar estágio de 'render' da bola
    ball.frame_render()    

def event_buffer():
    global game_state, mouse_state

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
    else:
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

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        menu.window = menu.windows.index("in_game")

            if event.type == pygame.QUIT:
                # caso o cliente tente fechar o aplicativo, executar a sequencia abaixo
                print("pygame.QUIT")
                game_state = STATE_QUIT
                break

def pre_round_start():
    global game_state, ball

    # verificar se estamos no estado de jogo correto
    if game_state != STATE_ROUND_START:
        return
    
    for player in players:
        # autorizar a simulação de colisão para os jogadores
        player.can_predict_collision = True

    world.should_update = True
    world.round_pre_start(retro_font, 5.0)

    # reinstanciar a bola    
    ball = Ball()
    ball.state = ball.states.index("frozen")
    
    # freezetime de 1 segundo
    time.sleep(1)
    
    ball.state = ball.states.index("active")

    # atualizar os dados da simulação com os reais
    simulated.apply_simulated_data([ball.origin, ball.velocity, ball.theta, ball.time_elapsed, ball.collision_scalars, ball.state])
    
    # atualizar o estado de jogo
    game_state = STATE_PLAYING

while game_state != STATE_QUIT:
    # jogo / definir framerate, atualizar frametime
    frametime = clock.tick(framerate)

    # background preto
    window.fill( (0,0,0) )

    event_buffer()

    # jogo / diferenciação de estados
    if game_state == STATE_MENU:
        world.frame_think()
        world.frame_render()
        menu.window_handler(retro_font)
    elif game_state == STATE_PLAYING or game_state == STATE_ROUND_START:
        # execução de estágios do frame
        pre_round_start()

        frame_think()
        frame_render()

        menu.window_handler(retro_font)
    else:
        pass

    pygame.display.update()
    framecount += 1

pygame.quit()