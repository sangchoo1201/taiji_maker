import src.const as const
from src.settings import context
from src.tile import Tile


class Drawer:
    def __init__(self, screen):
        self.screen = screen
        self.width = 0
        self.height = 0
        self.grid = []
        self.lit_color = const.LIT
        self.dark_color = const.GRAY

    def set_grid(self, grid):
        self.grid = grid.copy()
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        return self

    def resize(self, dx, dy):
        self.width += dx
        self.height += dy
        self.width = max(self.width, 1)
        self.height = max(self.height, 1)
        self.grid = [[Tile() for _ in range(self.width)] for _ in range(self.height)]
        return self

    def draw(self):
        for i, row in enumerate(self.grid):
            for j, sprite in enumerate(row):
                self.draw_tile(j, i, sprite)

    def draw_tile(self, x, y, sprite):
        size = context.tile_size
        x_pos = int(context.screen_width // 2 + (x - (self.width - 1) / 2) * size)
        y_pos = int(context.screen_height // 2 + (y - (self.height - 1) / 2) * size)
        sprite.locate(x_pos, y_pos)
        self.screen.blit(sprite.image, sprite.rect)

    def convert_coordinates(self, x, y):
        size = context.tile_size
        left = int(context.screen_width // 2 - self.width / 2 * size)
        bottom = int(context.screen_height // 2 - self.height / 2 * size)
        return (x - left) // size, (y - bottom) // size
