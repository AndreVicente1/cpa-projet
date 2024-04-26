import os
import pygame
import sys
from src.game import Game, get_asset_path, load_best_score
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.map import Map

#Commande pour génerer un .exe: python3 -m PyInstaller --onefile --windowed --add-data "assets;assets" main.py 

def draw_menu(screen):
    best_score=load_best_score()
    background_image = pygame.image.load(get_asset_path(os.path.join('assets', 'images', 'background', 'menu.jpg'))).convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    #background
    screen.blit(background_image, (0, 0))
    font = pygame.font.SysFont(None, 55)
    
    # Bouton Jouer
    text_jouer = font.render('Jouer', True, (255, 0, 0))
    button_jouer = text_jouer.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 90))
    screen.blit(text_jouer, button_jouer)
    
    # Bouton Mode Histoire
    text_mode_histoire = font.render('Mode Histoire', True, (0, 0, 0))
    button_mode_histoire = text_mode_histoire.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30))
    screen.blit(text_mode_histoire, button_mode_histoire)

    # Meilleur score 
    text_score = font.render(f'Meilleur Score: {best_score}', True, (0, 0, 0))
    score_pos = text_score.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 90))
    screen.blit(text_score, score_pos)
    
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
                        map = Map(screen)  
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
                map.draw()  
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


