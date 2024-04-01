import pygame
import sys
from src.game import Game
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Puyo Puyo Game")
    
    clock = pygame.time.Clock()
    game = Game(screen)


    running = True
    while running:
        game.handle_events()
        running = game.running
        game.update()
        game.draw(screen)

        pygame.display.flip()
        clock.tick(FPS) 

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
