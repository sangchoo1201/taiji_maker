import pygame

import src.const as const
from src.settings import context


def fill(surface, color):
    w, h = surface.get_size()
    r, g, b, *_ = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), (r, g, b, a))


def transparent(surface, alpha):
    w, h = surface.get_size()
    for x in range(w):
        for y in range(h):
            r, g, b, a = surface.get_at((x, y))
            surface.set_at((x, y), (r, g, b, alpha if a else a))


class Tile(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((context.tile_size,) * 2).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.lit = False
        self.fixed = False
        self.color = const.NONE
        self.symbol = const.NONE
        self.hidden = False
        self.exist = True

        self.draw()

    def flip(self):
        if self.fixed:
            return self
        self.lit = not self.lit
        self.draw()
        return self

    def change(self, symbol, color=const.NONE):
        self.symbol = symbol
        self.color = color
        self.draw()
        return self

    def draw(self, lit_color=const.LIT, dark_color=const.GRAY):
        if not self.exist:
            self.image.fill((0, 0, 0, 0))
            return
        size = context.tile_size
        width = context.line_width
        color = lit_color if self.lit else dark_color
        rect = (width, width, size - 2 * width, size - 2 * width)
        pygame.draw.rect(self.image, color, rect, width)
        if self.fixed:
            triple = context.tile_size // 3
            positions = (
                ((triple, 0), (triple, size)),
                ((size - triple, 0), (size - triple, size)),
                ((0, triple), (size, triple)),
                ((0, size - triple), (size, size - triple)),
            )
            for start, end in positions:
                pygame.draw.line(self.image, const.TRANS, start, end, size // 8)
        rect = (3 * width, 3 * width, size - 6 * width, size - 6 * width)
        pygame.draw.rect(self.image, color if self.lit else const.TRANS, rect)

        symbol_image = pygame.image.load(f"resource/symbol/{self.symbol}.png").convert_alpha()
        symbol_image = pygame.transform.scale(symbol_image, (size, size))
        if self.hidden:
            if not context.is_editing:
                return
            transparent(symbol_image, 127)
        if self.color and self.symbol not in const.FLOWER:
            fill(symbol_image, self.color)
        self.image.blit(symbol_image, (0, 0))

    def locate(self, centerx, centery):
        self.rect.centerx = centerx
        self.rect.centery = centery
