import pygame
import random
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, FPS


COLORS = {'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255), 'yellow': (255, 255, 0), 'purple': (128, 0, 128)}

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
        self.drop_speed = 0.1
        self.last_drop_time = pygame.time.get_ticks()
        self.screen = screen
        self.spawn_puyo()
        
    

    def spawn_puyo(self):
        color_key = random.choice(list(COLORS.keys()))
        color = COLORS[color_key]
        position = (3, 0)
        self.current_puyo = Puyo(color, position)

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
        if keys[pygame.K_DOWN]:
            self.drop_speed = 0.3
        else:
            self.drop_speed = 0.1

 

    def move_puyo(self, direction):
        new_x = self.current_puyo.position[0] + direction
        new_y = self.current_puyo.position[1] 
        if 0 <= new_x < 6 and not self.is_collision((new_x, int(new_y))):
            self.current_puyo.position[0] = new_x
            
    
    def update_moving_puyos(self):
        for puyo in self.moving_puyos[:]:  
            puyo.position[1] += self.moving_puyos_speed 
            if self.is_collision((puyo.position[0], int(puyo.position[1] + 1))):
                x, y = int(puyo.position[0]), int(puyo.position[1])
                self.board[y][x] = puyo.color  
                self.moving_puyos.remove(puyo)
                self.check_for_matches() 

    def drop_puyo(self):
        self.current_puyo.position[1] += self.drop_speed
        rounded_y = int(round(self.current_puyo.position[1]))
        if self.is_collision((self.current_puyo.position[0], rounded_y + 1)): 
            self.current_puyo.position[1] = max(rounded_y, 0)  
            self.place_puyo()
            self.spawn_puyo()

    def is_collision(self, position):
        x, y = position
        y = int(y)  
        if y >= 12 or (y >= 0 and self.board[y][x] is not None):
            return True
        return False

    def place_puyo(self):
        x, y = int(self.current_puyo.position[0]), int(self.current_puyo.position[1])
        if y < 12:
            self.board[y][x] = self.current_puyo.color
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
            self.DetectDefeat()
            self.last_drop_time = current_time
        

    def draw_board(self, screen):
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color:
                    pygame.draw.circle(screen, color, (x * 40 + 50, y * 40 ), 20)

    def draw(self,screen):
        screen.fill(BLACK)
        self.draw_board(screen)
        if self.current_puyo:
            pygame.draw.circle(screen, self.current_puyo.color, (self.current_puyo.position[0] * 40 + 50, self.current_puyo.position[1] * 40 ), 20)
        for puyo in self.moving_puyos:
            pygame.draw.circle(screen, puyo.color, (int(puyo.position[0] * 40 + 50), int(puyo.position[1] * 40)), 20)
        pygame.display.flip()

    
            

class Puyo:
    def __init__(self, color, position):
        self.color = color 
        self.position = list(position) 
    
class PuyoPiece:
    def __init__(self, color1, position1, color2, position2):
        self.puyo1 = Puyo(color1, position1)
        self.puyo2 = Puyo(color2, position2)
        self.orientation = 0  

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Puyo Puyo Game")
    game = Game()
    game.run()
    pygame.quit()
    