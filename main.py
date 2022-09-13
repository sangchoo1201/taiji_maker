import sys

import pygame

from src.player import Player
from src.selector import Selector
from src.settings import context

pygame.init()
screen = pygame.display.set_mode(context.screen_size, pygame.RESIZABLE)
pygame.display.set_caption("Taiji maker")
icon = pygame.image.load("resource/icon/icon.png")
pygame.display.set_icon(icon)


def end(*_):
    pygame.quit()
    sys.exit()


def level_select(*_):
    selector = Selector(screen)
    while True:
        result_selector = selector.run()
        if result_selector is not None:
            return result_selector


def play(file_name, *_):
    player = Player(screen, f"levels/{file_name}")
    while True:
        result_main = player.run()
        if result_main is not None:
            return result_main


if __name__ == "__main__":
    scene = level_select
    args = ()
    while True:
        result = scene(*args)
        if type(result) == tuple:
            scene, *args = result
        else:
            scene, args = result, ()
