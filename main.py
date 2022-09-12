import sys

import pygame

from src.player import Player
from src.settings import context

pygame.init()
screen = pygame.display.set_mode(context.screen_size, pygame.RESIZABLE)
pygame.display.set_caption("Taiji maker")
icon = pygame.image.load("resource/icon/icon.png")
pygame.display.set_icon(icon)


def end(*_):
    pygame.quit()
    sys.exit()


def main(*_):
    player = Player(screen, "levels/level.json")
    while True:
        result_main = player.run()
        if result_main is not None:
            return result_main


scene = main
args = ()
while True:
    result = scene(*args)
    if type(result) == tuple:
        scene, *args = result
    else:
        scene, args = result, ()
