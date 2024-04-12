import math
import os
import sys
import time
import pygame
import random
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, FPS

def get_asset_path(relative_path):
    """Constructs a path to the given asset, which is valid whether the
    application is frozen or run as a Python script."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

PUYO_COLORS = ['red', 'green', 'blue', 'yellow', 'purple']
PUYO_COLOR_MAP = {
    'red': (3, 1),
    'green': (3, 7),
    'blue': (3, 4),
    'yellow': (3, 10),
    'purple': (3, 13)
}
MOVING_PUYO_COLOR_MAP = {
    'red': (12, 1),
    'green': (12, 7),
    'blue': (12, 4),
    'yellow': (12, 10),
    'purple': (12, 13)
}

EXPLOSION_TEXTURE_MAP = {
    'red': get_asset_path(os.path.join('assets', 'images','explosion', 'puyo_explosion_red.png')),
    'green': get_asset_path(os.path.join('assets', 'images','explosion', 'puyo_explosion_green.png')),
    'blue': get_asset_path(os.path.join('assets', 'images','explosion', 'puyo_explosion_blue.png')),
    'yellow': get_asset_path(os.path.join('assets', 'images','explosion', 'puyo_explosion_yellow.png')),
    'purple': get_asset_path(os.path.join('assets', 'images','explosion', 'puyo_explosion_purple.png'))
}

FONT_NUMBER_MAP = {
    '0': (0, 8),
    '1': (8, 9),
    '2': (17, 10),
    '3': (27, 9),
    '4': (36, 9),
    '5': (45, 9),
    '6': (54, 9),
    '7': (63, 9),
    '8': (72, 9),
    '9': (81, 9),
}
FONT_LETTER_MAP = {
    'S': {'x': 107, 'width': 9, 'row': 2},
    'C': {'x': 107, 'width': 10, 'row': 1},
    'O': {'x': 72, 'width': 8, 'row': 2},
    'R': {'x': 98, 'width': 9, 'row': 2},
    'E': {'x': 125, 'width': 9, 'row': 1}
}

SCORES_FOR_VICTORY = {
    0: 100,  # Score pour gagner contre l'ennemi 0
    1: 10000,  # Score pour gagner contre l'ennemi 1
}


class Game:
    def __init__(self,screen,enemy= 1):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        if enemy == 0:
            pygame.mixer.music.load(get_asset_path(os.path.join('assets', 'music', 'vocal.mp3')))
            self.character = pygame.image.load(get_asset_path(os.path.join('assets', 'images',  'Screenshot_13.png'))).convert()
        elif enemy == 1: 
            pygame.mixer.music.load(get_asset_path(os.path.join('assets', 'music', 'OceanPrince.mp3')))
            self.character = pygame.image.load(get_asset_path(os.path.join('assets', 'images',  'Screenshot_2.png'))).convert()
        pygame.mixer.music.set_volume(0.01)  
        pygame.mixer.music.play(loops=-1) 
        self.enemy = enemy

        self.running = True
        self.board = [[None for _ in range(6)] for _ in range(12)]
        self.score = 0
        self.score_pos = (350, 20)
        self.level = 1
        self.moving_puyos = []
        self.moving_puyos_speed = 0.15 # tombé des puyos
        self.current_puyo = None
        self.next_puyo = None
        self.clock = pygame.time.Clock()
        self.drop_speed = 0.05
        self.last_drop_time = pygame.time.get_ticks()
        self.screen = screen
        self.texture = pygame.image.load(get_asset_path(os.path.join('assets', 'images', 'puyos_tile.png'))).convert_alpha()  
        self.cross_texture = pygame.image.load(get_asset_path(os.path.join('assets', 'images', 'redcross.png'))).convert_alpha()  
        self.font_sprite_sheet = pygame.image.load(get_asset_path(os.path.join('assets','images','fonts_yellow.png'))).convert_alpha()
        self.scale_factor = 3
        self.expl_scale_factor = 2
        self.puyo_size = 16
        
        self.explosion_textures = {color: pygame.image.load(path).convert_alpha() for color, path in EXPLOSION_TEXTURE_MAP.items()}
        self.explosions = []
        self.combo_counter = 0
        
        self.cross_texture = pygame.transform.scale(self.cross_texture, (self.puyo_size * self.scale_factor, self.puyo_size * self.scale_factor))

        self.explosion_delay_started = False
        self.explosion_delay = 600  
        self.last_explosion_end_time = None
        self.allow_puyo_drop = True  # Permet de contrôler si les Puyos peuvent tomber

        self.rotation_since_last_collision = 0
        self.max_rotations_before_lock = 5
        self.lock_delay = 1000

        self.background_image = pygame.image.load(get_asset_path(os.path.join('assets', 'images', 'background', 'game.jpg'))).convert()
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.has_won = False # victoire

        self.spawn_puyo()
    
    # # # # # # # # #
    #     Puyos     #
    # # # # # # # # #
    
    def draw_puyo(self, screen, color_key, position, is_moving=False):
        if is_moving:
            texture_pos = MOVING_PUYO_COLOR_MAP[color_key]
        else:
            texture_pos = PUYO_COLOR_MAP[color_key]

        source_x = texture_pos[0] * self.puyo_size
        source_y = texture_pos[1] * self.puyo_size
        source_rect = pygame.Rect(source_x, source_y, self.puyo_size, self.puyo_size)
        destination_rect = pygame.Rect(
            position[0] * self.puyo_size * self.scale_factor,
            position[1] * self.puyo_size * self.scale_factor,
            self.puyo_size * self.scale_factor,
            self.puyo_size * self.scale_factor
        )
        scaled_puyo = pygame.transform.scale(
            self.texture.subsurface(source_rect),
            (self.puyo_size * self.scale_factor, self.puyo_size * self.scale_factor)
        )
        screen.blit(scaled_puyo, destination_rect.topleft)


    def spawn_puyo(self):
        time.sleep(0.07)
        color_key1, color_key2 = random.sample(PUYO_COLORS, 2)
        position1, position2 = (3, 0), (4, 0)
        self.current_puyo = PuyoPiece(color_key1, position1, color_key2, position2)

    def spawn_moving_puyo(self, color, start_pos):
        moving_puyo = Puyo(color, start_pos)
        self.moving_puyos.append(moving_puyo)

    def move_puyo(self, direction):
        new_position1 = [self.current_puyo.puyo1.position[0] + direction, self.current_puyo.puyo1.position[1]]
        new_position2 = [self.current_puyo.puyo2.position[0] + direction, self.current_puyo.puyo2.position[1]]
        
        if (0 <= new_position1[0] < 6 and 0 <= new_position2[0] < 6 and
                not self.is_collision((new_position1[0], int(new_position1[1]))) and
                not self.is_collision((new_position2[0], int(new_position2[1])))):
            self.current_puyo.puyo1.position[0] += direction
            self.current_puyo.puyo2.position[0] += direction

    def update_moving_puyos(self):
        for puyo in self.moving_puyos[:]:  
            puyo.position[1] += self.moving_puyos_speed 
            if self.is_collision((puyo.position[0], int(puyo.position[1] + 1))):
                x, y = int(puyo.position[0]), int(puyo.position[1])
                self.board[y][x] = puyo.color  
                self.moving_puyos.remove(puyo)
                self.check_for_matches() 

    def adjust_puyo_position(self):
        for puyo in [self.current_puyo.puyo1, self.current_puyo.puyo2]:
            while self.is_collision((puyo.position[0], puyo.position[1])):
                puyo.position[1] -= 1  

    def drop_puyo(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed() 
        fast_drop = keys[pygame.K_DOWN] or keys[pygame.K_s]  

        self.current_puyo.puyo1.position[1] += self.drop_speed
        self.current_puyo.puyo2.position[1] += self.drop_speed

        collision_marge = 0.85
        collision1 = self.is_collision((self.current_puyo.puyo1.position[0], self.current_puyo.puyo1.position[1] + collision_marge))
        collision2 = self.is_collision((self.current_puyo.puyo2.position[0], self.current_puyo.puyo2.position[1] + collision_marge))

        if collision1 or collision2:
            if fast_drop or (current_time - self.last_collision_time > self.lock_delay or self.rotation_since_last_collision >= self.max_rotations_before_lock):
                self.current_puyo.puyo1.position[1] = math.floor(self.current_puyo.puyo1.position[1])
                self.current_puyo.puyo2.position[1] = math.floor(self.current_puyo.puyo2.position[1])
                self.adjust_puyo_position()
                self.place_puyo()
                self.spawn_puyo()
                self.last_collision_time = pygame.time.get_ticks()
                self.rotation_since_last_collision = 0
            else:
                self.current_puyo.puyo1.position[1] -= self.drop_speed
                self.current_puyo.puyo2.position[1] -= self.drop_speed
        else:
            self.last_collision_time = pygame.time.get_ticks()
            self.rotation_since_last_collision = 0

    # Fonction de recherche en profondeur pour trouver des groupes de puyos de la même couleur
    def dfs(self, x, y, color, visited):
        if (x, y) in visited or x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board) or self.board[y][x] != color:
            return []
        visited.add((x, y))
        positions = [(x, y)]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  
            positions += self.dfs(x + dx, y + dy, color, visited)
        return positions

    def check_for_matches(self):
        rows, cols = len(self.board), len(self.board[0])
        to_remove = set()
        visited = set()

        for y in range(rows):
            for x in range(cols):
                if self.board[y][x] is not None and (x, y) not in visited:
                    positions = self.dfs(x, y, self.board[y][x], visited)
                    if len(positions) >= 4:
                        self.combo_counter += 1
                        to_remove.update(positions)
                        self.play_combo_sound(self.combo_counter)
                        for pos in positions:
                            self.spawn_explosion(self.board[pos[1]][pos[0]], pos)
                
                            
        for y, x in to_remove:
            self.board[x][y] = None
            self.draw_board(self.screen)

        for x in range(len(self.board[0])):
            for y in range(len(self.board) - 1, -1, -1): 
                if self.board[y][x] is None:
                    for above_y in range(y - 1, -1, -1):
                        if self.board[above_y][x] is not None:
                            self.spawn_moving_puyo(self.board[above_y][x], [x, above_y])
                            self.board[above_y][x] = None 
                            break       

    def place_puyo(self):
        x1, y1 = int(self.current_puyo.puyo1.position[0]), int(self.current_puyo.puyo1.position[1])
        x2, y2 = int(self.current_puyo.puyo2.position[0]), int(self.current_puyo.puyo2.position[1])

        can_place_puyo1 = y1 + 1 < len(self.board) and self.board[y1 + 1][x1] is not None
        can_place_puyo2 = y2 + 1 < len(self.board) and self.board[y2 + 1][x2] is not None

        if y1 < 12 and (can_place_puyo1 or y1 + 1 == len(self.board)):
            self.board[y1][x1] = self.current_puyo.puyo1.color
        else:
            self.spawn_moving_puyo(self.current_puyo.puyo1.color, [x1, y1])
        if y2 < 12 and (can_place_puyo2 or y2 + 1 == len(self.board)):
            self.board[y2][x2] = self.current_puyo.puyo2.color
        else:
            self.spawn_moving_puyo(self.current_puyo.puyo2.color, [x2, y2])
        self.play_place_sound()
        self.check_for_matches()                   

    # # # # # # # # #
    #    Hotkeys    #
    # # # # # # # # #

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                    self.move_puyo(-1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.move_puyo(1)
                if event.key == pygame.K_l or event.key == pygame.K_w:
                    self.play_rotate_sound()
                    self.current_puyo.rotate("left",self.board)
                    self.rotation_since_last_collision += 1
                    if self.rotation_since_last_collision < self.max_rotations_before_lock:
                        self.last_collision_time = pygame.time.get_ticks()
                elif event.key == pygame.K_m or event.key == pygame.K_x:
                    self.play_rotate_sound()
                    self.current_puyo.rotate("right",self.board)
                    self.rotation_since_last_collision += 1
                    if self.rotation_since_last_collision < self.max_rotations_before_lock:
                        self.last_collision_time = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.drop_speed = 0.3
        else:
            self.drop_speed = 0.05

    # # # # # # # # #
    #   Collisions  #
    # # # # # # # # #

    def is_collision(self, position):
        x, y = position
        y = int(y)  
        if y >= 12 or (y >= 0 and self.board[y][x] is not None):
            return True
        return False

    # # # # # # # # #
    #   Explosions  #
    # # # # # # # # #

    def spawn_explosion(self, color, position):
        current_time = pygame.time.get_ticks()
        self.explosions.append({
            'color': color,
            'position': position,
            'frame_index': 0,
            'start_time': current_time,
            'delay_start': current_time,  # Enregistre le début du délai après l'explosion
            'delay_passed': False  # Indicateur si le délai après explosion est passé
        })

    def update_explosions(self):
        current_time = pygame.time.get_ticks()
        allow_puyo_drop = True
        
        for explosion in self.explosions[:]:
            time_elapsed = current_time - explosion['start_time']
            explosion['frame_index'] = time_elapsed // 150

            if explosion['frame_index'] >= 4:
                if not explosion['delay_passed'] and current_time - explosion['delay_start'] < self.explosion_delay:
                    allow_puyo_drop = False 
                    explosion['delay_passed'] = True 
                elif current_time - explosion['delay_start'] >= self.explosion_delay:
                    # Le délai est passé, l'explosion peut être retirée
                    self.explosions.remove(explosion)
                else:
                    allow_puyo_drop = False
            else:
                allow_puyo_drop = False  # Une explosion est toujours en cours, pas de chute des Puyos

        self.allow_puyo_drop = allow_puyo_drop
        
    def draw_explosion(self, screen, explosion):
        texture = self.explosion_textures[explosion['color']]
        frame_width = 32  
        frame_height = texture.get_height()  

        offset_x = explosion['frame_index'] * frame_width
        source_rect = pygame.Rect(offset_x, 0, frame_width, frame_height)

        position = explosion['position']
        destination_x = position[0] * self.puyo_size * self.scale_factor 
        destination_y = position[1] * self.puyo_size * self.scale_factor
        destination_width = frame_width * self.expl_scale_factor
        destination_height = frame_height * self.expl_scale_factor
        destination_rect = pygame.Rect(destination_x, destination_y, destination_width, destination_height)

        scaled_explosion = pygame.transform.scale(texture.subsurface(source_rect), (destination_width, destination_height))
        screen.blit(scaled_explosion, destination_rect.topleft)


    # # # # # # # # #
    #     Sounds    #
    # # # # # # # # #
                        
    def play_combo_sound(self, combo_level):
        sound_map = {
            1: get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00016_rensa_1.wav')),
            2: get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00017_rensa_2.wav')),
            3: get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00018_rensa_3.wav')),
            4: get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00019_rensa_4.wav')),
            5: get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00020_rensa_5.wav')),
            6: get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00021_rensa_6.wav')),
            7: get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00022_rensa_7.wav')),
        }
        if combo_level > 7:
            combo_level = 7
        sound_path = sound_map.get(combo_level)
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(0.15)
            sound.play()
        except Exception as e:
            print(f"Error playing sound: {e}")

    def play_rotate_sound(self):
        sound = pygame.mixer.Sound(get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00000_puyo_kaiten.wav')))
        sound.set_volume(0.02)
        sound.play()
    def play_place_sound(self):
        sound = pygame.mixer.Sound(get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00001_puyo_chakuchi.wav')))
        sound.set_volume(0.03)
        sound.play()

    def play_victory_sound(self):
        sound = pygame.mixer.Sound(get_asset_path(os.path.join('assets', 'sounds','Global', 'VAB_00008_zen_keshi.wav')))
        sound.set_volume(0.8)
        sound.play()

    # # # # # # # # # # # # # #
    #     General Gameplay    #
    # # # # # # # # # # # # # #

    # on regarde si un puyo est posé sur la ligne 0                    
    def DetectDefeat(self):
        for x in range(len(self.board[0])):
            if self.board[0][x] is not None:
                self.running = False
                break

    def update(self):
        current_time = pygame.time.get_ticks()
        self.update_explosions()  
        if not self.moving_puyos and not self.explosions: # combo terminé
            self.update_score()
        if self.allow_puyo_drop and not self.explosions:
            if current_time - self.last_drop_time > (self.drop_speed * 5):
                self.update_moving_puyos()  
                self.drop_puyo()
                if not self.current_puyo:
                    self.spawn_puyo()
                self.DetectDefeat()
                self.last_drop_time = current_time
        
        if not self.has_won and self.score >= SCORES_FOR_VICTORY[self.enemy]:
            self.play_victory_sound()
            self.has_won = True
            self.running = False

    def draw_board(self, screen):
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color:
                    self.draw_puyo(screen, color, (x, y), is_moving=False)
                if y == 0: 
                    cross_pos_x = x * self.puyo_size * self.scale_factor
                    cross_pos_y = y * self.puyo_size * self.scale_factor
                    screen.blit(self.cross_texture, (cross_pos_x, cross_pos_y))


    def draw_board_frame(self, screen):
        frame_thickness = 5 
        frame_color = (255, 255, 255)  
        board_width = self.puyo_size * self.scale_factor * len(self.board[0]) 
        board_height = self.puyo_size * self.scale_factor * len(self.board) 
        
        margin_left = -5  
        frame_x = margin_left
        frame_y = (SCREEN_HEIGHT - board_height) / 2 - frame_thickness -10
        
        frame_rect = pygame.Rect(frame_x, frame_y, board_width + frame_thickness * 2, board_height + frame_thickness * 2)
        pygame.draw.rect(screen, frame_color, frame_rect, frame_thickness)

    # Nb chain * 10 + 10
    def update_score(self):
        for i in range(1, self.combo_counter + 1):
            self.score += i * 10 + 10
        self.combo_counter = 0

    def draw_score(self):
        score_str = str(self.score)
        x1,y1 = self.score_pos

        for letter in "SCORE":
            letter_info = FONT_LETTER_MAP[letter]
            letter_surface = pygame.Surface((letter_info['width'], 16), pygame.SRCALPHA)
            y = (letter_info['row'] - 1) * 16  
            letter_surface.blit(self.font_sprite_sheet, (0, 0), (letter_info['x'], y, letter_info['width'], 16))
            letter_surface = pygame.transform.scale(letter_surface, (letter_info['width'] * self.scale_factor, 16 * self.scale_factor))
            self.screen.blit(letter_surface, (x1, y1))
            x1 += letter_info['width'] * self.scale_factor
        x1,y1 = self.score_pos
        y1 += 17 * self.scale_factor
        for nombre in score_str:
            x, width = FONT_NUMBER_MAP[nombre]
            nombre_surface = pygame.Surface((width, 16), pygame.SRCALPHA)
            nombre_surface.blit(self.font_sprite_sheet, (0, 0), (x, 0, width, 16))
            nombre_surface = pygame.transform.scale(nombre_surface, (width * self.scale_factor, 16 * self.scale_factor))
            self.screen.blit(nombre_surface, (x1, y1))
            x1 += width * self.scale_factor 

    def draw_character(self):
        self.character = pygame.transform.scale(self.character, (170, 170))
        self.screen.blit(self.character, (350, 130))

    def draw_victory_message(self, screen):
        if self.has_won:
            font = pygame.font.Font(None, 100) # peut être modifier la police?
            text = font.render("Victory!", True, (255, 255, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)

    def draw(self, screen):
        #background
        screen.blit(self.background_image, (0, 0))
        
        self.draw_character()
        self.draw_score()
        self.draw_board_frame(screen)
        self.draw_board(screen)
        if self.current_puyo:
            self.draw_puyo(screen, self.current_puyo.puyo1.color, self.current_puyo.puyo1.position, is_moving=False)
            self.draw_puyo(screen, self.current_puyo.puyo2.color, self.current_puyo.puyo2.position,is_moving=False)
        for puyo in self.moving_puyos:
            self.draw_puyo(screen, puyo.color, puyo.position, is_moving=True)

        for explosion in self.explosions:
            self.draw_explosion(screen, explosion)

        if self.has_won:
            self.draw_victory_message(screen)


        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw(self.screen)
            self.DetectDefeat()
            self.clock.tick(FPS)
        # check si le joueur a gagné, si oui appuyé sur espace pour revenir au menu
        while self.has_won:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.has_won = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.has_won = False

        pygame.display.flip()
        

    # # # # # # # # # # # # # #
    #       Puyo Class        #
    # # # # # # # # # # # # # #

class Puyo:
    def __init__(self, color, position):
        self.color = color 
        self.position = list(position) 
    
class PuyoPiece:
    def __init__(self, color1, position1, color2, position2):
        self.puyo1 = Puyo(color1, position1)
        self.puyo2 = Puyo(color2, position2)
        self.rotation_state = 0

    def rotate(self, direction, board):
        new_position = None
        if direction == "right":
            if self.rotation_state == 0:
                new_position = [self.puyo1.position[0], self.puyo1.position[1] + 1]
            elif self.rotation_state == 1:
                new_position = [self.puyo1.position[0] - 1, self.puyo1.position[1]]
            elif self.rotation_state == 2:
                new_position = [self.puyo1.position[0], self.puyo1.position[1] - 1]
            elif self.rotation_state == 3:
                new_position = [self.puyo1.position[0] + 1, self.puyo1.position[1]]
        elif direction == "left":
            if self.rotation_state == 0:
                new_position = [self.puyo1.position[0], self.puyo1.position[1] - 1]
            elif self.rotation_state == 1:
                new_position = [self.puyo1.position[0] + 1, self.puyo1.position[1]]
            elif self.rotation_state == 2:
                new_position = [self.puyo1.position[0], self.puyo1.position[1] + 1]
            elif self.rotation_state == 3:
                new_position = [self.puyo1.position[0] - 1, self.puyo1.position[1]]

        if not self.is_collision(new_position, board):
            self.puyo2.position = new_position
            self.rotation_state = (self.rotation_state + 1 if direction == "right" else self.rotation_state - 1) % 4
        else:
            #inverser les couleurs des 2 puyos 
            self.puyo1.color, self.puyo2.color = self.puyo2.color, self.puyo1.color

    def is_collision(self, position,board):
        x, y = position
        y = int(y)  
        if x < 0 or x >= 6:
            return True
        if y >= 12 or (y >= 0 and board[y][x] is not None):
            return True
        return False

if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Puyo Puyo Game")

    game = Game()
    game.run()
    pygame.quit()
    