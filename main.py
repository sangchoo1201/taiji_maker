import sys

import pygame

from src.menu import Menu
from src.player import Player
from src.builder import Builder
from src.selector import Selector
from src.settings import context
from src.textbox import TextBox

pygame.init()
screen = pygame.display.set_mode(context.screen_size, pygame.RESIZABLE)
pygame.display.set_caption("Taiji maker")
icon = pygame.image.load("resource/icon/icon.png")
pygame.display.set_icon(icon)


def end(*_):
    pygame.quit()
    sys.exit()


def main(*_):
    menu = Menu(screen)
    while True:
        result_menu = menu.run()
        if result_menu is not None:
            return result_menu


def select(*_):
    selector = Selector(screen, play)
    while True:
        result_selector = selector.run()
        if result_selector is not None:
            return result_selector


def play(file_name, *_):
    player = Player(screen, file_name)
    while True:
        result_main = player.run()
        if result_main is not None:
            return result_main


def new(*_):
    text_box = TextBox(screen, "Enter level name", make, ".tj")
    while True:
        result_text_box = text_box.run()
        if result_text_box is not None:
            return result_text_box


def load(*_):
    selector = Selector(screen, make)
    while True:
        result_selector = selector.run()
        if result_selector is not None:
            return result_selector


def make(file_name, *_):
    builder = Builder(screen, file_name)
    while True:
        result_builder = builder.run()
        if result_builder is not None:
            return result_builder


if __name__ == "__main__":
    scene = main
    args = ()
    while True:
        result = scene(*args)
        if type(result) == tuple:
            scene, *args = result
        else:
            scene, args = result, ()
