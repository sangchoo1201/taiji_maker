import math

import pygame

from src.settings import context
import src.const as const


class Palette:
    def __init__(self, width, selected=0):
        self.width = width
        self.height = context.screen_height
        self.columns = 0
        self.screen = pygame.Surface((self.width, self.height)).convert_alpha()
        self.list = []
        self.selected = selected

    def draw(self):
        self.height = context.screen_height
        self.screen = pygame.Surface((self.width, self.height)).convert_alpha()

        self.screen.fill((0, 0, 0, 0))

        size = context.tile_size
        width = context.line_width
        self.columns = math.ceil(len(self.list) / 3)
        for i, value in enumerate(self.list):
            x = self.width // 2 + (i % 3 - 1) * size
            y = int(self.height // 2 + (i // 3 - (self.columns - 1) / 2) * size)
            rect = (x - size // 2 + width, y - size // 2 + width, size - 2 * width, size - 2 * width)
            pygame.draw.rect(self.screen, const.GRAY, rect)
            if i == self.selected:
                rect = (x - size // 2, y - size // 2, size, size)
                pygame.draw.rect(self.screen, const.LIT, rect, width // 2)
            self.screen.blit(value[0], value[0].get_rect(center=(x, y)))

    def get_selection(self):
        return self.list[self.selected][1]

    def convert_coordinates(self, x, y):
        size = context.tile_size
        left = int(self.width / 2 - 1.5 * size)
        bottom = int(self.height / 2 - self.columns / 2 * size)
        return (x - left) // size, (y - bottom) // size
