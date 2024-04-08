import pygame
import sys
from src.game import Game
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.map import Map

#python3 -m PyInstaller --onefile --windowed --add-data "assets;assets" main.py 
def draw_menu(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 55)
    
    # Bouton Jouer
    text_jouer = font.render('Jouer', True, (255, 255, 255))
    button_jouer = text_jouer.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30))
    pygame.draw.rect(screen, (0, 128, 0), button_jouer)
    screen.blit(text_jouer, button_jouer)
    
    # Bouton Mode Histoire
    text_mode_histoire = font.render('Mode Histoire', True, (255, 255, 255))
    button_mode_histoire = text_mode_histoire.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30))
    pygame.draw.rect(screen, (0, 128, 0), button_mode_histoire)
    screen.blit(text_mode_histoire, button_mode_histoire)
    
    return button_jouer, button_mode_histoire

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Puyo Puyo 3")
    
    clock = pygame.time.Clock()
    game = None
    in_menu = True
    mode_histoire = False  # Pour suivre si le joueur a sélectionné le mode histoire

    while True:
        if in_menu:
            button_jouer, button_mode_histoire = draw_menu(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_jouer.collidepoint(event.pos):
                        in_menu = False
                        game = Game(screen)
                    elif button_mode_histoire.collidepoint(event.pos):
                        in_menu = False
                        mode_histoire = True
                        map = Map(screen)  # Initier la map pour le mode histoire
        elif mode_histoire:
            map.handle_events()
            if not map.running:
                pygame.mixer.music.stop()
                in_menu = True
                mode_histoire = False
                continue
            if map.state == 'PREGAME':
                map.run()
            else:
                map.update()
                map.draw()  # Corrigé pour ne pas passer 'screen'
        else:
            game.handle_events()
            if not game.running:
                in_menu = True
                pygame.mixer.music.stop()
                continue
            game.update()
            game.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()


