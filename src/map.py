import os
import pygame
import sys
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.game import Game
from src.algorithms.astar import astar

def get_asset_path(relative_path):
    """Constructs a path to the given asset, which is valid whether the
    application is frozen or run as a Python script."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Map:
    def __init__(self, screen):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        pygame.mixer.music.load(get_asset_path(os.path.join('assets', 'music', 'final.mp3')))
        pygame.mixer.music.set_volume(0.01)  
        pygame.mixer.music.play(loops=-1) 
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.rows, self.cols = 10, 15

        self.map = [
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        ]

        self.player_pos = [1, 1]
        self.enemy_pos = [5, 8] # Pos ennemi 1
        self.enemy_pos2 = [6, 5]  # Pos ennemi 2
        self.player_image = pygame.image.load(get_asset_path(os.path.join('assets', 'images', 'characters','cat.jpg'))).convert_alpha()
        self.enemy_image = pygame.image.load(get_asset_path(os.path.join('assets', 'images', 'characters','popoi.png'))).convert_alpha()  # ennemi 1
        self.enemy_image2 = pygame.image.load(get_asset_path(os.path.join('assets', 'images', 'characters','OceanKing.png'))).convert_alpha()  # ennemi 2
        
        self.tile_size = 40
        self.player_image = pygame.transform.scale(self.player_image, (self.tile_size, self.tile_size))
        self.enemy_image = pygame.transform.scale(self.enemy_image, (self.tile_size, self.tile_size))
        self.enemy_image2 = pygame.transform.scale(self.enemy_image2, (self.tile_size, self.tile_size))

        self.running = True
        self.state = 'PREGAME'
        self.game_started = False # Match puyo

        self.enemy_update_rate = 15  # Nombre d'itérations entre chaque mise à jour de la position de l'ennemi
        self.enemy_update_cpt = 0

    
    #
    # ASTAR algorithm application
    #

    def find_path(self, start_pos, end_pos, grid):
        path = astar(start_pos, end_pos, grid)
        return path


    def update_enemy_position(self, enemy_pos, enemy_pos2):
        tmp = [row[:] for row in self.map]
        tmp[enemy_pos2[0]][enemy_pos2[1]] = 1  # Marque l'autre ennemi comme un mur

        path = self.find_path(tuple(enemy_pos), tuple(self.player_pos), tmp)

        if path and len(path) > 1:
            next_pos = path[1]
            return next_pos
        return enemy_pos

    #
    #
    #

    # # # # # # # # #
    #     Visual    #
    # # # # # # # # #

    def draw_map(self):
        for row in range(self.rows):
            for col in range(self.cols):
                color = (100, 100, 100) if (row + col) % 2 == 0 else (150, 150, 150)
                pygame.draw.rect(self.screen, color, (col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))
                # murs
                if self.map[row][col] == 1:
                    pygame.draw.rect(self.screen, (0, 0, 0), (col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))

    def draw_player(self):
        self.screen.blit(self.player_image, (self.player_pos[1] * self.tile_size, self.player_pos[0] * self.tile_size))

    def draw_enemy(self):
        self.screen.blit(self.enemy_image, (self.enemy_pos[1] * self.tile_size, self.enemy_pos[0] * self.tile_size))
        self.screen.blit(self.enemy_image2, (self.enemy_pos2[1] * self.tile_size, self.enemy_pos2[0] * self.tile_size))

    # # # # # # # # # #
    #     Hotkeys     #
    # # # # # # # # # #

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT  or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.KEYDOWN:
                prev_pos = list(self.player_pos)
                if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                    self.player_pos[1] = max(0, self.player_pos[1] - 1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player_pos[1] = min(self.cols - 1, self.player_pos[1] + 1)
                elif event.key == pygame.K_UP or event.key == pygame.K_z:
                    self.player_pos[0] = max(0, self.player_pos[0] - 1)
                elif event.key == pygame.K_DOWN  or event.key == pygame.K_s:
                    self.player_pos[0] = min(self.rows - 1, self.player_pos[0] + 1)
                if self.map[self.player_pos[0]][self.player_pos[1]] != 0:
                    self.player_pos = prev_pos

    # # # # # # # # # # #
    #     Collisions    #
    # # # # # # # # # # #

    # collision = match
    def check_collision(self):
        player_pos_tuple = tuple(self.player_pos)
        enemy_pos_tuple = tuple(self.enemy_pos)
        enemy_pos2_tuple = tuple(self.enemy_pos2)

        if player_pos_tuple == enemy_pos_tuple:
            self.start_puyo_match(self.enemy_pos)

        elif player_pos_tuple == enemy_pos2_tuple:
            self.start_puyo_match(self.enemy_pos2)

    def start_puyo_match(self, enemy_pos):
        enemy_type = 0 if enemy_pos == self.enemy_pos else 1
        # nouvelle fenêtre pour le match Puyo
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Match Puyo")

        self.game_started = True
        game = Game(self.screen, enemy_type)
        game.run()
        while True:
            if not game.running:
                self.running = False
                break
        
    # # # # # # # # # # #
    #    Game update    #
    # # # # # # # # # # #
            
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
    def update(self):
        self.enemy_update_cpt += 1
        if self.enemy_update_cpt >= self.enemy_update_rate:
            self.enemy_update_cpt = 0

            distance_enemy1 = self.calculate_distance(self.enemy_pos, self.player_pos)
            distance_enemy2 = self.calculate_distance(self.enemy_pos2, self.player_pos)

            if distance_enemy1 > distance_enemy2:
                first_enemy, second_enemy = self.enemy_pos, self.enemy_pos2
            else:
                first_enemy, second_enemy = self.enemy_pos2, self.enemy_pos

            temp_first_enemy_pos = self.update_enemy_position(first_enemy, second_enemy)
            if temp_first_enemy_pos != first_enemy:
                first_enemy = temp_first_enemy_pos

            temp_second_enemy_pos = self.update_enemy_position(second_enemy, first_enemy)
            if temp_second_enemy_pos != second_enemy and temp_second_enemy_pos != first_enemy:
                second_enemy = temp_second_enemy_pos

            if distance_enemy1 > distance_enemy2:
                self.enemy_pos, self.enemy_pos2 = first_enemy, second_enemy
            else:
                self.enemy_pos2, self.enemy_pos = first_enemy, second_enemy

            self.check_collision()


    def draw(self):
        if self.state == 'PREGAME' or self.state == 'PLAYING':
            self.screen.fill((0, 0, 0))
            self.draw_map()
            self.draw_player()
            self.draw_enemy()
            pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            if self.state != 'PVP': 
                self.update()
                self.draw()
            self.clock.tick(FPS)
        