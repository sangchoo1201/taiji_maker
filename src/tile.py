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
        self.legacy_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.color = const.NONE
        self.symbol = const.NONE
        self.lit = False
        self.fixed = False
        self.hidden = False
        self.exist = True
        self.connected = [False, False, False, False]

        self.prev = None

        self.marked = False

    def flip(self):
        if self.fixed:
            return self
        self.lit = not self.lit
        return self

    def mark(self):
        self.marked = not self.marked
        return self

    def change(self, symbol, color=const.NONE):
        self.symbol = symbol
        self.color = color
        return self

    def get_state(self):
        return self.color, self.symbol, self.lit, self.fixed, self.hidden, self.exist, self.marked, *self.connected

    def draw(self, lit_color=const.LIT, dark_color=const.GRAY):
        if self.prev == self.get_state():
            return
        self.prev = self.get_state()

        if not self.exist:
            self.image.fill(const.TRANS)
            self.legacy_image = self.image.copy()
            return

        if self.marked:
            self.image.fill(const.MARK)
        else:
            self.image.fill(const.TRANS)

        size = context.tile_size
        width = context.line_width

        image = pygame.Surface((size, size)).convert_alpha()
        image.fill(const.TRANS)

        color = lit_color if self.lit else dark_color
        rect = (width, width, size - 2 * width, size - 2 * width)
        pygame.draw.rect(image, color, rect, width)
        if self.fixed:
            triple = context.tile_size // 3
            positions = (
                ((triple, 0), (triple, size)),
                ((size - triple, 0), (size - triple, size)),
                ((0, triple), (size, triple)),
                ((0, size - triple), (size, size - triple)),
            )
            for start, end in positions:
                pygame.draw.line(image, const.TRANS, start, end, size // 8)
        rect = (3 * width, 3 * width, size - 6 * width, size - 6 * width)
        pygame.draw.rect(image, color if self.lit else const.TRANS, rect)

        self.connect(image, lit_color, dark_color)

        symbol_image = pygame.image.load(f"resource/symbol/{self.symbol}.png").convert_alpha()
        symbol_image = pygame.transform.scale(symbol_image, (size, size))
        if self.hidden:
            transparent(symbol_image, 127 if context.is_editing else 0)
        if self.color and self.symbol not in const.FLOWER:
            fill(symbol_image, self.color)
        image.blit(symbol_image, (0, 0))

        self.image.blit(image, (0, 0))
        self.legacy_image = self.image.copy()

    def connect(self, image, lit_color=const.LIT, dark_color=const.GRAY):
        size = context.tile_size
        width = context.line_width
        rect1, rect2, rect3 = [], [], []
        if self.connected[0]:
            rect1.append((0, width, width, size - 2 * width))
            rect2.append((0, width * 2, 2 * width, size - 4 * width))
            rect3.append((0, width * 3, 3 * width, size - 6 * width))
        if self.connected[1]:
            rect1.append((size - width, width, width, size - 2 * width))
            rect2.append((size - 2 * width, width * 2, 2 * width, size - 4 * width))
            rect3.append((size - 3 * width, width * 3, 3 * width, size - 6 * width))
        if self.connected[2]:
            rect1.append((width, 0, size - 2 * width, width))
            rect2.append((width * 2, 0, size - 4 * width, 2 * width))
            rect3.append((width * 3, 0, size - 6 * width, 3 * width))
        if self.connected[3]:
            rect1.append((width, size - width, size - 2 * width, width))
            rect2.append((width * 2, size - 2 * width, size - 4 * width, 2 * width))
            rect3.append((width * 3, size - 3 * width, size - 6 * width, 3 * width))

        for rect in rect1:
            pygame.draw.rect(image, lit_color if self.lit else dark_color, rect)
        for rect in rect2:
            pygame.draw.rect(image, const.TRANS, rect)
        for rect in rect3:
            pygame.draw.rect(image, lit_color if self.lit else const.TRANS, rect)

    def corner(self, tiles, lit_color=const.LIT):
        size, width = context.tile_size, 3 * context.line_width
        self.image = self.legacy_image.copy()
        rects = []
        if self.connected[0] and tiles[0].connected[2] and self.connected[2] and tiles[2].connected[0]:
            rects.append((0, 0, width, width))
        if self.connected[0] and tiles[0].connected[3] and self.connected[3] and tiles[3].connected[0]:
            rects.append((0, size - width, width, width))
        if self.connected[1] and tiles[1].connected[2] and self.connected[2] and tiles[2].connected[1]:
            rects.append((size - width, 0, width, width))
        if self.connected[1] and tiles[1].connected[3] and self.connected[3] and tiles[3].connected[1]:
            rects.append((size - width, size - width, width, width))
        for rect in rects:
            pygame.draw.rect(self.image, lit_color if self.lit else const.TRANS, rect)

    def locate(self, centerx, centery):
        self.rect.centerx = centerx
        self.rect.centery = centery
