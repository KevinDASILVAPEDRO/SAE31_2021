import pygame
import pygame_menu
from game import Game

pygame.init()
surface = pygame.display.set_mode((800, 600))

def start_the_game():
    game = Game()
    game.game_run()



menu = pygame_menu.Menu("Mordred's Legend", 800, 600,
                       theme=pygame_menu.themes.THEME_ORANGE)
#menu.add.text_input('Name :', default='John Doe')
menu.add.button('Jouer', start_the_game)
menu.add.button('Quitter', pygame_menu.events.EXIT)
menu.mainloop(surface)

