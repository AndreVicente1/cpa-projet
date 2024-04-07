import time
import pygame
import random
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, FPS

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

# Ajout de la carte des textures d'explosion
EXPLOSION_TEXTURE_MAP = {
    'red': 'assets/images/explosion/puyo_explosion_red.png',
    'green': 'assets/images/explosion/puyo_explosion_green.png',
    'blue': 'assets/images/explosion/puyo_explosion_blue.png',
    'yellow': 'assets/images/explosion/puyo_explosion_yellow.png',
    'purple': 'assets/images/explosion/puyo_explosion_purple.png'
}

class Game:
    def __init__(self,screen):
        self.running = True
        self.board = [[None for _ in range(6)] for _ in range(12)]
        self.score = 0
        self.level = 1
        self.moving_puyos = []
        self.moving_puyos_speed = 0.4
        self.current_puyo = None
        self.next_puyo = None
        self.clock = pygame.time.Clock()
        self.drop_speed = 0.07
        self.last_drop_time = pygame.time.get_ticks()
        self.screen = screen
        self.texture = pygame.image.load('assets/images/puyos_tile.png').convert_alpha()  
        self.scale_factor = 3
        self.expl_scale_factor = 2
        self.puyo_size = 16
        self.explosion_textures = {color: pygame.image.load(path).convert_alpha() for color, path in EXPLOSION_TEXTURE_MAP.items()}
        self.explosions = []
        self.spawn_puyo()


    def spawn_explosion(self, color, position):
        
        self.explosions.append({
            'color': color,
            'position': position,
            'frame_index': 0,
            'start_time': pygame.time.get_ticks()
        })

    def update_explosions(self):
       
        for explosion in self.explosions[:]:
            time_elapsed = pygame.time.get_ticks() - explosion['start_time']
            
            explosion['frame_index'] = time_elapsed // 150
            if explosion['frame_index'] >= 4: 
                self.explosions.remove(explosion)

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
        color_key1, color_key2 = random.sample(PUYO_COLORS, 2)
        position1, position2 = (3, 0), (4, 0)
        self.current_puyo = PuyoPiece(color_key1, position1, color_key2, position2)

    def spawn_moving_puyo(self, color, start_pos):
        moving_puyo = Puyo(color, start_pos)
        self.moving_puyos.append(moving_puyo)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                    self.move_puyo(-1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.move_puyo(1)
                if event.key == pygame.K_l:
                    self.current_puyo.rotate("left")
                elif event.key == pygame.K_m:
                    self.current_puyo.rotate("right")

        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.drop_speed = 0.3
        else:
            self.drop_speed = 0.07

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

    def drop_puyo(self):
        self.current_puyo.puyo1.position[1] += self.drop_speed
        self.current_puyo.puyo2.position[1] += self.drop_speed

        rounded_y1 = int(round(self.current_puyo.puyo1.position[1]))
        rounded_y2 = int(round(self.current_puyo.puyo2.position[1]))

        collision1 = self.is_collision((self.current_puyo.puyo1.position[0], rounded_y1 + 1))
        collision2 = self.is_collision((self.current_puyo.puyo2.position[0], rounded_y2 + 1))

        if collision1 or collision2:
            self.current_puyo.puyo1.position[1] = max(rounded_y1, 0)
            self.current_puyo.puyo2.position[1] = max(rounded_y2, 0)
            
            self.place_puyo()
            self.spawn_puyo()


    def is_collision(self, position):
        x, y = position
        y = int(y)  
        if y >= 12 or (y >= 0 and self.board[y][x] is not None):
            return True
        return False

    def place_puyo(self):
        x1, y1 = int(self.current_puyo.puyo1.position[0]), int(self.current_puyo.puyo1.position[1])
        if y1 < 12:
            self.board[y1][x1] = self.current_puyo.puyo1.color

        x2, y2 = int(self.current_puyo.puyo2.position[0]), int(self.current_puyo.puyo2.position[1])
        if y2 < 12:
            self.board[y2][x2] = self.current_puyo.puyo2.color

        self.check_for_matches()

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
                    if len(positions) >= 4:  # Si un groupe de 4 ou plus est trouvé
                        to_remove.update(positions)
                        for pos in positions:  # Déclencher une explosion pour chaque Puyo à supprimer
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

    # on regarde si un puyo est posé sur la ligne 0                    
    def DetectDefeat(self):
        for x in range(len(self.board[0])):
            if self.board[0][x] is not None:
                self.running = False
                break

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_drop_time > self.drop_speed * 5:  
            self.drop_puyo()
            self.update_moving_puyos()
            self.update_explosions()
            if not self.current_puyo:
                self.spawn_puyo()
            self.DetectDefeat()
            self.last_drop_time = current_time
            
        

    def draw_board(self, screen):
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color:
                    self.draw_puyo(screen, color, (x, y),is_moving=False)

    def draw(self, screen):
        screen.fill(BLACK)
        self.draw_board(screen)
        if self.current_puyo:
            # Dessine les deux puyos de la pièce actuelle
            self.draw_puyo(screen, self.current_puyo.puyo1.color, self.current_puyo.puyo1.position, is_moving=False)
            self.draw_puyo(screen, self.current_puyo.puyo2.color, self.current_puyo.puyo2.position,is_moving=False)
        # Dessine les puyos en mouvement
        for puyo in self.moving_puyos:
            self.draw_puyo(screen, puyo.color, puyo.position, is_moving=True)

        for explosion in self.explosions:
            self.draw_explosion(screen, explosion)

        pygame.display.flip()

class Puyo:
    def __init__(self, color, position):
        self.color = color 
        self.position = list(position) 
    
class PuyoPiece:
    def __init__(self, color1, position1, color2, position2):
        self.puyo1 = Puyo(color1, position1)
        self.puyo2 = Puyo(color2, position2)
        self.rotation_state = 0
    def rotate(self, direction):
        if direction == "right":
            self.rotation_state = (self.rotation_state + 1) % 4
        elif direction == "left":
            self.rotation_state = (self.rotation_state - 1) % 4
        if self.rotation_state == 0:  
            self.puyo2.position = [self.puyo1.position[0] + 1, self.puyo1.position[1]]
        elif self.rotation_state == 1:  
            self.puyo2.position = [self.puyo1.position[0], self.puyo1.position[1] + 1]
        elif self.rotation_state == 2:  
            self.puyo2.position = [self.puyo1.position[0] - 1, self.puyo1.position[1]]
        elif self.rotation_state == 3:  
            self.puyo2.position = [self.puyo1.position[0], self.puyo1.position[1] - 1]

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Puyo Puyo Game")
    game = Game()
    game.run()
    pygame.quit()
    