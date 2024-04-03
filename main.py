import pygame
import sys
from src.game import Game
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def draw_menu(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 55)
    text = font.render('Jouer', True, (255, 255, 255))
    button = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    pygame.draw.rect(screen, (0, 128, 0), button)
    screen.blit(text, button)
    return button

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Puyo Puyo 3")
    
    clock = pygame.time.Clock()
    game = None
    in_menu = True

    while True:
        if in_menu:
            button = draw_menu(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button.collidepoint(event.pos):
                        in_menu = False
                        game = Game(screen)
        else:
            game.handle_events()
            if not game.running:
                in_menu = True
                continue
            game.update()
            game.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()


