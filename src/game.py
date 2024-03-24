import pygame
import random
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, FPS

# Définition des couleurs en format RGB pour être utilisées avec Pygame
COLORS = {'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255), 'yellow': (255, 255, 0), 'purple': (128, 0, 128)}

class Game:
    def __init__(self):
        self.running = True
        self.board = [[None for _ in range(6)] for _ in range(12)]
        self.score = 0
        self.level = 1
        self.current_puyo = None
        self.next_puyo = None
        self.clock = pygame.time.Clock()
        self.drop_speed = 500
        self.last_drop_time = pygame.time.get_ticks()
        self.spawn_puyo()

    def spawn_puyo(self):
        color_key = random.choice(list(COLORS.keys()))
        color = COLORS[color_key]
        position = (3, 0)
        self.current_puyo = Puyo(color, position)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                print(f"Key pressed: {event.key}")
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    print("left")
                    self.move_puyo(-1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.move_puyo(1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.drop_speed = 50  # Accélère la chute

    def move_puyo(self, direction):
        new_position = (self.current_puyo.position[0] + direction, self.current_puyo.position[1])
        if 0 <= new_position[0] < 6 and not self.is_collision(new_position):
            self.current_puyo.position = new_position

    def drop_puyo(self):
        new_position = (self.current_puyo.position[0], self.current_puyo.position[1] + 1)
        if not self.is_collision(new_position):
            self.current_puyo.position = new_position
        else:
            self.place_puyo()
            self.spawn_puyo()

    def is_collision(self, position):
        x, y = position
        if y >= 6 or (y > 0 and self.board[y][x] is not None):
            return True
        return False

    def place_puyo(self):
        x, y = self.current_puyo.position
        if y < 12:
            self.board[y][x] = self.current_puyo.color
        self.check_for_matches()

    def check_for_matches(self):
        # logique de vérification des correspondances
        pass

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_drop_time > self.drop_speed:
            self.drop_puyo()
            self.last_drop_time = current_time
        # Réinitialise la vitesse de chute après la chute rapide
        self.drop_speed = 500

    def draw_board(self, screen):
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color:
                    pygame.draw.circle(screen, color, (x * 100 + 50, y * 100 + 50), 20)

    def draw(self, screen):
        screen.fill(BLACK)
        self.draw_board(screen)
        if self.current_puyo:
            pygame.draw.circle(screen, self.current_puyo.color, (self.current_puyo.position[0] * 100 + 50, self.current_puyo.position[1] * 100 + 50), 20)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw(screen)
            self.clock.tick(FPS)

class Puyo:
    def __init__(self, color, position):
        self.color = color 
        self.position = list(position) 

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Puyo Puyo Game")
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()