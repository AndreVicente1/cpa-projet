import math
import os
import numpy
import pygame
import sys
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.game import Game
from src.algorithms.astar import astar

def get_asset_path(relative_path):
    """Construit un chemin d'accès vers la ressource indiquée"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Map:
    def __init__(self, screen):
        # Initialisation son
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        pygame.mixer.music.load(get_asset_path(os.path.join('assets', 'music', 'wc3.mp3')))
        pygame.mixer.music.set_volume(0.05)  
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
        # mise à l'échelle
        self.player_image = pygame.transform.scale(self.player_image, (self.tile_size, self.tile_size))
        self.enemy_image = pygame.transform.scale(self.enemy_image, (self.tile_size, self.tile_size))
        self.enemy_image2 = pygame.transform.scale(self.enemy_image2, (self.tile_size, self.tile_size))

        self.running = True
        self.state = "PREGAME"
        self.game_started = False # Match puyo

        self.enemy_update_rate = 15  # Nombre d'itérations entre chaque mise à jour de la position de l'ennemi
        self.enemy_update_cpt = 0

        # Systeme de vision (Fog of War)
        self.view_distance = 10  # distance de vision
        self.view_angle = math.radians(60) # angle de vision
    
    #
    # ASTAR algorithm application
    #

    def find_path(self, start_pos, end_pos, grid):
        """ Déterminer le chemin que les ennemis doivent emprunter pour atteindre le joueur """
        path = astar(start_pos, end_pos, grid)
        return path


    def update_enemy_position(self, enemy_pos, enemy_pos2):
        """Met à jour la position d'un ennemi en évitant les collisions avec l'autre ennemi"""
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
        """Affiche la carte du jeu"""
        visible_points = self.update_visibility() # points visibles par le joueur
        for row in range(self.rows):
            for col in range(self.cols):
                # les murs restent visibles
                if self.map[row][col] == 1:
                    color = (0, 0, 0)
                elif (col, row) in visible_points:
                    color = (150, 150, 150) # visible
                else:
                    color = (50, 50, 50) # non visible

                pygame.draw.rect(self.screen, color, (col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))

    def draw_player(self):
        """Affiche le joueur"""
        self.screen.blit(self.player_image, (self.player_pos[1] * self.tile_size, self.player_pos[0] * self.tile_size))

    def draw_enemy(self, visible_points):
        """Affiche les ennemis s'ils sont visibles par le joueur"""
        if (self.enemy_pos[1], self.enemy_pos[0]) in visible_points:
            self.screen.blit(self.enemy_image, (self.enemy_pos[1] * self.tile_size, self.enemy_pos[0] * self.tile_size))
        if (self.enemy_pos2[1], self.enemy_pos2[0]) in visible_points:
            self.screen.blit(self.enemy_image2, (self.enemy_pos2[1] * self.tile_size, self.enemy_pos2[0] * self.tile_size))


    # # # # # # # # # #
    #     Hotkeys     #
    # # # # # # # # # #

    def handle_events(self):
        """Gère les touches de l'utilisateur pour contrôler le jeu"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT  or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.KEYDOWN:
                prev_pos = list(self.player_pos) # position précédente pour annuler un déplacement non valide (mur)
                if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                    self.player_pos[1] = max(0, self.player_pos[1] - 1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player_pos[1] = min(self.cols - 1, self.player_pos[1] + 1)
                elif event.key == pygame.K_UP or event.key == pygame.K_z:
                    self.player_pos[0] = max(0, self.player_pos[0] - 1)
                elif event.key == pygame.K_DOWN  or event.key == pygame.K_s:
                    self.player_pos[0] = min(self.rows - 1, self.player_pos[0] + 1)
                if self.map[self.player_pos[0]][self.player_pos[1]] != 0: # reset position
                    self.player_pos = prev_pos


    # # # # # # # # # # #
    #     Collisions    #
    # # # # # # # # # # #

    # collision = match
    def check_collision(self):
        """Vérifie les collisions entre le joueur et les ennemis pour déclencher un match de Puyo"""
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

        
    # # # # # # # # # # # # # # # #
    #    Game update & Gameplay   #
    # # # # # # # # # # # # # # # #
            
    def calculate_distance(self, pos1, pos2):
        """Distance Manhattan"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
    def update(self):
        """Met à jour régulièrement l'état du jeu, en calculant les déplacements des ennemis et en vérifiant les collisions"""
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

    def get_direction(self):
        """Récupère la direction du joueur en fonction de la position de la souris"""
        mx, my = pygame.mouse.get_pos()
        px, py = self.player_pos[1] * self.tile_size + self.tile_size // 2, self.player_pos[0] * self.tile_size + self.tile_size // 2
        dx, dy = mx - px, my - py # vecteur entre le joueur et la souris
        distance = math.hypot(dx, dy)
        if distance == 0: # souris sur le joueur
            return (0, 0)
        return (dx / distance, dy / distance)

    def update_visibility(self):
        """Met à jour la visibilité du joueur en fonction de sa direction"""
        direction = self.get_direction()
        visible_points = set()
        angles = [-self.view_angle / 2, 0, self.view_angle / 2]

        for angle in angles:
            dx, dy = math.cos(math.atan2(direction[1], direction[0]) + angle), math.sin(math.atan2(direction[1], direction[0]) + angle)
            x, y = self.player_pos[1], self.player_pos[0]
            for _ in range(self.view_distance):
                x += dx
                y += dy
                ix, iy = int(x), int(y)
                if not (0 <= ix < self.cols and 0 <= iy < self.rows):
                    break
                visible_points.add((ix, iy))
                if self.map[iy][ix] == 1:
                    break

        return visible_points
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.draw_map()
        self.draw_player()
        visible_points = self.update_visibility()
        self.draw_enemy(visible_points)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)